from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter
from api_core.filtersets import ApiFilterSet
from rudi_constancias.models import (
    Constancia,
    ConstanciaParticipacion,
    PlantillaConstancia,
)

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class PlantillaConstanciaFilterSet(ApiFilterSet):
    codigo = LoweredFilter()

    vigente = BooleanFilter(field_name="vigente_hasta", lookup_expr="isnull")

    order = OrderingFilter(fields=("codigo", "created_at", "version"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = PlantillaConstancia


class ConstanciaFilterSet(ApiFilterSet):
    user_id = UUIDFilter(field_name="user__id")
    plantilla_id = UUIDFilter(field_name="plantilla__id")

    folio = LoweredFilter()
    estado = LoweredFilter(field_name="estado__codigo")

    anulada = BooleanFilter(exclude=True, field_name="anulada_at", lookup_expr="isnull")

    order = OrderingFilter(fields=("created_at", "emitida_at", "folio"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Constancia


class ConstanciaParticipacionFilterSet(ApiFilterSet):
    participacion_id = UUIDFilter(field_name="participacion__id")

    order = OrderingFilter(fields=("orden",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = ConstanciaParticipacion
