from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from api_media.controllers import ApiMediaDetailController, ApiMediaListController

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["media"],
    urls=sort_urls(route_controllers(ApiMediaDetailController, ApiMediaListController)),
)
