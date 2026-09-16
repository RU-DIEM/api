from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controller, route_controllers
from rudi_profiles.controllers import (
    CarreraDetailController,
    CarreraListAllController,
    CarreraListController,
    DocenteProfileDetailController,
    DocenteProfileListAllController,
    DocenteProfileListController,
    EstudianteCarreraDetailController,
    EstudianteCarreraListController,
    EstudianteProfileDetailController,
    EstudianteProfileListAllController,
    EstudianteProfileListController,
    ExternoProfileDetailController,
    ExternoProfileListAllController,
    ExternoProfileListController,
    FacultadDetailController,
    FacultadListAllController,
    FacultadListController,
    InstitucionDetailController,
    InstitucionListAllController,
    InstitucionListController,
    InstitucionNormalizarController,
    MentorAreaExperienciaDetailController,
    MentorAreaExperienciaListController,
    MentorCertificacionDetailController,
    MentorCertificacionListController,
    MentorConfirmarController,
    MentorProfileDetailController,
    MentorProfileListAllController,
    MentorProfileListController,
)

if TYPE_CHECKING:
    from typing import Final

    from api_core.controllers.base import BaseController

########################################################################################


def route_profile(
    detail: type[BaseController],
    listing: type[BaseController],
    listing_all: type[BaseController],
    prefix: str,
) -> tuple:
    return (
        route_controller(ctrl=listing, endpoint=prefix, suffix="list"),
        route_controller(
            ctrl=detail,
            endpoint=prefix,
            instance_param=("uuid", "id"),
            suffix="detail",
        ),
        route_controller(ctrl=listing_all, endpoint=f"{prefix}/all"),
    )


########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["perfiles"],
    urls=(
        *route_controllers(
            CarreraDetailController,
            CarreraListAllController,
            CarreraListController,
            FacultadDetailController,
            FacultadListAllController,
            FacultadListController,
            InstitucionDetailController,
            InstitucionListAllController,
            InstitucionListController,
            prefix="catalogos",
        ),
        route_controller(
            ctrl=InstitucionNormalizarController,
            endpoint="catalogos/institucion",
            instance_param=("uuid", "id"),
            suffix="normalizar",
            tail="normalizar",
        ),
        *route_profile(
            detail=DocenteProfileDetailController,
            listing=DocenteProfileListController,
            listing_all=DocenteProfileListAllController,
            prefix="perfiles/docente",
        ),
        *route_profile(
            detail=EstudianteProfileDetailController,
            listing=EstudianteProfileListController,
            listing_all=EstudianteProfileListAllController,
            prefix="perfiles/estudiante",
        ),
        route_controller(
            ctrl=EstudianteCarreraListController,
            endpoint="perfiles/estudiante",
            instance_param=("uuid", "profile_id"),
            suffix="carreras-list",
            tail="carreras",
        ),
        route_controller(
            ctrl=EstudianteCarreraDetailController,
            endpoint="perfiles/estudiante",
            instance_param=("uuid", "profile_id"),
            related_param=("uuid", "id"),
            suffix="carreras-detail",
            tail="carreras",
        ),
        *route_profile(
            detail=ExternoProfileDetailController,
            listing=ExternoProfileListController,
            listing_all=ExternoProfileListAllController,
            prefix="perfiles/externo",
        ),
        *route_profile(
            detail=MentorProfileDetailController,
            listing=MentorProfileListController,
            listing_all=MentorProfileListAllController,
            prefix="perfiles/mentor",
        ),
        route_controller(
            ctrl=MentorConfirmarController,
            endpoint="perfiles/mentor",
            instance_param=("uuid", "id"),
            suffix="confirmar",
            tail="confirmar",
        ),
        route_controller(
            ctrl=MentorAreaExperienciaListController,
            endpoint="perfiles/mentor",
            instance_param=("uuid", "profile_id"),
            suffix="areas-list",
            tail="areas",
        ),
        route_controller(
            ctrl=MentorAreaExperienciaDetailController,
            endpoint="perfiles/mentor",
            instance_param=("uuid", "profile_id"),
            related_param=("uuid", "id"),
            suffix="areas-detail",
            tail="areas",
        ),
        route_controller(
            ctrl=MentorCertificacionListController,
            endpoint="perfiles/mentor",
            instance_param=("uuid", "profile_id"),
            suffix="certificaciones-list",
            tail="certificaciones",
        ),
        route_controller(
            ctrl=MentorCertificacionDetailController,
            endpoint="perfiles/mentor",
            instance_param=("uuid", "profile_id"),
            related_param=("uuid", "id"),
            suffix="certificaciones-detail",
            tail="certificaciones",
        ),
    ),
)
