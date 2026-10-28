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
from api_core.schemas.get import BaseGet, IsoDate, LaxEnum, RelatedId
from rudi_actividades.schemas import ActividadInlineGet
from rudi_auth.schemas.user import RudiUserInlineGet
from rudi_catalogos.enums import (
    MRL,
    ODS,
    TRL,
    AmbitosAplicacion,
    EtapasDesarrollo,
    NivelesFormalizacion,
    SectoresAplicacion,
    TiposInnovacion,
    VerticalesInnovacion,
)
from rudi_catalogos.schemas.motivo import MotivoInlineGet
from rudi_core.types import EnlaceUrl, MotivoDescripcion, SinNul
from rudi_estados.schemas import EstadoPropuestaGet
from rudi_portafolio.enums import IntegranteRolTypes, PropuestaActividadRolTypes
from rudi_portafolio.filtersets import (
    PropuestaActividadFilterSet,
    PropuestaFilterSet,
    PropuestaIntegranteFilterSet,
)

########################################################################################

type Texto = Annotated[str, SinNul, StringConstraints(max_length=8_000)]

########################################################################################


class PropuestaInlineGet(BaseGet):
    codigo: str
    nombre: str
    anio_ingreso: int
    estado: EstadoPropuestaGet


class PropuestaGet(PropuestaInlineGet):
    actividad_origen: ActividadInlineGet | None

    problema: str
    solucion: str
    usuario_beneficiario: str
    cliente_adoptante: str

    nivel_formalizacion: NivelesFormalizacion
    etapa_desarrollo: EtapasDesarrollo
    ambito_aplicacion: AmbitosAplicacion
    sector_aplicacion: SectoresAplicacion
    vertical: VerticalesInnovacion
    tipo_innovacion: TiposInnovacion
    trl: TRL
    mrl: MRL
    ods_principal: ODS
    ods_secundario: ODS

    enlace_expediente: str

    clasificada_at: datetime | None
    cerrada_at: datetime | None

    motivo: MotivoInlineGet | None
    motivo_descripcion: str


class PropuestaWrite(DTO):
    nombre: Annotated[str, SinNul, StringConstraints(max_length=200, min_length=2)]

    problema: Texto = ""
    solucion: Texto = ""
    usuario_beneficiario: Texto = ""
    cliente_adoptante: Texto = ""

    nivel_formalizacion: LaxEnum[NivelesFormalizacion]
    etapa_desarrollo: LaxEnum[EtapasDesarrollo] = EtapasDesarrollo.P_D
    ambito_aplicacion: LaxEnum[AmbitosAplicacion]
    sector_aplicacion: LaxEnum[SectoresAplicacion] = SectoresAplicacion.P_D
    vertical: LaxEnum[VerticalesInnovacion] = VerticalesInnovacion.P_D
    tipo_innovacion: LaxEnum[TiposInnovacion] = TiposInnovacion.P_D
    trl: LaxEnum[TRL] = TRL.P_D
    mrl: LaxEnum[MRL] = MRL.P_D
    ods_principal: LaxEnum[ODS] = ODS.P_D
    ods_secundario: LaxEnum[ODS] = ODS.N_A

    enlace_expediente: EnlaceUrl = ""


class PropuestaPost(PropuestaWrite):
    anio_ingreso: Annotated[int, Field(ge=2015, le=2100)]
    actividad_origen: RelatedId | None = None


class PropuestaAccionPost(DTO):
    propuesta_id: UUID


class PropuestaCerrarPost(PropuestaAccionPost):
    # the closing outcome: a terminal `estado_propuesta` code
    desenlace: Annotated[str, SinNul, StringConstraints(max_length=50, min_length=1)]
    motivo_id: UUID
    motivo_descripcion: MotivoDescripcion = ""


########################################################################################


class PropuestaIntegranteGet(BaseGet):
    user: RudiUserInlineGet
    rol: IntegranteRolTypes
    desde: date
    hasta: date | None
    is_contacto: bool


class PropuestaIntegranteWrite(DTO):
    rol: LaxEnum[IntegranteRolTypes]
    hasta: IsoDate | None = None
    is_contacto: bool = False


class PropuestaIntegrantePost(PropuestaIntegranteWrite):
    user: RelatedId
    desde: IsoDate


class PropuestaActividadGet(BaseGet):
    actividad: ActividadInlineGet
    rol: PropuestaActividadRolTypes
    resultado: str
    enlace_evidencia: str


class PropuestaActividadWrite(DTO):
    resultado: Annotated[str, SinNul, StringConstraints(max_length=200)] = ""
    enlace_evidencia: EnlaceUrl = ""


class PropuestaActividadPost(PropuestaActividadWrite):
    actividad: RelatedId
    rol: LaxEnum[PropuestaActividadRolTypes] = PropuestaActividadRolTypes.PARTICIPA


########################################################################################

PropuestaPut = build_put_schema(PropuestaWrite)
PropuestaPatch = build_patch_schema(PropuestaPut)

PropuestaIntegrantePut = build_put_schema(PropuestaIntegranteWrite)
PropuestaIntegrantePatch = build_patch_schema(PropuestaIntegrantePut)

PropuestaActividadPut = build_put_schema(PropuestaActividadWrite)
PropuestaActividadPatch = build_patch_schema(PropuestaActividadPut)

########################################################################################

PropuestaFilterQuery = build_filter_query(PaginatedFilterQuery, PropuestaFilterSet)
PropuestaFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, PropuestaFilterSet)

PropuestaIntegranteFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    PropuestaIntegranteFilterSet,
)

PropuestaActividadFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    PropuestaActividadFilterSet,
)
