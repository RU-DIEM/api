from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controllers, sort_urls
from rudi_participacion.controllers import (
    AceptarMentoriaController,
    AnularParticipacionController,
    AsignacionMentorDetailController,
    AsignacionMentorListController,
    CancelarInscripcionController,
    CancelarMentoriaController,
    ConfirmarInscripcionController,
    DeclinarMentoriaController,
    EquipoDetailController,
    EquipoListAllController,
    EquipoListController,
    EquipoMiembroDetailController,
    EquipoMiembroListController,
    FinalizarMentoriaController,
    InscribirmeController,
    InscripcionDetailController,
    InscripcionListController,
    ParticipacionDetailController,
    ParticipacionListController,
    RechazarInscripcionController,
    ReconocimientoDetailController,
    ReconocimientoListController,
    UnirmeEquipoController,
    ValidarParticipacionController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["participacion"],
    urls=sort_urls(
        route_controllers(
            AceptarMentoriaController,
            AnularParticipacionController,
            AsignacionMentorDetailController,
            AsignacionMentorListController,
            CancelarInscripcionController,
            CancelarMentoriaController,
            ConfirmarInscripcionController,
            DeclinarMentoriaController,
            EquipoDetailController,
            EquipoListAllController,
            EquipoListController,
            EquipoMiembroDetailController,
            EquipoMiembroListController,
            FinalizarMentoriaController,
            InscribirmeController,
            InscripcionDetailController,
            InscripcionListController,
            ParticipacionDetailController,
            ParticipacionListController,
            RechazarInscripcionController,
            ReconocimientoDetailController,
            ReconocimientoListController,
            UnirmeEquipoController,
            ValidarParticipacionController,
            prefix="participacion",
        ),
    ),
)
