from typing import TYPE_CHECKING, Final

from django_filters import (
    FilterSet,
    OrderingFilter,
    UUIDFilter,
)

from api_core.filters import LoweredSearchFilter
from rudi_core.filters import PgDateTimeFromToRangeFilter

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

PROFILE_SEARCH: Final[Sequence[str]] = (
    "user__user__email",
    "user__user__first_name",
    "user__user__last_name",
)

########################################################################################


class RudiProfileFilterSet(FilterSet):
    id = UUIDFilter()

    user = UUIDFilter(field_name="user__id")

    verificado_at = PgDateTimeFromToRangeFilter()

    search = LoweredSearchFilter(*PROFILE_SEARCH)

    order = OrderingFilter(fields=("created_at", "verificado_at"))

    class Meta:
        fields: Sequence[str] = ()
