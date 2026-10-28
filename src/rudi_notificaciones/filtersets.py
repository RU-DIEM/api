from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter
from api_core.filtersets import ApiFilterSet
from rudi_notificaciones.models import Notificacion

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class NotificacionFilterSet(ApiFilterSet):
    cuenta_id = UUIDFilter(field_name="cuenta__id")

    plantilla = LoweredFilter(field_name="plantilla__codigo")
    destinatario = LoweredFilter()

    enviada = BooleanFilter(exclude=True, field_name="enviada_at", lookup_expr="isnull")
    descartada = BooleanFilter(
        exclude=True,
        field_name="descartada_at",
        lookup_expr="isnull",
    )

    order = OrderingFilter(fields=("created_at", "programada_para"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Notificacion
