from typing import TYPE_CHECKING

from django_filters import OrderingFilter

from api_core.filters import IntFilter, LoweredFilter, TypedLoweredFilter
from api_core.filtersets import ApiFilterSet
from rudi_analitica.enums import IndicadorUnidadTypes
from rudi_analitica.models import IndicadorPeriodo

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class IndicadorPeriodoFilterSet(ApiFilterSet):
    indicador = LoweredFilter()
    anio = IntFilter()
    dimension = LoweredFilter()

    unidad = TypedLoweredFilter(enum=IndicadorUnidadTypes)

    order = OrderingFilter(fields=("anio", "created_at", "indicador"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = IndicadorPeriodo
