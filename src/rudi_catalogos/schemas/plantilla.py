from typing import Annotated

from pydantic import Field, StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from rudi_catalogos.filtersets.plantilla import PlantillaMensajeFilterSet

from .base import CatalogoCodigo, CatalogoEtiqueta, RudiCatalogoInlineGet

########################################################################################

type PlantillaAsunto = Annotated[str, StringConstraints(max_length=200, min_length=1)]

type PlantillaCuerpo = Annotated[str, StringConstraints(max_length=8_000, min_length=1)]

type PlantillaVariable = Annotated[
    str,
    StringConstraints(max_length=50, min_length=1, pattern=r"^[a-z][a-z0-9_]*$"),
]

########################################################################################


class PlantillaMensajeInlineGet(RudiCatalogoInlineGet):
    asunto: str


########################################################################################


class PlantillaMensajeGet(PlantillaMensajeInlineGet):
    cuerpo: str
    is_active: bool
    variables: list[str]


########################################################################################


class PlantillaMensajeWrite(DTO):
    etiqueta: CatalogoEtiqueta
    is_active: bool = True

    asunto: PlantillaAsunto
    cuerpo: PlantillaCuerpo
    variables: list[PlantillaVariable] = Field(default_factory=list)


########################################################################################


class PlantillaMensajePost(PlantillaMensajeWrite):
    codigo: CatalogoCodigo


########################################################################################

PlantillaMensajePut = build_put_schema(PlantillaMensajeWrite)
PlantillaMensajePatch = build_patch_schema(PlantillaMensajePut)

########################################################################################

PlantillaMensajeFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    PlantillaMensajeFilterSet,
)

PlantillaMensajeFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    PlantillaMensajeFilterSet,
)
