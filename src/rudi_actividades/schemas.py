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
from api_core.schemas.get import BaseGet, IsoDate, IsoDateTime, LaxEnum, RelatedId
from rudi_actividades.enums import ModalidadTypes, ResponsableRolTypes
from rudi_actividades.filtersets import (
    ActividadFilterSet,
    ActividadResponsableFilterSet,
    ProgramaFilterSet,
)
from rudi_auth.schemas.user import RudiUserInlineGet
from rudi_catalogos.schemas.actividad import TipoActividadInlineGet
from rudi_catalogos.schemas.base import CatalogoCodigo
from rudi_catalogos.schemas.motivo import MotivoInlineGet
from rudi_core.types import Anio, EnlaceUrl, MotivoDescripcion, Puntos, SinNul
from rudi_estados.schemas import EstadoActividadGet

########################################################################################

type Nombre = Annotated[str, SinNul, StringConstraints(max_length=200, min_length=2)]

type TamanoEquipo = Annotated[int, Field(ge=1, le=100)]

type Cupo = Annotated[int, Field(ge=1, le=30_000)]

########################################################################################


class ProgramaInlineGet(BaseGet):
    codigo: str
    nombre: str
    nombre_corto: str


class ProgramaGet(ProgramaInlineGet):
    descripcion: str
    tipo_actividad: TipoActividadInlineGet | None
    is_institucional: bool
    is_active: bool


class ProgramaWrite(DTO):
    nombre: Nombre
    nombre_corto: Annotated[str, SinNul, StringConstraints(max_length=60)] = ""
    descripcion: str = ""

    tipo_actividad: RelatedId | None = None

    is_institucional: bool = True
    is_active: bool = True


class ProgramaPost(ProgramaWrite):
    codigo: CatalogoCodigo


########################################################################################


class ActividadInlineGet(BaseGet):
    nombre: str
    etiqueta_edicion: str
    anio: int
    fecha_inicio: date
    estado: EstadoActividadGet


class ActividadGet(ActividadInlineGet):
    programa: ProgramaInlineGet | None
    tipo_actividad: TipoActividadInlineGet

    descripcion: str

    modalidad: ModalidadTypes
    lugar: str

    fecha_fin: date | None

    inscripcion_abre_at: datetime | None
    inscripcion_cierra_at: datetime | None

    cupo: int | None
    inscritos_activos: int

    admite_lista_espera: bool
    admite_equipos: bool

    equipo_min: int | None
    equipo_max: int | None

    puntos_base: int | None

    publicada_at: datetime | None
    cancelada_at: datetime | None

    motivo: MotivoInlineGet | None
    motivo_descripcion: str

    enlace_evidencia: str


class ActividadWrite(DTO):
    programa: RelatedId | None = None
    tipo_actividad: RelatedId

    nombre: Nombre
    etiqueta_edicion: Annotated[str, SinNul, StringConstraints(max_length=60)] = ""
    descripcion: str = ""

    modalidad: LaxEnum[ModalidadTypes] = ModalidadTypes.PRESENCIAL
    lugar: Annotated[str, SinNul, StringConstraints(max_length=200)] = ""

    anio: Anio

    fecha_inicio: IsoDate
    fecha_fin: IsoDate | None = None

    inscripcion_abre_at: IsoDateTime | None = None
    inscripcion_cierra_at: IsoDateTime | None = None

    cupo: Cupo | None = None

    admite_lista_espera: bool = True
    admite_equipos: bool = False

    equipo_min: TamanoEquipo | None = None
    equipo_max: TamanoEquipo | None = None

    puntos_base: Puntos | None = None

    enlace_evidencia: EnlaceUrl = ""


class ActividadPost(ActividadWrite):
    pass


########################################################################################


class ActividadAccionPost(DTO):
    actividad_id: UUID


class ActividadCancelarPost(ActividadAccionPost):
    motivo_id: UUID
    motivo_descripcion: MotivoDescripcion = ""


########################################################################################


class ActividadResponsableGet(BaseGet):
    user: RudiUserInlineGet
    rol: ResponsableRolTypes
    is_public: bool
    retirado_at: datetime | None


class ActividadResponsableWrite(DTO):
    rol: LaxEnum[ResponsableRolTypes]
    is_public: bool = True
    retirado_at: IsoDateTime | None = None


class ActividadResponsablePost(ActividadResponsableWrite):
    user: RelatedId


########################################################################################

ProgramaPut = build_put_schema(ProgramaWrite)
ProgramaPatch = build_patch_schema(ProgramaPut)

ActividadPut = build_put_schema(ActividadWrite)
ActividadPatch = build_patch_schema(ActividadPut)

ActividadResponsablePut = build_put_schema(ActividadResponsableWrite)
ActividadResponsablePatch = build_patch_schema(ActividadResponsablePut)

########################################################################################

ProgramaFilterQuery = build_filter_query(PaginatedFilterQuery, ProgramaFilterSet)
ProgramaFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, ProgramaFilterSet)

ActividadFilterQuery = build_filter_query(PaginatedFilterQuery, ActividadFilterSet)
ActividadFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, ActividadFilterSet)

ActividadResponsableFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    ActividadResponsableFilterSet,
)
