from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import (
    route_controllers,
    route_inferred_controller,
)
from rudi_catalogos.controllers import (
    AreaExperienciaDetailController,
    AreaExperienciaListAllController,
    AreaExperienciaListController,
    DepartamentoListAllController,
    MotivoDetailController,
    MotivoListAllController,
    MotivoListController,
    MunicipioListAllController,
    ParametroDetailController,
    ParametroListAllController,
    PlantillaMensajeDetailController,
    PlantillaMensajeListAllController,
    PlantillaMensajeListController,
    RolParticipacionDetailController,
    RolParticipacionListAllController,
    RolParticipacionListController,
    TipoActividadDetailController,
    TipoActividadListAllController,
    TipoActividadListController,
    TipoIdentificadorDetailController,
    TipoIdentificadorListAllController,
    TipoIdentificadorListController,
    TipoMentorDetailController,
    TipoMentorListAllController,
    TipoMentorListController,
    TipoReconocimientoDetailController,
    TipoReconocimientoListAllController,
    TipoReconocimientoListController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["catalogos"],
    urls=(
        *route_controllers(
            AreaExperienciaDetailController,
            AreaExperienciaListAllController,
            AreaExperienciaListController,
            MotivoDetailController,
            MotivoListAllController,
            MotivoListController,
            ParametroDetailController,
            ParametroListAllController,
            PlantillaMensajeDetailController,
            PlantillaMensajeListAllController,
            PlantillaMensajeListController,
            RolParticipacionDetailController,
            RolParticipacionListAllController,
            RolParticipacionListController,
            TipoActividadDetailController,
            TipoActividadListAllController,
            TipoActividadListController,
            TipoIdentificadorDetailController,
            TipoIdentificadorListAllController,
            TipoIdentificadorListController,
            TipoMentorDetailController,
            TipoMentorListAllController,
            TipoMentorListController,
            TipoReconocimientoDetailController,
            TipoReconocimientoListAllController,
            TipoReconocimientoListController,
            prefix="catalogos",
        ),
        route_inferred_controller(
            ctrl=DepartamentoListAllController,
            prefix="catalogos",
        ),
        route_inferred_controller(
            ctrl=MunicipioListAllController,
            prefix="catalogos",
        ),
    ),
)
