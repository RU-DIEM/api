from typing import TYPE_CHECKING

from django_filters import (
    BooleanFilter,
    DateFromToRangeFilter,
    OrderingFilter,
)

from api_core.filters import LoweredFilter, LoweredSearchFilter
from api_core.filtersets import ApiFilterSet
from rudi_auth.models import PoliticaPrivacidad

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet

########################################################################################


class PoliticaPrivacidadFilterSet(ApiFilterSet):
    version = LoweredFilter()
    titulo = LoweredFilter()

    vigente = BooleanFilter(method="filter_vigente")

    vigente_desde = DateFromToRangeFilter()

    search = LoweredSearchFilter("texto", "titulo", "version")

    order = OrderingFilter(fields=("created_at", "vigente_desde"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = PoliticaPrivacidad

    def filter_vigente(  # ruff: ignore[no-self-use]
        self,
        qs: QuerySet,
        name: str,  # ruff: ignore[unused-method-argument]
        value: bool | None,  # ruff: ignore[boolean-type-hint-positional-argument]
    ) -> QuerySet:
        if value is None:
            return qs

        return qs.filter(vigente_hasta__isnull=value)
