from datetime import date
from typing import Annotated

from pydantic import StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, IsoDate
from rudi_auth.filtersets.politica import PoliticaPrivacidadFilterSet

########################################################################################

type PoliticaTexto = Annotated[str, StringConstraints(min_length=1)]

type PoliticaTitulo = Annotated[str, StringConstraints(max_length=200, min_length=1)]

type PoliticaVersion = Annotated[
    str,
    StringConstraints(max_length=20, min_length=3, pattern=r"^\d+\.\d+$"),
]

########################################################################################


class PoliticaPrivacidadInlineGet(BaseGet):
    version: str
    titulo: str

    vigente_desde: date
    vigente_hasta: date | None


########################################################################################


class PoliticaPrivacidadGet(PoliticaPrivacidadInlineGet):
    texto: str


########################################################################################


class PoliticaPrivacidadWrite(DTO):
    titulo: PoliticaTitulo
    texto: PoliticaTexto

    vigente_desde: IsoDate
    vigente_hasta: IsoDate | None = None


########################################################################################


class PoliticaPrivacidadPost(PoliticaPrivacidadWrite):
    version: PoliticaVersion


########################################################################################

PoliticaPrivacidadPut = build_put_schema(PoliticaPrivacidadWrite)
PoliticaPrivacidadPatch = build_patch_schema(PoliticaPrivacidadPut)

########################################################################################

PoliticaPrivacidadFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    PoliticaPrivacidadFilterSet,
)

PoliticaPrivacidadFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    PoliticaPrivacidadFilterSet,
)
