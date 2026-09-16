from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, RelatedId
from rudi_auth.filtersets.identificador import IdentificadorUserFilterSet
from rudi_catalogos.schemas.identificador import TipoIdentificadorInlineGet

########################################################################################

type IdentificadorValor = Annotated[
    str,
    StringConstraints(max_length=20, min_length=4),
]

########################################################################################


class IdentificadorUserInlineGet(BaseGet):
    tipo: TipoIdentificadorInlineGet
    valor: str
    is_main: bool


########################################################################################


class IdentificadorUserGet(IdentificadorUserInlineGet):
    created_at: datetime

    valor_normalizado: str

    verificado_at: datetime | None


########################################################################################


class IdentificadorUserWrite(DTO):
    valor: IdentificadorValor
    is_main: bool = False


########################################################################################


class IdentificadorUserPost(IdentificadorUserWrite):
    tipo: RelatedId


########################################################################################

IdentificadorUserPut = build_put_schema(IdentificadorUserWrite)
IdentificadorUserPatch = build_patch_schema(IdentificadorUserPut)

########################################################################################

IdentificadorUserFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    IdentificadorUserFilterSet,
)

IdentificadorUserFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    IdentificadorUserFilterSet,
)
