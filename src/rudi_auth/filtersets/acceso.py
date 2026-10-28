from typing import TYPE_CHECKING

from django_filters import OrderingFilter, UUIDFilter

from api_core.filters import TypedLoweredFilter
from api_core.filtersets import ApiFilterSet
from rudi_auth.enums import AccesoDatoTypes
from rudi_auth.models import AccesoDatoPersonal

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class AccesoDatoPersonalFilterSet(ApiFilterSet):
    accedido_por_id = UUIDFilter(field_name="accedido_por__id")

    tipo = TypedLoweredFilter(enum=AccesoDatoTypes)

    order = OrderingFilter(fields=("created_at",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = AccesoDatoPersonal
