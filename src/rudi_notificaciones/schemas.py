from datetime import datetime
from uuid import UUID

from api_core.schemas.factories import build_filter_query
from api_core.schemas.filters import PaginatedFilterQuery
from api_core.schemas.get import BaseGet
from rudi_catalogos.schemas.plantilla import PlantillaMensajeInlineGet
from rudi_notificaciones.filtersets import NotificacionFilterSet

########################################################################################


class NotificacionGet(BaseGet):
    plantilla: PlantillaMensajeInlineGet
    cuenta_id: UUID | None

    destinatario: str
    asunto: str
    cuerpo: str

    programada_para: datetime
    intentos: int
    ultimo_error: str

    enviada_at: datetime | None
    descartada_at: datetime | None

    created_at: datetime


########################################################################################

NotificacionFilterQuery = build_filter_query(
    PaginatedFilterQuery, NotificacionFilterSet
)
