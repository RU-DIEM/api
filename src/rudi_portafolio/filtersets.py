from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter, UUIDFilter

from api_core.filters import (
    IntFilter,
    LoweredFilter,
    LoweredSearchFilter,
    TypedLoweredFilter,
)
from api_core.filtersets import ApiFilterSet
from rudi_catalogos.enums import (
    MRL,
    ODS,
    TRL,
    AmbitosAplicacion,
    EtapasDesarrollo,
    NivelesFormalizacion,
    SectoresAplicacion,
    TiposInnovacion,
    VerticalesInnovacion,
)
from rudi_portafolio.enums import IntegranteRolTypes, PropuestaActividadRolTypes
from rudi_portafolio.models import Propuesta, PropuestaActividad, PropuestaIntegrante

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class PropuestaFilterSet(ApiFilterSet):
    codigo = LoweredFilter()
    anio_ingreso = IntFilter()

    actividad_origen_id = UUIDFilter(field_name="actividad_origen__id")
    estado = LoweredFilter(field_name="estado__codigo")

    nivel_formalizacion = TypedLoweredFilter(enum=NivelesFormalizacion)
    etapa_desarrollo = TypedLoweredFilter(enum=EtapasDesarrollo)
    ambito_aplicacion = TypedLoweredFilter(enum=AmbitosAplicacion)
    sector_aplicacion = TypedLoweredFilter(enum=SectoresAplicacion)
    vertical = TypedLoweredFilter(enum=VerticalesInnovacion)
    tipo_innovacion = TypedLoweredFilter(enum=TiposInnovacion)
    trl = TypedLoweredFilter(enum=TRL)
    mrl = TypedLoweredFilter(enum=MRL)
    ods = TypedLoweredFilter(enum=ODS, field_name="ods_principal")

    clasificada = BooleanFilter(
        exclude=True,
        field_name="clasificada_at",
        lookup_expr="isnull",
    )
    cerrada = BooleanFilter(exclude=True, field_name="cerrada_at", lookup_expr="isnull")

    search = LoweredSearchFilter("codigo", "nombre", "problema", "solucion")

    order = OrderingFilter(fields=("anio_ingreso", "codigo", "created_at", "nombre"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Propuesta


class PropuestaIntegranteFilterSet(ApiFilterSet):
    user_id = UUIDFilter(field_name="user__id")

    rol = TypedLoweredFilter(enum=IntegranteRolTypes)

    vigente = BooleanFilter(field_name="hasta", lookup_expr="isnull")
    is_contacto = BooleanFilter()

    order = OrderingFilter(fields=("created_at", "desde"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = PropuestaIntegrante


class PropuestaActividadFilterSet(ApiFilterSet):
    actividad_id = UUIDFilter(field_name="actividad__id")

    rol = TypedLoweredFilter(enum=PropuestaActividadRolTypes)

    order = OrderingFilter(fields=("created_at",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = PropuestaActividad
