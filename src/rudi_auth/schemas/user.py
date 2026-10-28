from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import StringConstraints

from api_auth.schemas.user import ApiUserInlineGet
from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, IsoDate, LaxEnum
from rudi_auth.filtersets.user import RudiUserFilterSet
from rudi_catalogos.enums import Etnias, Generos, TallasCamisa
from rudi_estados.enums import InputSourceTypes
from rudi_estados.schemas import EstadoRudiUserGet

from .types import TelefonoNI

########################################################################################


class UserPath(DTO):
    user_id: UUID


########################################################################################


class RudiUserInlineGet(BaseGet):
    user: ApiUserInlineGet
    origen: InputSourceTypes


########################################################################################


class RudiUserGet(RudiUserInlineGet):
    created_at: datetime
    updated_at: datetime

    estado: EstadoRudiUserGet

    fecha_nacimiento: date | None
    telefono: TelefonoNI

    genero: Generos | Literal[""]
    etnia: Etnias | Literal[""]
    talla: TallasCamisa | Literal[""]

    anonimizado_at: datetime | None


########################################################################################


class RudiUserWrite(DTO):
    fecha_nacimiento: IsoDate | None = None

    telefono: Annotated[TelefonoNI, StringConstraints(max_length=20)] = ""

    genero: LaxEnum[Generos] | Literal[""] = ""
    etnia: LaxEnum[Etnias] | Literal[""] = ""
    talla: LaxEnum[TallasCamisa] | Literal[""] = ""


########################################################################################

RudiUserPut = build_put_schema(RudiUserWrite)
RudiUserPatch = build_patch_schema(RudiUserPut)

########################################################################################

RudiUserFilterQuery = build_filter_query(PaginatedFilterQuery, RudiUserFilterSet)
RudiUserFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, RudiUserFilterSet)
