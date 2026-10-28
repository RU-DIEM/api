from datetime import date

import pytest

from django.db.backends.postgresql.psycopg_any import DateRange
from django.utils.timezone import now

from rudi_auth.models import RudiUser
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo
from rudi_constancias.models import (
    Constancia,
    ConstanciaParticipacion,
    PlantillaConstancia,
)
from rudi_participacion.models import Participacion
from rudi_puntos.enums import MovimientoOrigenTypes
from rudi_puntos.models import MovimientoPunto, ReglaPuntuacion

from .conftest import Mundo, rejected

pytestmark = pytest.mark.django_db

VIGENCIA: DateRange = DateRange(date(2000, 1, 1), None)

########################################################################################


def saldo(persona: RudiUser) -> int:
    return sum(
        MovimientoPunto.objects
        .filter(user=persona, revertido_at__isnull=True)
        .exclude(origen=MovimientoOrigenTypes.REVERSO)
        .values_list("puntos", flat=True)
    )


def emitir(
    mundo: Mundo, persona: RudiUser, codigo: str, **fields: object
) -> Constancia:
    plantilla: PlantillaConstancia = (
        PlantillaConstancia.objects.first()
        or PlantillaConstancia.objects.create(
            codigo="participacion",
            cuerpo="Constancia para {nombre}.",
            etiqueta="Participación",
            vigente_desde=date(2026, 1, 1),
        )
    )

    fields = {
        "codigo_verificacion": codigo,
        "contenido_congelado": {"actividades": []},
        "emitida_por": mundo.admin,
        "estado": mundo.estados.emitida,
        "nombre_congelado": "Ana",
        "plantilla": plantilla,
        "texto_congelado": "Constancia para Ana.",
        **fields,
    }

    return Constancia.objects.create(user=persona, **fields)


########################################################################################
# puntos


def test_validar_otorga_la_regla_mas_especifica(mundo: Mundo) -> None:
    ReglaPuntuacion.objects.create(
        codigo="general",
        etiqueta="General",
        puntos=5,
        tipo_actividad=mundo.tipo,
        vigencia=VIGENCIA,
    )
    ReglaPuntuacion.objects.create(
        codigo="por_rol",
        etiqueta="Por rol",
        puntos=8,
        rol=mundo.rol,
        tipo_actividad=mundo.tipo,
        vigencia=VIGENCIA,
    )

    persona: RudiUser = mundo.persona("ana")

    mundo.validar(mundo.participacion(mundo.actividad(), persona))

    assert saldo(persona) == 8


def test_puntos_base_prevalece(mundo: Mundo) -> None:
    ReglaPuntuacion.objects.create(
        codigo="general",
        etiqueta="General",
        puntos=5,
        tipo_actividad=mundo.tipo,
        vigencia=VIGENCIA,
    )

    persona: RudiUser = mundo.persona("ana")
    participacion: Participacion = mundo.participacion(
        mundo.actividad(puntos_base=20),
        persona,
    )

    mundo.validar(participacion)

    assert MovimientoPunto.objects.filter(
        anio=participacion.anio,
        puntos=20,
        regla=None,
        user=persona,
    ).exists()


def test_reglas_solapadas(mundo: Mundo) -> None:
    ReglaPuntuacion.objects.create(
        codigo="una",
        etiqueta="Una",
        puntos=5,
        tipo_actividad=mundo.tipo,
        vigencia=VIGENCIA,
    )

    with rejected("excl_reglapuntuacion_vigencia"):
        ReglaPuntuacion.objects.create(
            codigo="otra",
            etiqueta="Otra",
            puntos=7,
            tipo_actividad=mundo.tipo,
            vigencia=DateRange(date(2026, 1, 1), date(2027, 1, 1)),
        )


def test_anular_revierte_e_invalida_constancias(mundo: Mundo) -> None:
    persona: RudiUser = mundo.persona("ana")
    participacion: Participacion = mundo.participacion(
        mundo.actividad(puntos_base=10),
        persona,
    )

    mundo.validar(participacion)

    constancia: Constancia = emitir(mundo, persona, "ABCD1234")

    # assigned by the trigger, whatever the insert sent
    assert Constancia.objects.filter(
        folio__startswith=f"DIEM-{now().year}-",
        pk=constancia.pk,
    ).exists()

    ConstanciaParticipacion.objects.create(
        constancia=constancia,
        orden=1,
        participacion=participacion,
    )

    with rejected("ya se usó"):
        PlantillaConstancia.objects.update(cuerpo="Otro.")

    Participacion.objects.filter(pk=participacion.pk).update(
        anulada_at=now(),
        estado=mundo.estados.anulada,
        motivo=mundo.motivo(MotivoAmbitoTypes.NULL_PARTICIPACION),
    )

    assert saldo(persona) == 0
    assert MovimientoPunto.objects.filter(
        origen=MovimientoOrigenTypes.AUTO,
        revertido_at__isnull=False,
    ).exists()
    assert Constancia.objects.filter(
        anulada_at__isnull=False,
        estado=mundo.estados.constancia_anulada,
        pk=constancia.pk,
    ).exists()


def test_reverso_exacto(mundo: Mundo) -> None:
    ana: RudiUser = mundo.persona("ana")
    ajuste: Motivo = mundo.motivo(MotivoAmbitoTypes.AJUSTE_PUNTOS)

    asiento: MovimientoPunto = MovimientoPunto.objects.create(
        anio=2026,
        motivo=ajuste,
        origen=MovimientoOrigenTypes.MANUAL,
        puntos=10,
        user=ana,
    )
    reverso: dict = {
        "anio": 2026,
        "motivo": ajuste,
        "origen": MovimientoOrigenTypes.REVERSO,
        "revierte": asiento,
    }

    with rejected("Un reverso anula el asiento completo"):
        MovimientoPunto.objects.create(**reverso, puntos=-5, user=ana)

    with rejected("Un reverso es de la misma persona"):
        MovimientoPunto.objects.create(
            **reverso,
            puntos=-10,
            user=mundo.persona("beto"),
        )

    MovimientoPunto.objects.create(**reverso, puntos=-10, user=ana)

    assert MovimientoPunto.objects.filter(
        pk=asiento.pk,
        revertido_at__isnull=False,
    ).exists()

    with rejected():
        MovimientoPunto.objects.filter(pk=asiento.pk).update(puntos=99)


########################################################################################
# constancias


def test_constancia_solo_ampara_participaciones_validadas(mundo: Mundo) -> None:
    persona: RudiUser = mundo.persona("ana")
    pendiente: Participacion = mundo.participacion(mundo.actividad(), persona)
    constancia: Constancia = emitir(mundo, persona, "WXYZ9876")

    with rejected("no está validada"):
        ConstanciaParticipacion.objects.create(
            constancia=constancia,
            orden=1,
            participacion=pendiente,
        )

    with rejected("Solo se reemplaza una constancia anulada."):
        emitir(mundo, persona, "WXYZ9877", reemplaza_a=constancia)

    with rejected():
        Constancia.objects.filter(pk=constancia.pk).update(nombre_congelado="Otra")
