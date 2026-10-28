from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints, model_validator

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, IsoDate, RelatedId
from rudi_actividades.schemas import ProgramaInlineGet
from rudi_auth.schemas.user import RudiUserInlineGet
from rudi_catalogos.schemas.actividad import TipoActividadInlineGet
from rudi_catalogos.schemas.base import CatalogoCodigo
from rudi_catalogos.schemas.motivo import MotivoInlineGet
from rudi_catalogos.schemas.reconocimiento import TipoReconocimientoInlineGet
from rudi_catalogos.schemas.rol import RolParticipacionInlineGet
from rudi_core.types import Anio, Puntos
from rudi_estados.schemas import EstadoParticipacionGet
from rudi_puntos.enums import MovimientoOrigenTypes
from rudi_puntos.filtersets import MovimientoPuntoFilterSet, ReglaPuntuacionFilterSet

########################################################################################

type Descripcion = Annotated[str, StringConstraints(max_length=300)]

########################################################################################


class VigenciaGet(DTO):
    """
    A `daterange`, half open: `upper` is the first day the rule no longer applies.
    """

    lower: date | None
    upper: date | None


class Vigencia(DTO):
    lower: IsoDate
    upper: IsoDate | None = None

    @model_validator(mode="after")
    def check_orden(self) -> Vigencia:
        if self.upper is not None and self.upper <= self.lower:
            raise ValueError("La vigencia termina después de empezar.")

        return self


########################################################################################


class ReglaPuntuacionGet(BaseGet):
    codigo: str
    etiqueta: str

    tipo_actividad: TipoActividadInlineGet | None
    programa: ProgramaInlineGet | None
    rol: RolParticipacionInlineGet | None
    estado_participacion: EstadoParticipacionGet | None
    tipo_reconocimiento: TipoReconocimientoInlineGet | None

    puntos: int
    especificidad: int
    vigencia: VigenciaGet

    is_active: bool


class ReglaPuntuacionWrite(DTO):
    etiqueta: Annotated[str, StringConstraints(max_length=150, min_length=1)]

    tipo_actividad: RelatedId | None = None
    programa: RelatedId | None = None
    rol: RelatedId | None = None
    estado_participacion: RelatedId | None = None
    tipo_reconocimiento: RelatedId | None = None

    puntos: Puntos
    vigencia: Vigencia

    is_active: bool = True


class ReglaPuntuacionPost(ReglaPuntuacionWrite):
    codigo: CatalogoCodigo


########################################################################################


class MovimientoPuntoGet(BaseGet):
    user: RudiUserInlineGet
    participacion_id: UUID | None
    regla_id: UUID | None

    puntos: int
    origen: MovimientoOrigenTypes
    anio: int

    motivo: MotivoInlineGet | None
    descripcion: str

    revierte_id: UUID | None
    revertido_at: datetime | None
    registrado_por_id: UUID | None

    created_at: datetime


class MovimientoPuntoPost(DTO):
    """
    A manual adjustment (RF-A-32): signed points, always with a reason.
    """

    user: RelatedId
    participacion: RelatedId | None = None

    puntos: Annotated[int, Field(ge=-500, le=500)]
    anio: Anio

    motivo: RelatedId
    descripcion: Descripcion = ""


class MovimientoRevertirPost(DTO):
    movimiento_id: UUID
    motivo_id: UUID
    descripcion: Descripcion = ""


class SaldoGet(DTO):
    user_id: UUID
    saldo: int
    automatico: int
    manual: int


########################################################################################

ReglaPuntuacionPut = build_put_schema(ReglaPuntuacionWrite)
ReglaPuntuacionPatch = build_patch_schema(ReglaPuntuacionPut)

########################################################################################

ReglaPuntuacionFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    ReglaPuntuacionFilterSet,
)
ReglaPuntuacionFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    ReglaPuntuacionFilterSet,
)

MovimientoPuntoFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    MovimientoPuntoFilterSet,
)
