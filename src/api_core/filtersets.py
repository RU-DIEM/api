from typing import TYPE_CHECKING

from django_filters import FilterSet

from typing_extensions import disjoint_base

if TYPE_CHECKING:
    from collections.abc import Sequence


########################################################################################


@disjoint_base
class ApiFilterSet(FilterSet):
    """
    Base filterset for `ApiModel` tables: always filterable by `id`.
    """

    class Meta:
        fields: Sequence[str] = ("id",)


@disjoint_base
class ApiSoftDeleteFilterSet(FilterSet):
    """
    Base filterset for `ApiSoftDeleteModel` tables: filterable by `id` and `is_active`.
    """

    class Meta:
        fields: Sequence[str] = ("id", "is_active")
