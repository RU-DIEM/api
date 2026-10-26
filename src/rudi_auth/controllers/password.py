from http import HTTPStatus

from django.views.decorators.debug import sensitive_variables
from dmr import Body, modify

from api_core.controllers.mixins import PublicControllerMixin, StrictThrottlingMixin
from rudi_auth.schemas.password import PasswordConfirmPost, PasswordResetPost
from rudi_auth.services.password import accept_invite, confirm_reset, request_reset

from .base import RudiAuthController

########################################################################################


class PasswordResetController(
    PublicControllerMixin,
    StrictThrottlingMixin,
    RudiAuthController,
):
    @sensitive_variables()
    @modify(status_code=HTTPStatus.ACCEPTED)
    async def post(self, parsed_body: Body[PasswordResetPost]) -> None:  # ruff: ignore[no-self-use]
        await request_reset(parsed_body.email)


########################################################################################


class PasswordConfirmController(
    PublicControllerMixin,
    StrictThrottlingMixin,
    RudiAuthController,
):
    @sensitive_variables()
    @modify(status_code=HTTPStatus.NO_CONTENT)
    async def post(self, parsed_body: Body[PasswordConfirmPost]) -> None:  # ruff: ignore[no-self-use]
        await confirm_reset(parsed_body)


########################################################################################


class InviteAcceptController(
    PublicControllerMixin,
    StrictThrottlingMixin,
    RudiAuthController,
):
    @sensitive_variables()
    @modify(status_code=HTTPStatus.NO_CONTENT)
    async def post(self, parsed_body: Body[PasswordConfirmPost]) -> None:  # ruff: ignore[no-self-use]
        await accept_invite(parsed_body)
