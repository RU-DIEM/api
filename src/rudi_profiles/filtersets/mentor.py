from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter, TypedLoweredFilter
from api_core.filtersets import ApiFilterSet
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

    class Meta(RudiProfileFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
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


class MentorAreaExperienciaFilterSet(ApiFilterSet):
    area = LoweredFilter(field_name="area__codigo")

    is_main = BooleanFilter()

    order = OrderingFilter(fields=("created_at",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = MentorAreaExperiencia


########################################################################################


class MentorCertificacionFilterSet(ApiFilterSet):
    nombre = LoweredFilter()
    institucion = LoweredFilter()

    search = LoweredSearchFilter("institucion", "nombre")

    order = OrderingFilter(fields=("created_at", "year"))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = MentorCertificacion
