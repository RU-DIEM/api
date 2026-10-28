from datetime import timedelta

import pytest

from django.utils.timezone import now

from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import TipoMentor
from rudi_estados.enums import ActorTypes, InputSourceTypes
from rudi_estados.services.actor import set_actor
from rudi_participacion.models import (
    AsignacionMentor,
    Equipo,
    EquipoMiembro,
    Inscripcion,
    Participacion,
)
from rudi_profiles.models import MentorProfile

from .conftest import Mundo, rejected

pytestmark = pytest.mark.django_db

########################################################################################


def inscritos(actividad: Actividad) -> int:
    return Actividad.objects.values_list("inscritos_activos", flat=True).get(
        pk=actividad.pk,
    )


def en_estado(inscripcion: Inscripcion, estado: object) -> bool:
    return Inscripcion.objects.filter(pk=inscripcion.pk, estado=estado).exists()


def cerrar(mundo: Mundo, inscripcion: Inscripcion) -> None:
    Inscripcion.objects.filter(pk=inscripcion.pk).update(
        cerrada_at=now(),
        estado=mundo.estados.inscripcion_cerrada,
        motivo=mundo.motivo(MotivoAmbitoTypes.CANCEL_INSCRIPCION),
    )


########################################################################################
# inscripción: cupo, contador y lista de espera


def test_contador_y_cupo(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(cupo=1)

    mundo.inscripcion(actividad, mundo.persona("ana"))

    assert inscritos(actividad) == 1

    with rejected("chk_actividad_cupo_coherente"):
        mundo.inscripcion(actividad, mundo.persona("beto"))

    mundo.inscripcion(actividad, mundo.persona("caro"), is_excepcion_cupo=True)

    assert inscritos(actividad) == 1


def test_reducir_cupo_bajo_los_inscritos(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(cupo=2)

    mundo.inscripcion(actividad, mundo.persona("ana"))
    mundo.inscripcion(actividad, mundo.persona("beto"))

    with rejected("chk_actividad_cupo_coherente"):
        Actividad.objects.filter(pk=actividad.pk).update(cupo=1)


def test_cerrar_libera_y_promueve(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(cupo=1)

    primera: Inscripcion = mundo.inscripcion(actividad, mundo.persona("ana"))
    espera: Inscripcion = mundo.inscripcion(
        actividad,
        mundo.persona("beto"),
        estado=mundo.estados.en_espera,
        posicion_espera=1,
    )

    set_actor(ActorTypes.USER)
    cerrar(mundo, primera)

    assert en_estado(espera, mundo.estados.confirmada)
    assert Inscripcion.objects.filter(pk=espera.pk, posicion_espera=None).exists()
    assert inscritos(actividad) == 1


def test_ampliar_cupo_promueve(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(cupo=1)

    mundo.inscripcion(actividad, mundo.persona("ana"))
    espera: Inscripcion = mundo.inscripcion(
        actividad,
        mundo.persona("beto"),
        estado=mundo.estados.en_espera,
        posicion_espera=1,
    )

    Actividad.objects.filter(pk=actividad.pk).update(cupo=2)

    assert en_estado(espera, mundo.estados.confirmada)
    assert inscritos(actividad) == 2


def test_estado_coherente_de_inscripcion(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()

    with rejected("Una inscripción en lista de espera no ocupa cupo."):
        mundo.inscripcion(actividad, mundo.persona("ana"), posicion_espera=1)

    with rejected("si y solo si su estado es terminal"):
        mundo.inscripcion(
            actividad,
            mundo.persona("beto"),
            estado=mundo.estados.inscripcion_cerrada,
        )


def test_ventana_cerrada(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(
        inscripcion_abre_at=now() - timedelta(days=2),
        inscripcion_cierra_at=now() - timedelta(days=1),
    )

    with rejected("no admite inscripciones en este momento"):
        mundo.inscripcion(actividad, mundo.persona("ana"))

    # an administrative inscription ignores the window
    mundo.inscripcion(
        actividad,
        mundo.persona("beto"),
        creada_por=mundo.admin,
        origen=InputSourceTypes.MODERN,
    )


def test_cancelar_actividad_cierra_inscripciones(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()
    viva: Inscripcion = mundo.inscripcion(actividad, mundo.persona("ana"))

    set_actor(ActorTypes.ADMIN)
    Actividad.objects.filter(pk=actividad.pk).update(
        cancelada_at=now(),
        estado=mundo.estados.cancelada,
        motivo=mundo.motivo(MotivoAmbitoTypes.CANCEL_ACTIVIDAD),
    )

    assert en_estado(viva, mundo.estados.inscripcion_cerrada)
    assert Inscripcion.objects.filter(pk=viva.pk, cerrada_at__isnull=False).exists()
    assert inscritos(actividad) == 0


def test_no_se_cierra_lo_validado(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()
    persona: RudiUser = mundo.persona("ana")
    inscripcion: Inscripcion = mundo.inscripcion(actividad, persona)

    mundo.validar(mundo.participacion(actividad, persona, inscripcion=inscripcion))

    with rejected("con una participación validada"):
        cerrar(mundo, inscripcion)


########################################################################################
# participación


def test_anio_se_copia_y_se_congela(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(anio=2025)
    participacion: Participacion = mundo.participacion(
        actividad,
        mundo.persona("ana"),
        anio=2030,
    )

    assert Participacion.objects.filter(pk=participacion.pk, anio=2025).exists()

    with rejected():
        Participacion.objects.filter(pk=participacion.pk).update(anio=2026)


def test_participacion_coherente(mundo: Mundo) -> None:
    una: Actividad = mundo.actividad(admite_equipos=True)
    otra: Actividad = mundo.actividad()
    persona: RudiUser = mundo.persona("ana")

    ajena: Inscripcion = mundo.inscripcion(otra, persona)

    with rejected("La inscripción es de otra persona o de otra actividad."):
        mundo.participacion(una, persona, inscripcion=ajena)

    equipo: Equipo = Equipo.objects.create(
        actividad=una,
        codigo_union="ABC123",
        nombre="Equipo",
    )

    with rejected("El equipo es de otra actividad."):
        mundo.participacion(otra, persona, equipo=equipo)


def test_efectiva_exige_validacion_y_actividad_validable(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()

    with rejected("Un estado efectivo exige una participación validada."):
        mundo.participacion(
            actividad,
            mundo.persona("ana"),
            estado=mundo.estados.validada,
        )

    borrador: Actividad = mundo.actividad(publicar=False)

    with rejected("no admite validar participaciones"):
        mundo.validar(mundo.participacion(borrador, mundo.persona("beto")))


########################################################################################
# equipos


def test_reglas_de_equipo(mundo: Mundo) -> None:
    with rejected("La actividad no admite equipos."):
        Equipo.objects.create(
            actividad=mundo.actividad(),
            codigo_union="NOPE01",
            nombre="Nope",
        )

    actividad: Actividad = mundo.actividad(admite_equipos=True, equipo_max=1)
    rojo: Equipo = Equipo.objects.create(
        actividad=actividad,
        codigo_union="ROJO01",
        nombre="Rojo",
    )
    azul: Equipo = Equipo.objects.create(
        actividad=actividad,
        codigo_union="AZUL01",
        nombre="Azul",
    )

    ana: RudiUser = mundo.persona("ana")

    EquipoMiembro.objects.create(equipo=rojo, user=ana)

    with rejected("ya pertenece a otro equipo de esta actividad"):
        EquipoMiembro.objects.create(equipo=azul, user=ana)

    with rejected("ya tiene el máximo de miembros"):
        EquipoMiembro.objects.create(equipo=rojo, user=mundo.persona("beto"))

    Equipo.objects.filter(pk=azul.pk).update(congelado_at=now())

    with rejected("La composición del equipo está congelada."):
        EquipoMiembro.objects.create(equipo=azul, user=mundo.persona("caro"))

    set_actor(ActorTypes.ADMIN)
    EquipoMiembro.objects.create(equipo=azul, user=mundo.persona("dani"))


########################################################################################
# asignación de mentores


def test_asignacion_de_mentor(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()
    mentor: MentorProfile = MentorProfile.objects.create(
        tipo_mentor=TipoMentor.objects.create(codigo="uam", etiqueta="UAM"),
        user=mundo.persona("mentora"),
    )
    propuesta: dict = {
        "actividad": actividad,
        "estado": mundo.estados.mentoria_propuesta,
        "mentor": mentor,
        "tipo_acompanamiento": "charla",
    }

    with rejected("todavía no ha sido confirmado"):
        AsignacionMentor.objects.create(**propuesta)

    MentorProfile.objects.filter(pk=mentor.pk).update(
        confirmado_at=now(),
        confirmado_por=mundo.admin,
    )

    asignacion: AsignacionMentor = AsignacionMentor.objects.create(**propuesta)
    pendiente = AsignacionMentor.objects.filter(pk=asignacion.pk)

    assert pendiente.filter(respondida_at=None).exists()

    with rejected("Este estado exige un motivo."):
        pendiente.update(estado=mundo.estados.mentoria_declinada)

    pendiente.update(
        estado=mundo.estados.mentoria_declinada,
        motivo=mundo.motivo(MotivoAmbitoTypes.REJECT_MENTORIA),
    )

    assert pendiente.filter(
        finalizada_at__isnull=False,
        respondida_at__isnull=False,
    ).exists()

    equipo: Equipo = Equipo.objects.create(
        actividad=mundo.actividad(admite_equipos=True),
        codigo_union="MENT01",
        nombre="Mentoreado",
    )

    with rejected("El equipo es de otra actividad."):
        AsignacionMentor.objects.create(
            **propuesta | {"equipo": equipo, "tipo_acompanamiento": "jurado"},
        )
