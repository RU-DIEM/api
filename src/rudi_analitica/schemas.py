from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import build_filter_query
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, LaxEnum
from rudi_analitica.enums import IndicadorUnidadTypes
from rudi_analitica.filtersets import IndicadorPeriodoFilterSet
from rudi_core.types import Anio

########################################################################################


class IndicadorPeriodoGet(BaseGet):
    indicador: str
    anio: int

    dimension: str
    dimension_valor: str

    valor: Decimal
    unidad: IndicadorUnidadTypes

    metodo: str
    filas_origen: int

    cerrado_por_id: UUID | None
    created_at: datetime


class IndicadorPeriodoPost(DTO):
    """
    One frozen figure of a closed year, filed by hand (RF-A-45).
    """

    indicador: Annotated[
        str,
        StringConstraints(max_length=60, min_length=1, pattern=r"^[a-z][a-z0-9_]*$"),
    ]
    anio: Anio

    dimension: Annotated[str, StringConstraints(max_length=40)] = ""
    dimension_valor: Annotated[str, StringConstraints(max_length=150)] = ""

    valor: Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
    unidad: LaxEnum[IndicadorUnidadTypes] = IndicadorUnidadTypes.PERSONAS

    metodo: Annotated[str, StringConstraints(max_length=4_000)] = ""
    filas_origen: Annotated[int, Field(ge=0)] = 0


class CerrarPeriodoPost(DTO):
    anio: Anio


########################################################################################

IndicadorPeriodoFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    IndicadorPeriodoFilterSet,
)
IndicadorPeriodoFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    IndicadorPeriodoFilterSet,
)
