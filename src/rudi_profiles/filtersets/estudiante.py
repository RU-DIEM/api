from typing import TYPE_CHECKING

from django_filters import (
    BooleanFilter,
    DateTimeFromToRangeFilter,
    OrderingFilter,
)

from api_core.filters import LoweredFilter, TypedLoweredFilter
from api_core.filtersets import ApiFilterSet
from rudi_catalogos.enums import NivelesCarrera
from rudi_profiles.models import EstudianteCarrera, EstudianteProfile

from .base import RudiProfileFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model, QuerySet

########################################################################################


class EstudianteProfileFilterSet(RudiProfileFilterSet):
    carrera = LoweredFilter(field_name="carreras__carrera__codigo")

    class Meta(RudiProfileFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = EstudianteProfile


########################################################################################


class EstudianteCarreraFilterSet(ApiFilterSet):
    carrera = LoweredFilter(field_name="carrera__codigo")

    nivel = TypedLoweredFilter(enum=NivelesCarrera)

    is_main = BooleanFilter()

    vigente = BooleanFilter(method="filter_vigente")

    cerrada_at = DateTimeFromToRangeFilter()

    order = OrderingFilter(fields=("created_at", "iniciada_en"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = EstudianteCarrera

    def filter_vigente(  # ruff: ignore[no-self-use]
        self,
        qs: QuerySet,
        name: str,  # ruff: ignore[unused-method-argument]
        value: bool | None,  # ruff: ignore[boolean-type-hint-positional-argument]
    ) -> QuerySet:
        if value is None:
            return qs

        return qs.filter(cerrada_at__isnull=value)
