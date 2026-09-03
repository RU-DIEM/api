from typing import TYPE_CHECKING

from django_filters import FilterSet, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter
from rudi_catalogos.models import Departamento, Municipio

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class DepartamentoFilterSet(FilterSet):
    id = UUIDFilter()
    nombre = LoweredFilter()

    search = LoweredSearchFilter("nombre")
    order = OrderingFilter(fields=("nombre",))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = Departamento


########################################################################################


class MunicipioFilterSet(FilterSet):
    id = UUIDFilter()
    departamento = UUIDFilter()
    nombre = LoweredFilter()

    search = LoweredSearchFilter("nombre")
    order = OrderingFilter(fields=("nombre",))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = Municipio
