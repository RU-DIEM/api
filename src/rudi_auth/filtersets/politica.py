from typing import TYPE_CHECKING

from django_filters import (
    BooleanFilter,
    DateFromToRangeFilter,
    FilterSet,
    OrderingFilter,
    UUIDFilter,
)

from api_core.filters import LoweredFilter, LoweredSearchFilter
from rudi_auth.models import PoliticaPrivacidad

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model, QuerySet

########################################################################################


class PoliticaPrivacidadFilterSet(FilterSet):
    id = UUIDFilter()

    version = LoweredFilter()
    titulo = LoweredFilter()

    vigente = BooleanFilter(method="filter_vigente")

    vigente_desde = DateFromToRangeFilter()

    search = LoweredSearchFilter("texto", "titulo", "version")

    order = OrderingFilter(fields=("created_at", "vigente_desde"))

    class Meta:
        fields: Sequence[str] = ()
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
