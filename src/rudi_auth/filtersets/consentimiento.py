from typing import TYPE_CHECKING

from django_filters import (
    DateTimeFromToRangeFilter,
    OrderingFilter,
    UUIDFilter,
)

from api_core.filters import LoweredFilter, TypedLoweredFilter
from api_core.filtersets import ApiFilterSet
from rudi_auth.enums import ConsentimientoCanalTypes
from rudi_auth.models import ConsentimientoDatos

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class ConsentimientoDatosFilterSet(ApiFilterSet):
    user = UUIDFilter(field_name="user__id")

    estado = LoweredFilter(field_name="estado__codigo")

    canal = TypedLoweredFilter(enum=ConsentimientoCanalTypes)

    otorgado_at = DateTimeFromToRangeFilter()
    retirado_at = DateTimeFromToRangeFilter()

    order = OrderingFilter(fields=("created_at", "otorgado_at", "retirado_at"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = ConsentimientoDatos
