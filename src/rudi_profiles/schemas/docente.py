from typing import Annotated, Literal

from pydantic import StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import LaxEnum, RelatedId
from rudi_catalogos.enums import NivelesAcademicos
from rudi_profiles.filtersets.docente import DocenteProfileFilterSet
from rudi_profiles.schemas.academia import FacultadInlineGet

from .base import RudiProfileGet, RudiProfileInlineGet

########################################################################################

type Cargo = Annotated[str, StringConstraints(max_length=120)]

type NivelAcademico = LaxEnum[NivelesAcademicos] | Literal[""]

########################################################################################


class DocenteProfileInlineGet(RudiProfileInlineGet):
    cargo: str


########################################################################################


class DocenteProfileGet(RudiProfileGet):
    facultad: FacultadInlineGet | None

    nivel_academico: NivelAcademico
    cargo: str


########################################################################################


class DocenteProfileWrite(DTO):
    facultad: RelatedId | None = None

    nivel_academico: NivelAcademico = ""
    cargo: Cargo = ""


########################################################################################


class DocenteProfilePost(DocenteProfileWrite):
    user: RelatedId


########################################################################################

DocenteProfilePut = build_put_schema(DocenteProfileWrite)
DocenteProfilePatch = build_patch_schema(DocenteProfilePut)

########################################################################################

DocenteProfileFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    DocenteProfileFilterSet,
)

DocenteProfileFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    DocenteProfileFilterSet,
)
