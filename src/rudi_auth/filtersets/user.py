from typing import TYPE_CHECKING

from django_filters import (
    BooleanFilter,
    DateFromToRangeFilter,
    FilterSet,
    OrderingFilter,
    UUIDFilter,
)

from api_core.filters import LoweredFilter, LoweredSearchFilter, TypedLoweredFilter
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import Etnias, Generos
from rudi_estados.enums import InputSourceTypes

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class RudiUserFilterSet(FilterSet):
    id = UUIDFilter()

    estado = LoweredFilter(field_name="estado__codigo")

    origen = TypedLoweredFilter(enum=InputSourceTypes)

    genero = TypedLoweredFilter(enum=Generos)
    etnia = TypedLoweredFilter(enum=Etnias)

    is_active = BooleanFilter(field_name="user__is_active")

    fecha_nacimiento = DateFromToRangeFilter()

    search = LoweredSearchFilter(
        "user__email",
        "user__first_name",
        "user__last_name",
        "user__username",
    )

    order = OrderingFilter(
        fields=("created_at", "user__first_name", "user__last_name"),
    )

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = RudiUser
