from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from rudi_actividades.controllers import (
    ActividadDetailController,
    ActividadListAllController,
    ActividadListController,
    ActividadResponsableDetailController,
    ActividadResponsableListController,
    CancelarActividadController,
    FinalizarActividadController,
    IniciarActividadController,
    ProgramaDetailController,
    ProgramaListAllController,
    ProgramaListController,
    PublicarActividadController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["actividades"],
    urls=sort_urls(
        route_controllers(
            ActividadDetailController,
            ActividadListAllController,
            ActividadListController,
            ActividadResponsableDetailController,
            ActividadResponsableListController,
            CancelarActividadController,
            FinalizarActividadController,
            IniciarActividadController,
            ProgramaDetailController,
            ProgramaListAllController,
            ProgramaListController,
            PublicarActividadController,
            prefix="actividades",
        ),
    ),
)
