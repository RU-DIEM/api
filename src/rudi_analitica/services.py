from decimal import Decimal
from typing import TYPE_CHECKING, Final

from django.db.models import Count, Q, Sum
from django.db.transaction import atomic

from rudi_analitica.enums import IndicadorUnidadTypes
from rudi_analitica.models import IndicadorPeriodo
from rudi_constancias.models import Constancia
from rudi_participacion.models import Inscripcion, Participacion
from rudi_puntos.enums import MovimientoOrigenTypes
from rudi_puntos.models import MovimientoPunto

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from api_auth.models import ApiUser

########################################################################################

# a participation counts once validated, not annulled, in an `efectiva` state (RN-13)
EFECTIVA: Final[Q] = Q(
    anulada_at__isnull=True,
    estado__efectiva=True,
    validada_at__isnull=False,
)

METODO_UNICOS: Final[str] = (
    "Personas distintas con al menos una participación validada, no anulada, "
    "en un estado efectivo, con año de reporte igual al del cierre."
)

########################################################################################


@atomic
def cerrar_periodo(*, anio: int, cerrado_por: ApiUser | None) -> list[IndicadorPeriodo]:
    """
    Freeze a finished year's figures (RF-A-45, RN-18).

    A year closes once: `unq_indicadorperiodo_corte` refuses a second close,
    and `trg_indicadorperiodo_anio_cerrado` one before the year ends. Later
    corrections never touch these rows; the live figure and the frozen one
    are compared instead.

    Returns:
        The frozen indicators.

    """

    efectivas: QuerySet = Participacion.objects.filter(EFECTIVA, anio=anio)

    filas: list[dict] = [
        {
            "filas_origen": efectivas.count(),
            "indicador": "participantes_unicos",
            "metodo": METODO_UNICOS,
            "valor": efectivas.values("user").distinct().count(),
        },
        {
            "filas_origen": efectivas.count(),
            "indicador": "participaciones_validadas",
            "metodo": "Participaciones efectivas del año.",
            "unidad": IndicadorUnidadTypes.REGISTROS,
            "valor": efectivas.count(),
        },
        {
            "indicador": "inscripciones",
            "metodo": "Inscripciones a actividades del año, en cualquier estado.",
            "unidad": IndicadorUnidadTypes.REGISTROS,
            "valor": Inscripcion.objects.filter(actividad__anio=anio).count(),
        },
        {
            "indicador": "constancias",
            "metodo": "Constancias emitidas en el año y no anuladas.",
            "unidad": IndicadorUnidadTypes.REGISTROS,
            "valor": Constancia.objects.filter(
                anulada_at__isnull=True,
                emitida_at__year=anio,
            ).count(),
        },
        {
            "indicador": "puntos_otorgados",
            "metodo": "Suma de movimientos vivos del año, sin reversos.",
            "unidad": IndicadorUnidadTypes.PUNTOS,
            "valor": max(
                MovimientoPunto.objects
                .filter(anio=anio, revertido_at__isnull=True)
                .exclude(origen=MovimientoOrigenTypes.REVERSO)
                .aggregate(total=Sum("puntos"))["total"]
                or 0,
                0,
            ),
        },
        *(
            {
                "dimension": "tipo_actividad",
                "dimension_valor": corte["actividad__tipo_actividad__etiqueta"],
                "filas_origen": corte["filas"],
                "indicador": "participantes_unicos",
                "metodo": METODO_UNICOS,
                "valor": corte["personas"],
            }
            for corte in efectivas
            .values("actividad__tipo_actividad__etiqueta")
            .annotate(filas=Count("pk"), personas=Count("user", distinct=True))
            .order_by("actividad__tipo_actividad__etiqueta")
        ),
    ]

    return [
        IndicadorPeriodo.objects.create(
            anio=anio,
            cerrado_por=cerrado_por,
            **(fila | {"valor": Decimal(fila["valor"])}),
        )
        for fila in filas
    ]
