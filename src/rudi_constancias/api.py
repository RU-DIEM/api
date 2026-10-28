from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from rudi_constancias.controllers import (
    AnularConstanciaController,
    ConstanciaDetailController,
    ConstanciaListController,
    ConstanciaParticipacionListController,
    EmitirConstanciaController,
    MisConstanciasController,
    PlantillaConstanciaDetailController,
    PlantillaConstanciaListAllController,
    PlantillaConstanciaListController,
    VerificarConstanciaController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["constancias"],
    urls=sort_urls(
        route_controllers(
            AnularConstanciaController,
            ConstanciaDetailController,
            ConstanciaListController,
            ConstanciaParticipacionListController,
            EmitirConstanciaController,
            MisConstanciasController,
            PlantillaConstanciaDetailController,
            PlantillaConstanciaListAllController,
            PlantillaConstanciaListController,
            VerificarConstanciaController,
            prefix="constancias",
        ),
    ),
)
