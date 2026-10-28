from typing import TYPE_CHECKING

from django_filters import BooleanFilter, OrderingFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter, TypedLoweredFilter
from api_core.filtersets import ApiSoftDeleteFilterSet
from rudi_catalogos.filtersets.base import RudiCatalogoFilterSet
from rudi_profiles.enums import InstitucionTypes
from rudi_profiles.models import Carrera, Facultad, Institucion

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model, QuerySet

########################################################################################


class FacultadFilterSet(RudiCatalogoFilterSet):
    abreviacion = LoweredFilter()

    class Meta(RudiCatalogoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = Facultad


########################################################################################


class CarreraFilterSet(RudiCatalogoFilterSet):
    facultad = LoweredFilter(field_name="facultad__codigo")

    class Meta(RudiCatalogoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = Carrera


########################################################################################


class InstitucionFilterSet(ApiSoftDeleteFilterSet):
    nombre = LoweredFilter()

    tipo = TypedLoweredFilter(enum=InstitucionTypes)

    pendiente = BooleanFilter(method="filter_pendiente")

    search = LoweredSearchFilter("nombre")

    order = OrderingFilter(fields=("created_at", "nombre"))

    class Meta(ApiSoftDeleteFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Institucion

    def filter_pendiente(  # ruff: ignore[no-self-use]
        self,
        qs: QuerySet,
        name: str,  # ruff: ignore[unused-method-argument]
        value: bool | None,  # ruff: ignore[boolean-type-hint-positional-argument]
    ) -> QuerySet:
        if value is None:
            return qs

        return qs.filter(normalizada_at__isnull=value)
