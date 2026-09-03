from typing import TYPE_CHECKING

from django_filters import BooleanFilter, FilterSet, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter
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


class RudiEstadoFilterSet(FilterSet):
    id = UUIDFilter()

    codigo = LoweredFilter()
    etiqueta = LoweredFilter()

    initial = BooleanFilter()
    terminal = BooleanFilter()
    is_active = BooleanFilter()

    search = LoweredSearchFilter("codigo", "descripcion", "etiqueta")

    order = OrderingFilter(fields=("codigo", "etiqueta"))

    class Meta:
        fields: Sequence[str] = ()


########################################################################################


class EstadoActividadFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoActividad


########################################################################################


class EstadoAsignacionMentorFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoAsignacionMentor


########################################################################################


class EstadoConsentimientoFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoConsentimiento


########################################################################################


class EstadoConstanciaFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoConstancia


########################################################################################


class EstadoInscripcionFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoInscripcion


########################################################################################


class EstadoParticipacionFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoParticipacion


########################################################################################


class EstadoPropuestaFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoPropuesta


########################################################################################


class EstadoRudiUserFilterSet(RudiEstadoFilterSet):
    class Meta(RudiEstadoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = EstadoRudiUser
