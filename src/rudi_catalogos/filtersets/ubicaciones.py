from typing import TYPE_CHECKING

from django_filters import OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter
from api_core.filtersets import ApiFilterSet
from rudi_catalogos.models import Departamento, Municipio

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class DepartamentoFilterSet(ApiFilterSet):
    nombre = LoweredFilter()

    search = LoweredSearchFilter("nombre")
    order = OrderingFilter(fields=("nombre",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Departamento


########################################################################################


class MunicipioFilterSet(ApiFilterSet):
    departamento = UUIDFilter()
    nombre = LoweredFilter()

    search = LoweredSearchFilter("nombre")
    order = OrderingFilter(fields=("nombre",))

    class Meta(ApiFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Municipio
