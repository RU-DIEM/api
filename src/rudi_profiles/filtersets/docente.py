from typing import TYPE_CHECKING

from api_core.filters import LoweredFilter, TypedLoweredFilter
from rudi_catalogos.enums import NivelesAcademicos
from rudi_profiles.models import DocenteProfile

from .base import RudiProfileFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class DocenteProfileFilterSet(RudiProfileFilterSet):
    facultad = LoweredFilter(field_name="facultad__codigo")

    nivel_academico = TypedLoweredFilter(enum=NivelesAcademicos)

    class Meta(RudiProfileFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = DocenteProfile
