from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import build_filter_query
from api_core.schemas.filters import PaginatedFilterQuery
from api_core.schemas.get import BaseGet, RelatedId
from rudi_auth.enums import ConsentimientoCanalTypes
from rudi_auth.filtersets.consentimiento import ConsentimientoDatosFilterSet
from rudi_estados.schemas import EstadoConsentimientoGet

from .politica import PoliticaPrivacidadInlineGet

########################################################################################

type RetiroDescripcion = Annotated[str, StringConstraints(max_length=500)]

########################################################################################


class ConsentimientoDatosGet(BaseGet):
    politica: PoliticaPrivacidadInlineGet
    estado: EstadoConsentimientoGet

    canal: ConsentimientoCanalTypes

    otorgado_at: datetime | None
    retirado_at: datetime | None

    evidencia_url: str


########################################################################################


class ConsentimientoRetiroPost(DTO):
    motivo: RelatedId
    descripcion: RetiroDescripcion = ""


########################################################################################

ConsentimientoDatosFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    ConsentimientoDatosFilterSet,
)
