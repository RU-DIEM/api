from typing import TYPE_CHECKING

from django_filters import OrderingFilter

from api_auth.enums import ApiUserTypes
from api_auth.models import ApiUser
from api_core.filters import (
    IntFilter,
    LoweredFilter,
    LoweredSearchFilter,
    TypedChoiceFilter,
)
from api_core.filtersets import ApiSoftDeleteFilterSet

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class ApiUserFilterSet(ApiSoftDeleteFilterSet):
    first_name = LoweredFilter()
    last_name = LoweredFilter()
    email = LoweredFilter()
    username = LoweredFilter()

    group_id = IntFilter(field_name="groups__id")
    permission_id = IntFilter(field_name="permissions__id")

    group = TypedChoiceFilter(enum=ApiUserTypes, field_name="groups__name")

    search = LoweredSearchFilter("username", "email", "first_name", "last_name")

    order = OrderingFilter(fields=("username", "email", "created_at"))

    class Meta(ApiSoftDeleteFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = ApiUser
