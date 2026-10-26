from typing import TYPE_CHECKING

from django_filters import OrderingFilter, UUIDFilter

from api_core.filters import TypedChoiceFilter
from api_core.filtersets import ApiFilterSet
from api_media.enums import MediaVisibility
from api_media.models import ApiMedia

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class ApiMediaFilterSet(ApiFilterSet):
    visibility = TypedChoiceFilter(enum=MediaVisibility)

    uploaded_by_id = UUIDFilter(field_name="uploaded_by__id")

    order = OrderingFilter(fields=("created_at", "size"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = ApiMedia
