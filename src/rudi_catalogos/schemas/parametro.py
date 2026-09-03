from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints

from api_auth.schemas.user import ApiUserInlineGet
from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet
from rudi_catalogos.enums import ParametroGrupoTypes, ParametroTypes
from rudi_catalogos.filtersets.parametro import ParametroFilterSet

########################################################################################

type ParametroValor = bool | int | str | list[str]

type ParametroDescripcion = Annotated[str, StringConstraints(max_length=300)]

########################################################################################


class ParametroInlineGet(BaseGet):
    codigo: str
    grupo: ParametroGrupoTypes
    tipo: ParametroTypes
    valor: ParametroValor


########################################################################################


class ParametroGet(ParametroInlineGet):
    updated_at: datetime
    updated_by: ApiUserInlineGet | None

    descripcion: str
    restricciones: dict


########################################################################################


class ParametroWrite(DTO):
    valor: ParametroValor
    descripcion: ParametroDescripcion = ""


########################################################################################

ParametroPut = build_put_schema(ParametroWrite)
ParametroPatch = build_patch_schema(ParametroPut)

########################################################################################

ParametroFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    ParametroFilterSet,
)
