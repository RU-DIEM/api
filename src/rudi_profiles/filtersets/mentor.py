from typing import TYPE_CHECKING

from django_filters import BooleanFilter, FilterSet, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter, TypedLoweredFilter
from rudi_catalogos.enums import NivelesAcademicos
from rudi_profiles.models import (
    MentorAreaExperiencia,
    MentorCertificacion,
    MentorProfile,
)

from .base import RudiProfileFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model, QuerySet

########################################################################################


class MentorProfileFilterSet(RudiProfileFilterSet):
    tipo_mentor = LoweredFilter(field_name="tipo_mentor__codigo")

    municipio = UUIDFilter(field_name="municipio__id")
    departamento = UUIDFilter(field_name="municipio__departamento__id")

    nivel_academico = TypedLoweredFilter(enum=NivelesAcademicos)

    confirmado = BooleanFilter(method="filter_confirmado")

    search = LoweredSearchFilter("descripcion_profesional")

    class Meta(RudiProfileFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = MentorProfile

    def filter_confirmado(  # ruff: ignore[no-self-use]
        self,
        qs: QuerySet,
        name: str,  # ruff: ignore[unused-method-argument]
        value: bool | None,  # ruff: ignore[boolean-type-hint-positional-argument]
    ) -> QuerySet:
        if value is None:
            return qs

        return qs.filter(confirmado_at__isnull=(not value))


########################################################################################


class MentorAreaExperienciaFilterSet(FilterSet):
    id = UUIDFilter()

    area = LoweredFilter(field_name="area__codigo")

    is_main = BooleanFilter()

    order = OrderingFilter(fields=("created_at",))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = MentorAreaExperiencia


########################################################################################


class MentorCertificacionFilterSet(FilterSet):
    id = UUIDFilter()

    nombre = LoweredFilter()
    institucion = LoweredFilter()

    search = LoweredSearchFilter("institucion", "nombre")

    order = OrderingFilter(fields=("created_at", "year"))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = MentorCertificacion
