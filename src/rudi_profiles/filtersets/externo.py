from typing import TYPE_CHECKING

from django_filters import UUIDFilter

from api_core.filters import TypedLoweredFilter
from rudi_profiles.enums import OcupacionTypes
from rudi_profiles.models import ExternoProfile

from .base import RudiProfileFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class ExternoProfileFilterSet(RudiProfileFilterSet):
    institucion = UUIDFilter(field_name="institucion__id")

    ocupacion = TypedLoweredFilter(enum=OcupacionTypes)

    class Meta(RudiProfileFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = ExternoProfile
