from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from rudi_puntos.controllers import (
    MiSaldoController,
    MisMovimientosController,
    MovimientoPuntoDetailController,
    MovimientoPuntoListController,
    ReglaPuntuacionDetailController,
    ReglaPuntuacionListAllController,
    ReglaPuntuacionListController,
    RevertirMovimientoController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["puntos"],
    urls=sort_urls(
        route_controllers(
            MiSaldoController,
            MisMovimientosController,
            MovimientoPuntoDetailController,
            MovimientoPuntoListController,
            ReglaPuntuacionDetailController,
            ReglaPuntuacionListAllController,
            ReglaPuntuacionListController,
            RevertirMovimientoController,
            prefix="puntos",
        ),
    ),
)
