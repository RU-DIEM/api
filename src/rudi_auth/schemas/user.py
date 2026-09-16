from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import StringConstraints
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

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

########################################################################################

type Telefono = (
    Annotated[
        PhoneNumber,
        PhoneNumberValidator(default_region="NI", number_format="INTERNATIONAL"),
        StringConstraints(max_length=20),
    ]
    | Literal[""]
)

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
    telefono: Telefono

    genero: Generos | Literal[""]
    etnia: Etnias | Literal[""]
    talla: TallasCamisa | Literal[""]

    email_verified_at: datetime | None
    anonimizado_at: datetime | None


########################################################################################


class RudiUserWrite(DTO):
    fecha_nacimiento: IsoDate | None = None

    telefono: Telefono = ""

    genero: LaxEnum[Generos] | Literal[""] = ""
    etnia: LaxEnum[Etnias] | Literal[""] = ""
    talla: LaxEnum[TallasCamisa] | Literal[""] = ""


########################################################################################

RudiUserPut = build_put_schema(RudiUserWrite)
RudiUserPatch = build_patch_schema(RudiUserPut)

########################################################################################

RudiUserFilterQuery = build_filter_query(PaginatedFilterQuery, RudiUserFilterSet)
RudiUserFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, RudiUserFilterSet)
