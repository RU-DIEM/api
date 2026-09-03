from api_core.schemas.factories import build_filter_query
from api_core.schemas.filters import UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet
from rudi_catalogos.filtersets.ubicaciones import (
    DepartamentoFilterSet,
    MunicipioFilterSet,
)

########################################################################################


class DepartamentoInlineGet(BaseGet):
    nombre: str


########################################################################################


class DepartamentoGet(DepartamentoInlineGet):
    is_active: bool


########################################################################################


class MunicipioInlineGet(BaseGet):
    nombre: str


########################################################################################


class MunicipioGet(MunicipioInlineGet):
    departamento: DepartamentoInlineGet
    is_active: bool


########################################################################################

DepartamentoFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    DepartamentoFilterSet,
)

MunicipioFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    MunicipioFilterSet,
)
