from typing import TYPE_CHECKING

from dmr.routing import Router

from api_core.controllers.routers import route_controller
from rudi_auth.controllers import (
    ConsentimientoDatosDetailController,
    ConsentimientoRetiroController,
    EmailConfirmController,
    EmailResendController,
    IdentificadorUserDetailController,
    IdentificadorUserListController,
    InviteAcceptController,
    MeConsentimientoController,
    MeDetailController,
    MeIdentificadoresController,
    PasswordConfirmController,
    PasswordResetController,
    PoliticaPrivacidadDetailController,
    PoliticaPrivacidadListAllController,
    PoliticaPrivacidadListController,
    PoliticaVigenteController,
    RudiInviteController,
    RudiRegisterController,
    RudiUserDetailController,
    RudiUserListAllController,
    RudiUserListController,
)

if TYPE_CHECKING:
    from typing import Final

########################################################################################

router: Final[Router] = Router(
    prefix="",
    tags=["rudi-auth"],
    urls=(
        route_controller(ctrl=MeDetailController, endpoint="me"),
        route_controller(
            ctrl=MeConsentimientoController,
            endpoint="me/consentimiento",
        ),
        route_controller(
            ctrl=MeIdentificadoresController,
            endpoint="me/identificadores",
        ),
        route_controller(
            ctrl=PoliticaPrivacidadListController,
            endpoint="politicas",
            suffix="list",
        ),
        route_controller(
            ctrl=PoliticaPrivacidadDetailController,
            endpoint="politicas",
            instance_param=("uuid", "id"),
            suffix="detail",
        ),
        route_controller(
            ctrl=PoliticaPrivacidadListAllController,
            endpoint="politicas/all",
        ),
        route_controller(ctrl=PoliticaVigenteController, endpoint="politicas/vigente"),
        route_controller(ctrl=RudiRegisterController, endpoint="registro"),
        route_controller(ctrl=EmailConfirmController, endpoint="registro/confirmar"),
        route_controller(ctrl=RudiInviteController, endpoint="registro/invitacion"),
        route_controller(
            ctrl=InviteAcceptController,
            endpoint="registro/invitacion/aceptar",
        ),
        route_controller(ctrl=PasswordResetController, endpoint="registro/recuperar"),
        route_controller(
            ctrl=PasswordConfirmController,
            endpoint="registro/recuperar/confirmar",
        ),
        route_controller(ctrl=EmailResendController, endpoint="registro/reenviar"),
        route_controller(
            ctrl=RudiUserListController,
            endpoint="usuarios",
            suffix="list",
        ),
        route_controller(
            ctrl=RudiUserDetailController,
            endpoint="usuarios",
            instance_param=("uuid", "id"),
            suffix="detail",
        ),
        route_controller(ctrl=RudiUserListAllController, endpoint="usuarios/all"),
        route_controller(
            ctrl=ConsentimientoDatosDetailController,
            endpoint="usuarios",
            instance_param=("uuid", "user_id"),
            suffix="consentimiento-detail",
            tail="consentimiento",
        ),
        route_controller(
            ctrl=ConsentimientoRetiroController,
            endpoint="usuarios",
            instance_param=("uuid", "user_id"),
            suffix="consentimiento-retiro",
            tail="consentimiento/retiro",
        ),
        route_controller(
            ctrl=IdentificadorUserListController,
            endpoint="usuarios",
            instance_param=("uuid", "user_id"),
            suffix="identificadores-list",
            tail="identificadores",
        ),
        route_controller(
            ctrl=IdentificadorUserDetailController,
            endpoint="usuarios",
            instance_param=("uuid", "user_id"),
            related_param=("uuid", "id"),
            suffix="identificadores-detail",
            tail="identificadores",
        ),
    ),
)
