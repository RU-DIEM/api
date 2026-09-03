from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from rudi_catalogos.filtersets.identificador import TipoIdentificadorFilterSet

from .base import (
    CatalogoCodigo,
    CatalogoEtiqueta,
    CatalogoRegex,
    RudiCatalogoInlineGet,
)

########################################################################################


class TipoIdentificadorInlineGet(RudiCatalogoInlineGet):
    pass


########################################################################################


class TipoIdentificadorGet(TipoIdentificadorInlineGet):
    is_active: bool
    is_institucional: bool
    regex: str


########################################################################################


class TipoIdentificadorWrite(DTO):
    etiqueta: CatalogoEtiqueta
    is_active: bool = True

    is_institucional: bool = False
    regex: CatalogoRegex = ""


########################################################################################


class TipoIdentificadorPost(TipoIdentificadorWrite):
    codigo: CatalogoCodigo


########################################################################################

TipoIdentificadorPut = build_put_schema(TipoIdentificadorWrite)
TipoIdentificadorPatch = build_patch_schema(TipoIdentificadorPut)

########################################################################################

TipoIdentificadorFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    TipoIdentificadorFilterSet,
)

TipoIdentificadorFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    TipoIdentificadorFilterSet,
)
