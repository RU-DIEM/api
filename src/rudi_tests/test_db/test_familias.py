import pytest

from django.utils.timezone import now

from rudi_actividades.models import Actividad, Programa
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo, TipoActividad
from rudi_estados.enums import ActorTypes
from rudi_estados.models import EstadoActividad
from rudi_estados.services.actor import set_actor
from rudi_estados.services.catalogo import resolve_estado_id
from rudi_estados.services.transicion import exige_motivo, transiciones_validas

from .conftest import Mundo, rejected

pytestmark = pytest.mark.django_db

########################################################################################
# ciclo de vida del estado


def test_estado_desactivado_no_se_asigna(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(publicar=False)

    EstadoActividad.objects.filter(pk=mundo.estados.publicada.pk).update(
        is_active=False,
    )

    with rejected("El estado está desactivado."):
        Actividad.objects.filter(pk=actividad.pk).update(
            estado=mundo.estados.publicada,
        )


def test_estado_desactivado_no_bloquea_las_filas_que_ya_lo_tienen(
    mundo: Mundo,
) -> None:
    actividad: Actividad = mundo.actividad()

    EstadoActividad.objects.filter(pk=mundo.estados.publicada.pk).update(
        is_active=False,
    )

    Actividad.objects.filter(pk=actividad.pk).update(nombre="Renombrada")


def test_estado_terminal_no_cambia(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()

    Actividad.objects.filter(pk=actividad.pk).update(
        cancelada_at=now(),
        estado=mundo.estados.cancelada,
        motivo=mundo.motivo(MotivoAmbitoTypes.CANCEL_ACTIVIDAD),
    )

    with rejected("El estado es terminal"):
        Actividad.objects.filter(pk=actividad.pk).update(
            estado=mundo.estados.publicada,
        )


def test_transicion_no_declarada(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()

    with rejected("La transición no está declarada"):
        Actividad.objects.filter(pk=actividad.pk).update(
            estado=mundo.estados.borrador,
        )


def test_transicion_exige_el_actor_declarado(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(publicar=False)

    set_actor(ActorTypes.USER)

    with rejected("para este actor"):
        Actividad.objects.filter(pk=actividad.pk).update(
            estado=mundo.estados.publicada,
        )

    set_actor(ActorTypes.ADMIN)

    Actividad.objects.filter(pk=actividad.pk).update(estado=mundo.estados.publicada)


def test_publicar_exige_responsable(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(publicar=False, sin_responsable=True)

    with rejected("sin al menos un responsable"):
        Actividad.objects.filter(pk=actividad.pk).update(
            estado=mundo.estados.publicada,
        )


def test_publicar_fija_publicada_at(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()

    assert Actividad.objects.filter(
        pk=actividad.pk,
        publicada_at__isnull=False,
    ).exists()


def test_servicios_de_estado(mundo: Mundo) -> None:
    estados = mundo.estados

    assert resolve_estado_id("actividad", "publicada") == estados.publicada.pk

    validas = transiciones_validas(
        actor=ActorTypes.ADMIN,
        entidad="actividad",
        from_id=estados.borrador.pk,
    )

    assert list(validas.values_list("to_estado", flat=True)) == [estados.publicada.pk]

    assert not exige_motivo(
        actor=ActorTypes.ADMIN,
        entidad="actividad",
        from_id=estados.borrador.pk,
        to_id=estados.publicada.pk,
    )
    assert exige_motivo(
        actor="sistema",
        entidad="asignacion_mentor",
        from_id=estados.mentoria_propuesta.pk,
        to_id=estados.mentoria_declinada.pk,
    )
    assert not exige_motivo(
        actor="sistema",
        entidad="actividad",
        from_id=estados.borrador.pk,
        to_id=estados.cancelada.pk,
    )


########################################################################################
# motivo de lista cerrada


def test_motivo_de_otro_ambito(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()

    with rejected("no pertenece al ámbito"):
        Actividad.objects.filter(pk=actividad.pk).update(
            motivo=mundo.motivo(MotivoAmbitoTypes.NULL_CONSTANCIA),
        )


def test_motivo_desactivado_y_descripcion(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()
    exigente: Motivo = mundo.motivo(
        MotivoAmbitoTypes.CANCEL_ACTIVIDAD,
        require_descripcion=True,
    )

    with rejected("exige una descripción"):
        Actividad.objects.filter(pk=actividad.pk).update(motivo=exigente)

    Motivo.objects.filter(pk=exigente.pk).update(is_active=False)

    with rejected("El motivo está desactivado."):
        Actividad.objects.filter(pk=actividad.pk).update(
            motivo=exigente,
            motivo_descripcion="Lluvia.",
        )


########################################################################################
# catálogo activo


def test_catalogo_desactivado_no_se_estrena(mundo: Mundo) -> None:
    TipoActividad.objects.filter(pk=mundo.tipo.pk).update(is_active=False)

    with rejected("La entrada de catálogo está desactivada."):
        Programa.objects.create(
            codigo="rally",
            nombre="Rally",
            tipo_actividad=mundo.tipo,
        )

    with rejected("La entrada de catálogo está desactivada."):
        mundo.actividad(publicar=False, sin_responsable=True)
