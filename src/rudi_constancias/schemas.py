from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, IsoDate, RelatedId
from rudi_auth.schemas.user import RudiUserInlineGet
from rudi_catalogos.schemas.base import CatalogoCodigo
from rudi_catalogos.schemas.motivo import MotivoInlineGet
from rudi_constancias.filtersets import (
    ConstanciaFilterSet,
    ConstanciaParticipacionFilterSet,
    PlantillaConstanciaFilterSet,
)
from rudi_core.types import EnlaceUrl, MotivoDescripcion
from rudi_estados.schemas import EstadoConstanciaGet

########################################################################################

type Campo = Annotated[str, StringConstraints(max_length=50, pattern=r"^[a-z_]+$")]

type Firma = Annotated[str, StringConstraints(max_length=150)]

type Verificacion = Annotated[
    str,
    StringConstraints(max_length=12, min_length=8, pattern=r"^[A-Z0-9]+$"),
]

########################################################################################


class PlantillaConstanciaInlineGet(BaseGet):
    codigo: str
    etiqueta: str
    version: int


class PlantillaConstanciaGet(PlantillaConstanciaInlineGet):
    cuerpo: str
    campos_requeridos: list[str]

    firma_nombre: str
    firma_cargo: str
    firma_imagen_url: str

    vigente_desde: date
    vigente_hasta: date | None


class PlantillaConstanciaWrite(DTO):
    etiqueta: Annotated[str, StringConstraints(max_length=120, min_length=1)]

    firma_nombre: Firma = ""
    firma_cargo: Firma = ""
    firma_imagen_url: EnlaceUrl = ""


class PlantillaConstanciaPost(PlantillaConstanciaWrite):
    """
    A new version of a certificate's text; it replaces the one in use.
    """

    codigo: CatalogoCodigo
    cuerpo: Annotated[str, StringConstraints(max_length=20_000, min_length=1)]
    campos_requeridos: Annotated[list[Campo], Field(max_length=30)] = Field(
        default_factory=list,
    )
    vigente_desde: IsoDate


########################################################################################


class ConstanciaGet(BaseGet):
    folio: str
    user: RudiUserInlineGet
    plantilla: PlantillaConstanciaInlineGet
    estado: EstadoConstanciaGet

    codigo_verificacion: str

    nombre_congelado: str
    identificador_congelado: str
    contenido_congelado: dict
    texto_congelado: str

    emitida_at: datetime
    emitida_por_id: UUID
    solicitada_at: datetime | None

    anulada_at: datetime | None
    motivo: MotivoInlineGet | None
    motivo_descripcion: str

    reemplaza_a_id: UUID | None
    documento_url: str


class ConstanciaEmitirPost(DTO):
    user_id: UUID
    plantilla_id: UUID
    participaciones: Annotated[list[RelatedId], Field(max_length=100, min_length=1)]

    reemplaza_a_id: UUID | None = None
    solicitada_at: datetime | None = None


class ConstanciaAnularPost(DTO):
    constancia_id: UUID
    motivo_id: UUID
    motivo_descripcion: MotivoDescripcion = ""


class ConstanciaVerificarPost(DTO):
    folio: Annotated[str, StringConstraints(max_length=30, min_length=1)]
    codigo_verificacion: Verificacion


class ConstanciaVerificadaGet(DTO):
    """
    What the public verification page shows, and nothing else (RF-P-24).

    Enough to tell a real, valid certificate from a forged or annulled one.
    """

    folio: str
    nombre_congelado: str
    texto_congelado: str
    emitida_at: datetime
    valida: bool
    anulada_at: datetime | None


class ConstanciaParticipacionGet(BaseGet):
    participacion_id: UUID
    orden: int


########################################################################################

PlantillaConstanciaPut = build_put_schema(PlantillaConstanciaWrite)
PlantillaConstanciaPatch = build_patch_schema(PlantillaConstanciaPut)

########################################################################################

PlantillaConstanciaFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    PlantillaConstanciaFilterSet,
)
PlantillaConstanciaFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    PlantillaConstanciaFilterSet,
)

ConstanciaFilterQuery = build_filter_query(PaginatedFilterQuery, ConstanciaFilterSet)

ConstanciaParticipacionFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    ConstanciaParticipacionFilterSet,
)
