from datetime import datetime
from uuid import UUID

from api_core.schemas.factories import build_filter_query
from api_core.schemas.filters import PaginatedFilterQuery
from api_core.schemas.get import BaseGet
from rudi_auth.enums import AccesoDatoTypes
from rudi_auth.filtersets.acceso import AccesoDatoPersonalFilterSet

########################################################################################


class AccesoDatoPersonalGet(BaseGet):
    tipo: AccesoDatoTypes
    accedido_por_id: UUID
    recurso: str
    detalle: str
    created_at: datetime


########################################################################################

AccesoDatoPersonalFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    AccesoDatoPersonalFilterSet,
)
