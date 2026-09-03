from api_core.schemas.factories import build_filter_query
from api_core.schemas.filters import UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet
from rudi_estados.filtersets import (
    EstadoActividadFilterSet,
    EstadoAsignacionMentorFilterSet,
    EstadoConsentimientoFilterSet,
    EstadoConstanciaFilterSet,
    EstadoInscripcionFilterSet,
    EstadoParticipacionFilterSet,
    EstadoPropuestaFilterSet,
    EstadoRudiUserFilterSet,
)

########################################################################################


class RudiEstadoGet(BaseGet):
    codigo: str
    etiqueta: str
    descripcion: str
    initial: bool
    terminal: bool
    is_active: bool


########################################################################################


class RudiSourceAwareEstadoGet(RudiEstadoGet):
    source: str


########################################################################################


class EstadoActividadGet(RudiEstadoGet):
    public: bool
    allow_inscripcion: bool
    allow_validacion: bool


class EstadoAsignacionMentorGet(RudiEstadoGet):
    public: bool
    vigente: bool
    require_motivo: bool


class EstadoConsentimientoGet(RudiSourceAwareEstadoGet):
    allow_reporte: bool
    allow_comunicacion: bool


class EstadoConstanciaGet(RudiEstadoGet):
    valid: bool
    require_motivo: bool


class EstadoInscripcionGet(RudiSourceAwareEstadoGet):
    consume_cupo: bool
    allow_participacion: bool


class EstadoParticipacionGet(RudiEstadoGet):
    efectiva: bool
    allow_constancia: bool
    allow_puntos: bool


class EstadoPropuestaGet(RudiEstadoGet):
    vigente: bool
    allow_portafolio: bool


class EstadoRudiUserGet(RudiEstadoGet):
    allow_ingreso: bool
    allow_inscripcion: bool
    visible_reportes: bool
    require_motivo: bool


########################################################################################

EstadoActividadFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoActividadFilterSet,
)

EstadoAsignacionMentorFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoAsignacionMentorFilterSet,
)

EstadoConsentimientoFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoConsentimientoFilterSet,
)

EstadoConstanciaFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoConstanciaFilterSet,
)

EstadoInscripcionFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoInscripcionFilterSet,
)

EstadoParticipacionFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoParticipacionFilterSet,
)

EstadoPropuestaFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoPropuestaFilterSet,
)

EstadoRudiUserFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    EstadoRudiUserFilterSet,
)
