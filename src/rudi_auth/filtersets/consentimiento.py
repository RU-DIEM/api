from typing import TYPE_CHECKING

from django_filters import (
    DateTimeFromToRangeFilter,
    FilterSet,
    OrderingFilter,
    UUIDFilter,
)

from api_core.filters import LoweredFilter, TypedLoweredFilter
from rudi_auth.enums import ConsentimientoCanalTypes
from rudi_auth.models import ConsentimientoDatos

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class ConsentimientoDatosFilterSet(FilterSet):
    id = UUIDFilter()

    user = UUIDFilter(field_name="user__id")

    estado = LoweredFilter(field_name="estado__codigo")

    canal = TypedLoweredFilter(enum=ConsentimientoCanalTypes)

    otorgado_at = DateTimeFromToRangeFilter()
    retirado_at = DateTimeFromToRangeFilter()

    order = OrderingFilter(fields=("created_at", "otorgado_at", "retirado_at"))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = ConsentimientoDatos
