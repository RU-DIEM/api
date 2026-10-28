from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter
from api_core.filtersets import ApiSoftDeleteFilterSet
from rudi_estados.models import (
    EstadoActividad,
    EstadoAsignacionMentor,
    EstadoConsentimiento,
    EstadoConstancia,
    EstadoInscripcion,
    EstadoParticipacion,
    EstadoPropuesta,
    EstadoRudiUser,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class RudiEstadoFilterSet(ApiSoftDeleteFilterSet):
    codigo = LoweredFilter()
    etiqueta = LoweredFilter()

    initial = BooleanFilter()
    terminal = BooleanFilter()

    search = LoweredSearchFilter("codigo", "descripcion", "etiqueta")

    order = OrderingFilter(fields=("codigo", "etiqueta"))


########################################################################################


class EstadoActividadFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoActividad


########################################################################################


class EstadoAsignacionMentorFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoAsignacionMentor


########################################################################################


class EstadoConsentimientoFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoConsentimiento


########################################################################################


class EstadoConstanciaFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoConstancia


########################################################################################


class EstadoInscripcionFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoInscripcion


########################################################################################


class EstadoParticipacionFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoParticipacion


########################################################################################


class EstadoPropuestaFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoPropuesta


########################################################################################


class EstadoRudiUserFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstadoRudiUser
