from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, LaxEnum, RelatedId
from rudi_catalogos.schemas.base import (
    CatalogoCodigo,
    RudiCatalogoGet,
    RudiCatalogoInlineGet,
    RudiCatalogoWrite,
)
from rudi_profiles.enums import InstitucionTypes
from rudi_profiles.filtersets.academia import (
    CarreraFilterSet,
    FacultadFilterSet,
    InstitucionFilterSet,
)

########################################################################################

type CarreraDuracion = Annotated[int, Field(ge=1, le=8)]

type FacultadAbreviacion = Annotated[str, StringConstraints(max_length=30)]

type InstitucionNombre = Annotated[
    str,
    StringConstraints(max_length=200, min_length=2),
]

########################################################################################


class FacultadInlineGet(RudiCatalogoInlineGet):
    abreviacion: str


########################################################################################


class FacultadGet(RudiCatalogoGet):
    abreviacion: str


########################################################################################


class FacultadWrite(RudiCatalogoWrite):
    abreviacion: FacultadAbreviacion = ""


########################################################################################


class FacultadPost(FacultadWrite):
    codigo: CatalogoCodigo


########################################################################################


class CarreraInlineGet(RudiCatalogoInlineGet):
    duracion: int | None


########################################################################################


class CarreraGet(RudiCatalogoGet):
    facultad: FacultadInlineGet

    duracion: int | None


########################################################################################


class CarreraWrite(RudiCatalogoWrite):
    duracion: CarreraDuracion | None = None


########################################################################################


class CarreraPost(CarreraWrite):
    codigo: CatalogoCodigo
    facultad: RelatedId


########################################################################################


class InstitucionInlineGet(BaseGet):
    nombre: str
    tipo: InstitucionTypes


########################################################################################


class InstitucionGet(InstitucionInlineGet):
    is_active: bool

    normalizada_at: datetime | None


########################################################################################


class InstitucionWrite(DTO):
    nombre: InstitucionNombre
    tipo: LaxEnum[InstitucionTypes]

    is_active: bool = True


########################################################################################


class InstitucionPost(InstitucionWrite):
    pass


########################################################################################

CarreraPut = build_put_schema(CarreraWrite)
CarreraPatch = build_patch_schema(CarreraPut)

FacultadPut = build_put_schema(FacultadWrite)
FacultadPatch = build_patch_schema(FacultadPut)

InstitucionPut = build_put_schema(InstitucionWrite)
InstitucionPatch = build_patch_schema(InstitucionPut)

########################################################################################

CarreraFilterQuery = build_filter_query(PaginatedFilterQuery, CarreraFilterSet)
CarreraFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, CarreraFilterSet)

FacultadFilterQuery = build_filter_query(PaginatedFilterQuery, FacultadFilterSet)
FacultadFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, FacultadFilterSet)

InstitucionFilterQuery = build_filter_query(PaginatedFilterQuery, InstitucionFilterSet)

InstitucionFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    InstitucionFilterSet,
)
