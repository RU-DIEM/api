from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, IsoDateTime, LaxEnum, RelatedId
from rudi_catalogos.enums import NivelesCarrera
from rudi_profiles.filtersets.estudiante import (
    EstudianteCarreraFilterSet,
    EstudianteProfileFilterSet,
)
from rudi_profiles.schemas.academia import CarreraInlineGet

from .base import RudiProfileGet, RudiProfileInlineGet

########################################################################################

type CarreraNivel = LaxEnum[NivelesCarrera] | Literal[""]

type CarreraYear = Annotated[int, Field(ge=2000, le=3000)]

########################################################################################


class EstudianteCarreraGet(BaseGet):
    carrera: CarreraInlineGet

    nivel: CarreraNivel
    is_main: bool

    iniciada_en: int | None
    cerrada_at: datetime | None


########################################################################################


class EstudianteCarreraWrite(DTO):
    nivel: CarreraNivel = ""
    is_main: bool = False

    iniciada_en: CarreraYear | None = None
    cerrada_at: IsoDateTime | None = None


########################################################################################


class EstudianteCarreraPost(EstudianteCarreraWrite):
    carrera: RelatedId


########################################################################################


class EstudianteProfileInlineGet(RudiProfileInlineGet):
    pass


########################################################################################


class EstudianteProfileGet(RudiProfileGet):
    carreras: list[EstudianteCarreraGet]


########################################################################################


class EstudianteProfilePost(DTO):
    user: RelatedId

    carreras: Annotated[list[EstudianteCarreraPost], Field(min_length=1)]


########################################################################################

EstudianteCarreraPut = build_put_schema(EstudianteCarreraWrite)
EstudianteCarreraPatch = build_patch_schema(EstudianteCarreraPut)

########################################################################################

EstudianteCarreraFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    EstudianteCarreraFilterSet,
)

EstudianteProfileFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    EstudianteProfileFilterSet,
)

EstudianteProfileFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstudianteProfileFilterSet,
)
