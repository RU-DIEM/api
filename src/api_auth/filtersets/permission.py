from typing import TYPE_CHECKING

from django.contrib.auth.models import Permission
from django_filters import FilterSet, OrderingFilter

from api_auth.enums import PermissionTypes
from api_core.filters import (
    IntFilter,
    LoweredFilter,
    LoweredSearchFilter,
    TypedLoweredFilter,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class PermissionFilterSet(FilterSet):
    id = IntFilter()

    action = TypedLoweredFilter(
        enum=PermissionTypes,
        field_name="codename",
    )

    model = LoweredFilter(field_name="content_type__model")

    search = LoweredSearchFilter("codename", "content_type__model")

    order = OrderingFilter(fields=("codename",))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = Permission
