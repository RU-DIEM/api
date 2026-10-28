from decimal import Decimal

import pytest

from django.db import connection
from django.utils.timezone import now

from rudi_actividades.models import Actividad
from rudi_analitica.models import (
    IndicadorPeriodo,
    MvParticipacionActividad,
    MvParticipanteUnicoAnio,
)
from rudi_catalogos.enums import TRL, AmbitosAplicacion, NivelesFormalizacion
from rudi_portafolio.enums import PropuestaActividadRolTypes
from rudi_portafolio.models import Propuesta, PropuestaActividad

from .conftest import Mundo, rejected

pytestmark = pytest.mark.django_db

########################################################################################


def make_propuesta(mundo: Mundo, nombre: str, **fields: object) -> Propuesta:
    fields = {
        "ambito_aplicacion": AmbitosAplicacion.ACADEMIA,
        "anio_ingreso": 2026,
        "estado": mundo.estados.propuesta_activa,
        "nivel_formalizacion": NivelesFormalizacion.IDEA,
        **fields,
    }

    return Propuesta.objects.create(nombre=nombre, **fields)


def clasificada(propuesta: Propuesta) -> bool:
    return Propuesta.objects.filter(
        clasificada_at__isnull=False,
        pk=propuesta.pk,
    ).exists()


########################################################################################
# portafolio


def test_codigo_correlativo_por_anio(mundo: Mundo) -> None:
    primera: Propuesta = make_propuesta(mundo, "Primera")
    segunda: Propuesta = make_propuesta(mundo, "Segunda")
    otra: Propuesta = make_propuesta(mundo, "Otra", anio_ingreso=2025)

    assert primera.codigo == "UAM-INN-2026-001"
    assert segunda.codigo == "UAM-INN-2026-002"
    assert otra.codigo == "UAM-INN-2025-001"

    with rejected():
        Propuesta.objects.filter(pk=primera.pk).update(anio_ingreso=2024)


def test_clasificada_marca(mundo: Mundo) -> None:
    propuesta: Propuesta = make_propuesta(mundo, "Propuesta")

    assert not clasificada(propuesta)

    Propuesta.objects.filter(pk=propuesta.pk).update(
        etapa_desarrollo="incubacion",
        mrl="mrl_3",
        ods_principal="ods_4",
        sector_aplicacion="cuaen_p",
        tipo_innovacion="servicio",
        trl="trl_4",
        vertical="edtech",
    )

    assert clasificada(propuesta)

    Propuesta.objects.filter(pk=propuesta.pk).update(trl=TRL.P_D)

    assert not clasificada(propuesta)


def test_actividad_de_origen_abre_la_trayectoria(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad()
    propuesta: Propuesta = make_propuesta(
        mundo,
        "Propuesta",
        actividad_origen=actividad,
    )

    assert PropuestaActividad.objects.filter(
        actividad=actividad,
        propuesta=propuesta,
        rol=PropuestaActividadRolTypes.ORIGINA,
    ).exists()


def test_cierre_coherente(mundo: Mundo) -> None:
    propuesta: Propuesta = make_propuesta(mundo, "Propuesta")

    with rejected("si y solo si su estado es terminal"):
        Propuesta.objects.filter(pk=propuesta.pk).update(
            estado=mundo.estados.propuesta_cerrada,
        )


########################################################################################
# analítica


def test_anio_sin_terminar_no_se_cierra(db: None) -> None:
    with rejected("Solo se cierra un año que ya terminó."):
        IndicadorPeriodo.objects.create(
            anio=now().year,
            indicador="participantes_unicos",
            valor=Decimal(10),
        )

    IndicadorPeriodo.objects.create(
        anio=now().year - 1,
        indicador="participantes_unicos",
        valor=Decimal(10),
    )


def test_vistas_materializadas(mundo: Mundo) -> None:
    actividad: Actividad = mundo.actividad(anio=2025)

    mundo.validar(mundo.participacion(actividad, mundo.persona("ana")))
    mundo.participacion(actividad, mundo.persona("beto"))

    with connection.cursor() as cursor:
        for vista in (
            "mv_participante_unico_anio",
            "mv_participacion_actividad",
            "mv_saldo_puntos_user",
            "mv_cobertura_carrera",
        ):
            cursor.execute(f"REFRESH MATERIALIZED VIEW {vista}")

    assert MvParticipanteUnicoAnio.objects.get(anio=2025).valor == 1

    resumen: MvParticipacionActividad = MvParticipacionActividad.objects.get(
        actividad=actividad,
    )

    assert (resumen.participaciones, resumen.validadas) == (2, 1)
    assert str(resumen) == f"MvParticipacionActividad(actividad_id={actividad.pk})"
