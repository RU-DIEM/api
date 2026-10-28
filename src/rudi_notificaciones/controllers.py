from api_core.controllers.models import (
    ModelReadOnlyDetailController,
    ModelReadOnlyListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_notificaciones.filtersets import NotificacionFilterSet
from rudi_notificaciones.models import Notificacion
from rudi_notificaciones.schemas import NotificacionFilterQuery, NotificacionGet

########################################################################################


class NotificacionDetailController(
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        Notificacion,
        NotificacionGet,
    ],
):
    pass


class NotificacionListController(
    ModelReadOnlyListController[
        CustomPydanticFastSerializer,
        Notificacion,
        NotificacionFilterSet,
        NotificacionFilterQuery,
        NotificacionGet,
        Paginated[NotificacionGet],
    ],
):
    pass


########################################################################################

__all__ = (
    "NotificacionDetailController",
    "NotificacionListController",
)
