from typing import TYPE_CHECKING

from django.contrib.auth.models import Group
from django_filters import FilterSet, OrderingFilter

from api_core.filters import IntFilter, LoweredFilter, LoweredSearchFilter

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class GroupFilterSet(FilterSet):
    id = IntFilter()

    name = LoweredFilter()

    search = LoweredSearchFilter("name")

    order = OrderingFilter(fields=("name",))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = Group
