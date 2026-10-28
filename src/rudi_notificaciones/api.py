from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from rudi_notificaciones.controllers import (
    NotificacionDetailController,
    NotificacionListController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["notificaciones"],
    urls=sort_urls(
        route_controllers(
            NotificacionDetailController,
            NotificacionListController,
            prefix="notificaciones",
        ),
    ),
)
