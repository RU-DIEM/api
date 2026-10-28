from typing import TYPE_CHECKING, Final

from django_filters import (
    DateTimeFromToRangeFilter,
    OrderingFilter,
    UUIDFilter,
)

from api_core.filters import LoweredSearchFilter
from api_core.filtersets import ApiFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

PROFILE_SEARCH: Final[Sequence[str]] = (
    "user__user__email",
    "user__user__first_name",
    "user__user__last_name",
)

########################################################################################


class RudiProfileFilterSet(ApiFilterSet):
    user = UUIDFilter(field_name="user__id")

    verificado_at = DateTimeFromToRangeFilter()

    search = LoweredSearchFilter(*PROFILE_SEARCH)

    order = OrderingFilter(fields=("created_at", "verificado_at"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        pass
