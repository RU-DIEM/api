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
from rudi_actividades.schemas import ActividadInlineGet
from rudi_auth.schemas.user import RudiUserInlineGet
from rudi_catalogos.schemas.motivo import MotivoInlineGet
from rudi_catalogos.schemas.reconocimiento import TipoReconocimientoInlineGet
from rudi_catalogos.schemas.rol import RolParticipacionInlineGet
from rudi_core.types import EnlaceUrl, MotivoDescripcion
from rudi_estados.enums import InputSourceTypes
from rudi_estados.schemas import (
    EstadoAsignacionMentorGet,
    EstadoInscripcionGet,
    EstadoParticipacionGet,
)
from rudi_participacion.enums import AcompanamientoTypes, ParticipacionOrigenTypes
from rudi_participacion.filtersets import (
    AsignacionMentorFilterSet,
    EquipoFilterSet,
    EquipoMiembroFilterSet,
    InscripcionFilterSet,
    ParticipacionFilterSet,
    ReconocimientoFilterSet,
)
from rudi_profiles.schemas.mentor import MentorProfileInlineGet

########################################################################################

type Observaciones = Annotated[str, StringConstraints(max_length=4_000)]

########################################################################################
# inscripción


class InscripcionGet(BaseGet):
    user: RudiUserInlineGet
    actividad: ActividadInlineGet
    estado: EstadoInscripcionGet

    origen: InputSourceTypes
    creada_por_id: UUID | None

    posicion_espera: int | None
    is_excepcion_cupo: bool

    confirmada_at: datetime | None
    cerrada_at: datetime | None

    motivo: MotivoInlineGet | None
    motivo_descripcion: str

    created_at: datetime


class InscripcionPost(DTO):
    """
    An inscription filed by the administration on someone's behalf.
    """

    user: RelatedId
    actividad: RelatedId

    is_excepcion_cupo: bool = False


class InscribirmePost(DTO):
    actividad_id: UUID


class InscripcionAccionPost(DTO):
    inscripcion_id: UUID


class InscripcionCierrePost(InscripcionAccionPost):
    motivo_id: UUID
    motivo_descripcion: MotivoDescripcion = ""


########################################################################################
# participación


class ParticipacionGet(BaseGet):
    user: RudiUserInlineGet
    actividad: ActividadInlineGet
    inscripcion_id: UUID | None
    equipo_id: UUID | None

    anio: int
    rol: RolParticipacionInlineGet
    estado: EstadoParticipacionGet
    origen: ParticipacionOrigenTypes

    fecha_inicio: date | None
    fecha_fin: date | None

    validada_at: datetime | None
    validada_por_id: UUID | None

    enlace_evidencia: str
    observaciones: str

    anulada_at: datetime | None
    motivo: MotivoInlineGet | None
    motivo_descripcion: str


class ParticipacionWrite(DTO):
    rol: RelatedId
    equipo: RelatedId | None = None

    fecha_inicio: IsoDate | None = None
    fecha_fin: IsoDate | None = None

    enlace_evidencia: EnlaceUrl = ""
    observaciones: Observaciones = ""


class ParticipacionPost(ParticipacionWrite):
    user: RelatedId
    actividad: RelatedId
    inscripcion: RelatedId | None = None

    origen: LaxEnum[ParticipacionOrigenTypes] = ParticipacionOrigenTypes.ADMIN


class ParticipacionValidarPost(DTO):
    participacion_id: UUID
    # the outcome being validated: an `estado_participacion` code (`finalizada`,
    # `no_completo`, `retirada`, ...); the transition catalog decides if it is legal
    desenlace: Annotated[str, StringConstraints(max_length=50, min_length=1)]


class ParticipacionAnularPost(DTO):
    participacion_id: UUID
    motivo_id: UUID
    motivo_descripcion: MotivoDescripcion = ""


########################################################################################
# reconocimiento


class ReconocimientoGet(BaseGet):
    tipo: TipoReconocimientoInlineGet
    descripcion: str
    posicion: int | None
    otorgado_en: date | None
    enlace_evidencia: str
    anulado_at: datetime | None


class ReconocimientoWrite(DTO):
    descripcion: Annotated[str, StringConstraints(max_length=300, min_length=1)]
    posicion: Annotated[int, Field(ge=1, le=1_000)] | None = None
    otorgado_en: IsoDate | None = None
    enlace_evidencia: EnlaceUrl = ""
    anulado_at: IsoDateTime | None = None


class ReconocimientoPost(ReconocimientoWrite):
    tipo: RelatedId


########################################################################################
# equipos


class EquipoGet(BaseGet):
    actividad_id: UUID
    nombre: str
    codigo_union: str
    creado_por_id: UUID | None
    congelado_at: datetime | None


class EquipoWrite(DTO):
    nombre: Annotated[str, StringConstraints(max_length=120, min_length=2)]
    congelado_at: IsoDateTime | None = None


class EquipoPost(DTO):
    actividad: RelatedId
    nombre: Annotated[str, StringConstraints(max_length=120, min_length=2)]


class EquipoMiembroGet(BaseGet):
    user: RudiUserInlineGet
    is_lider: bool
    retirado_at: datetime | None


class EquipoMiembroWrite(DTO):
    is_lider: bool = False
    retirado_at: IsoDateTime | None = None


class EquipoMiembroPost(DTO):
    user: RelatedId
    is_lider: bool = False


class UnirmeEquipoPost(DTO):
    codigo_union: Annotated[str, StringConstraints(max_length=10, min_length=6)]


########################################################################################
# asignación de mentores


class AsignacionMentorGet(BaseGet):
    actividad: ActividadInlineGet
    mentor: MentorProfileInlineGet
    equipo_id: UUID | None

    tipo_acompanamiento: AcompanamientoTypes
    estado: EstadoAsignacionMentorGet

    propuesta_at: datetime
    respondida_at: datetime | None
    finalizada_at: datetime | None

    motivo: MotivoInlineGet | None
    motivo_descripcion: str

    observaciones: str
    enlace_evidencia: str


class AsignacionMentorWrite(DTO):
    tipo_acompanamiento: LaxEnum[AcompanamientoTypes]
    observaciones: Observaciones = ""
    enlace_evidencia: EnlaceUrl = ""


class AsignacionMentorPost(AsignacionMentorWrite):
    actividad: RelatedId
    mentor: RelatedId
    equipo: RelatedId | None = None


class AsignacionAccionPost(DTO):
    asignacion_id: UUID


class AsignacionCierrePost(AsignacionAccionPost):
    motivo_id: UUID
    motivo_descripcion: MotivoDescripcion = ""


########################################################################################

ParticipacionPut = build_put_schema(ParticipacionWrite)
ParticipacionPatch = build_patch_schema(ParticipacionPut)

ReconocimientoPut = build_put_schema(ReconocimientoWrite)
ReconocimientoPatch = build_patch_schema(ReconocimientoPut)

EquipoPut = build_put_schema(EquipoWrite)
EquipoPatch = build_patch_schema(EquipoPut)

EquipoMiembroPut = build_put_schema(EquipoMiembroWrite)
EquipoMiembroPatch = build_patch_schema(EquipoMiembroPut)

AsignacionMentorPut = build_put_schema(AsignacionMentorWrite)
AsignacionMentorPatch = build_patch_schema(AsignacionMentorPut)

########################################################################################

InscripcionFilterQuery = build_filter_query(PaginatedFilterQuery, InscripcionFilterSet)

ParticipacionFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    ParticipacionFilterSet,
)

ReconocimientoFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    ReconocimientoFilterSet,
)

EquipoFilterQuery = build_filter_query(PaginatedFilterQuery, EquipoFilterSet)
EquipoFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, EquipoFilterSet)

EquipoMiembroFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    EquipoMiembroFilterSet,
)

AsignacionMentorFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    AsignacionMentorFilterSet,
)
