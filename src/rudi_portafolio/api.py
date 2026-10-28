from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from rudi_portafolio.controllers import (
    CerrarPropuestaController,
    PausarPropuestaController,
    PropuestaActividadDetailController,
    PropuestaActividadListController,
    PropuestaDetailController,
    PropuestaIntegranteDetailController,
    PropuestaIntegranteListController,
    PropuestaListAllController,
    PropuestaListController,
    ReanudarPropuestaController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["portafolio"],
    urls=sort_urls(
        route_controllers(
            CerrarPropuestaController,
            PausarPropuestaController,
            PropuestaActividadDetailController,
            PropuestaActividadListController,
            PropuestaDetailController,
            PropuestaIntegranteDetailController,
            PropuestaIntegranteListController,
            PropuestaListAllController,
            PropuestaListController,
            ReanudarPropuestaController,
            prefix="portafolio",
        ),
    ),
)
