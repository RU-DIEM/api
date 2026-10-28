from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from rudi_analitica.controllers import (
    CerrarPeriodoController,
    IndicadorPeriodoDetailController,
    IndicadorPeriodoListAllController,
    IndicadorPeriodoListController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["analitica"],
    urls=sort_urls(
        route_controllers(
            CerrarPeriodoController,
            IndicadorPeriodoDetailController,
            IndicadorPeriodoListAllController,
            IndicadorPeriodoListController,
            prefix="analitica",
        ),
    ),
)
