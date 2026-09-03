from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controller
from rudi_estados.controllers import (
    EstadoActividadDetailController,
    EstadoActividadListAllController,
    EstadoAsignacionMentorDetailController,
    EstadoAsignacionMentorListAllController,
    EstadoConsentimientoDetailController,
    EstadoConsentimientoListAllController,
    EstadoConstanciaDetailController,
    EstadoConstanciaListAllController,
    EstadoInscripcionDetailController,
    EstadoInscripcionListAllController,
    EstadoParticipacionDetailController,
    EstadoParticipacionListAllController,
    EstadoPropuestaDetailController,
    EstadoPropuestaListAllController,
    EstadoRudiUserDetailController,
    EstadoRudiUserListAllController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["estados"],
    urls=(
        route_controller(
            ctrl=EstadoActividadDetailController,
            endpoint="estados/actividad",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoActividadListAllController,
            endpoint="estados/actividad/all",
        ),
        route_controller(
            ctrl=EstadoAsignacionMentorDetailController,
            endpoint="estados/asignacion-mentor",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoAsignacionMentorListAllController,
            endpoint="estados/asignacion-mentor/all",
        ),
        route_controller(
            ctrl=EstadoConsentimientoDetailController,
            endpoint="estados/consentimiento",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoConsentimientoListAllController,
            endpoint="estados/consentimiento/all",
        ),
        route_controller(
            ctrl=EstadoConstanciaDetailController,
            endpoint="estados/constancia",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoConstanciaListAllController,
            endpoint="estados/constancia/all",
        ),
        route_controller(
            ctrl=EstadoInscripcionDetailController,
            endpoint="estados/inscripcion",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoInscripcionListAllController,
            endpoint="estados/inscripcion/all",
        ),
        route_controller(
            ctrl=EstadoParticipacionDetailController,
            endpoint="estados/participacion",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoParticipacionListAllController,
            endpoint="estados/participacion/all",
        ),
        route_controller(
            ctrl=EstadoPropuestaDetailController,
            endpoint="estados/propuesta",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoPropuestaListAllController,
            endpoint="estados/propuesta/all",
        ),
        route_controller(
            ctrl=EstadoRudiUserDetailController,
            endpoint="estados/user",
            instance_param=("uuid", "id"),
        ),
        route_controller(
            ctrl=EstadoRudiUserListAllController,
            endpoint="estados/user/all",
        ),
    ),
)
