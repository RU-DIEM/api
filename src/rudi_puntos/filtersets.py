from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter, UUIDFilter

from api_core.filters import (
    IntFilter,
    LoweredFilter,
    LoweredSearchFilter,
    TypedLoweredFilter,
)
from api_core.filtersets import ApiFilterSet, ApiSoftDeleteFilterSet
from rudi_puntos.enums import MovimientoOrigenTypes
from rudi_puntos.models import MovimientoPunto, ReglaPuntuacion

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class ReglaPuntuacionFilterSet(ApiSoftDeleteFilterSet):
    codigo = LoweredFilter()

    tipo_actividad = LoweredFilter(field_name="tipo_actividad__codigo")
    programa_id = UUIDFilter(field_name="programa__id")
    rol = LoweredFilter(field_name="rol__codigo")

    search = LoweredSearchFilter("codigo", "etiqueta")

    order = OrderingFilter(fields=("codigo", "created_at", "especificidad", "puntos"))

    class Meta(ApiSoftDeleteFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = ReglaPuntuacion


########################################################################################


class MovimientoPuntoFilterSet(ApiFilterSet):
    user_id = UUIDFilter(field_name="user__id")
    participacion_id = UUIDFilter(field_name="participacion__id")

    origen = TypedLoweredFilter(enum=MovimientoOrigenTypes)
    anio = IntFilter()

    revertido = BooleanFilter(
        exclude=True,
        field_name="revertido_at",
        lookup_expr="isnull",
    )

    order = OrderingFilter(fields=("anio", "created_at", "puntos"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = MovimientoPunto
