from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter
from api_core.filtersets import ApiFilterSet
from rudi_auth.models import IdentificadorUser

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet

########################################################################################


class IdentificadorUserFilterSet(ApiFilterSet):
    tipo = LoweredFilter(field_name="tipo__codigo")

    is_main = BooleanFilter()

    verificado = BooleanFilter(method="filter_verificado")

    search = LoweredSearchFilter("valor_normalizado")

    order = OrderingFilter(fields=("created_at", "verificado_at"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = IdentificadorUser

    def filter_verificado(  # ruff: ignore[no-self-use]
        self,
        qs: QuerySet,
        name: str,  # ruff: ignore[unused-method-argument]
        value: bool | None,  # ruff: ignore[boolean-type-hint-positional-argument]
    ) -> QuerySet:
        if value is None:
            return qs

        return qs.filter(verificado_at__isnull=(not value))
