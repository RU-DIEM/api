from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter, UUIDFilter

from api_core.filters import (
    IntFilter,
    LoweredFilter,
    LoweredSearchFilter,
    TypedLoweredFilter,
)
from api_core.filtersets import ApiFilterSet
from rudi_estados.enums import InputSourceTypes
from rudi_participacion.enums import AcompanamientoTypes, ParticipacionOrigenTypes
from rudi_participacion.models import (
    AsignacionMentor,
    Equipo,
    EquipoMiembro,
    Inscripcion,
    Participacion,
    Reconocimiento,
)

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class InscripcionFilterSet(ApiFilterSet):
    user_id = UUIDFilter(field_name="user__id")
    actividad_id = UUIDFilter(field_name="actividad__id")

    estado = LoweredFilter(field_name="estado__codigo")
    origen = TypedLoweredFilter(enum=InputSourceTypes)

    en_espera = BooleanFilter(
        exclude=True,
        field_name="posicion_espera",
        lookup_expr="isnull",
    )
    cerrada = BooleanFilter(exclude=True, field_name="cerrada_at", lookup_expr="isnull")

    order = OrderingFilter(fields=("created_at", "posicion_espera"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Inscripcion


########################################################################################


class ParticipacionFilterSet(ApiFilterSet):
    user_id = UUIDFilter(field_name="user__id")
    actividad_id = UUIDFilter(field_name="actividad__id")
    equipo_id = UUIDFilter(field_name="equipo__id")

    anio = IntFilter()

    estado = LoweredFilter(field_name="estado__codigo")
    rol = LoweredFilter(field_name="rol__codigo")
    origen = TypedLoweredFilter(enum=ParticipacionOrigenTypes)

    efectiva = BooleanFilter(field_name="estado__efectiva")
    validada = BooleanFilter(
        exclude=True, field_name="validada_at", lookup_expr="isnull"
    )
    anulada = BooleanFilter(exclude=True, field_name="anulada_at", lookup_expr="isnull")

    order = OrderingFilter(fields=("anio", "created_at", "validada_at"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Participacion


########################################################################################


class ReconocimientoFilterSet(ApiFilterSet):
    tipo = LoweredFilter(field_name="tipo__codigo")

    anulado = BooleanFilter(exclude=True, field_name="anulado_at", lookup_expr="isnull")

    order = OrderingFilter(fields=("created_at", "otorgado_en", "posicion"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Reconocimiento


########################################################################################


class EquipoFilterSet(ApiFilterSet):
    actividad_id = UUIDFilter(field_name="actividad__id")

    codigo_union = LoweredFilter()

    congelado = BooleanFilter(
        exclude=True,
        field_name="congelado_at",
        lookup_expr="isnull",
    )

    search = LoweredSearchFilter("nombre")

    order = OrderingFilter(fields=("created_at", "nombre"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Equipo


class EquipoMiembroFilterSet(ApiFilterSet):
    user_id = UUIDFilter(field_name="user__id")

    is_lider = BooleanFilter()
    retirado = BooleanFilter(
        exclude=True, field_name="retirado_at", lookup_expr="isnull"
    )

    order = OrderingFilter(fields=("created_at",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = EquipoMiembro


########################################################################################


class AsignacionMentorFilterSet(ApiFilterSet):
    actividad_id = UUIDFilter(field_name="actividad__id")
    mentor_id = UUIDFilter(field_name="mentor__id")
    equipo_id = UUIDFilter(field_name="equipo__id")

    estado = LoweredFilter(field_name="estado__codigo")
    tipo_acompanamiento = TypedLoweredFilter(enum=AcompanamientoTypes)

    pendiente = BooleanFilter(field_name="respondida_at", lookup_expr="isnull")

    order = OrderingFilter(fields=("created_at", "propuesta_at"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = AsignacionMentor
