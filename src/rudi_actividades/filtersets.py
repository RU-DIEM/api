from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter, UUIDFilter

from api_core.filters import (
    IntFilter,
    LoweredFilter,
    LoweredSearchFilter,
    TypedLoweredFilter,
)
from api_core.filtersets import ApiFilterSet, ApiSoftDeleteFilterSet
from rudi_actividades.enums import ModalidadTypes, ResponsableRolTypes
from rudi_actividades.models import Actividad, ActividadResponsable, Programa

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class ProgramaFilterSet(ApiSoftDeleteFilterSet):
    codigo = LoweredFilter()
    nombre = LoweredFilter()

    tipo_actividad = LoweredFilter(field_name="tipo_actividad__codigo")

    is_institucional = BooleanFilter()

    search = LoweredSearchFilter("codigo", "nombre", "nombre_corto")

    order = OrderingFilter(fields=("codigo", "created_at", "nombre"))

    class Meta(ApiSoftDeleteFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Programa


########################################################################################


class ActividadFilterSet(ApiFilterSet):
    programa_id = UUIDFilter(field_name="programa__id")

    tipo_actividad = LoweredFilter(field_name="tipo_actividad__codigo")
    estado = LoweredFilter(field_name="estado__codigo")

    modalidad = TypedLoweredFilter(enum=ModalidadTypes)

    anio = IntFilter()

    publica = BooleanFilter(field_name="estado__public")
    admite_inscripcion = BooleanFilter(field_name="estado__allow_inscripcion")
    admite_equipos = BooleanFilter()

    search = LoweredSearchFilter("descripcion", "etiqueta_edicion", "nombre")

    order = OrderingFilter(fields=("anio", "created_at", "fecha_inicio", "nombre"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Actividad


########################################################################################


class ActividadResponsableFilterSet(ApiFilterSet):
    user_id = UUIDFilter(field_name="user__id")

    rol = TypedLoweredFilter(enum=ResponsableRolTypes)

    is_public = BooleanFilter()
    retirado = BooleanFilter(
        field_name="retirado_at", lookup_expr="isnull", exclude=True
    )

    order = OrderingFilter(fields=("created_at",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = ActividadResponsable
