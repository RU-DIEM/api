from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from django.views.decorators.debug import sensitive_variables
from dmr import Body, modify

from api_auth.services.permissions import T_ADD_PERM
from api_core.controllers.mixins import PublicControllerMixin, StrictThrottlingMixin
from api_core.controllers.models import ModelController
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.services.operations import CreateOperation
from rudi_auth.models import RudiUser
from rudi_auth.schemas.register import RudiInvitePost, RudiRegisterGet, RudiRegisterPost
from rudi_auth.services.register import (
    RudiInviteCreateOperation,
    RudiUserCreateOperation,
)

from .base import RudiAuthController

########################################################################################


class RudiRegisterController(
    PublicControllerMixin,
    StrictThrottlingMixin,
    RudiAuthController,
    ModelController[
        CustomPydanticFastSerializer,
        RudiUser,
        RudiRegisterGet,
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = RudiUserCreateOperation

    @sensitive_variables()
    @modify(status_code=HTTPStatus.CREATED)
    async def post(self, parsed_body: Body[RudiRegisterPost]) -> RudiRegisterGet:
        return await self.build_operation(self.create_operation).run(parsed_body)


########################################################################################


class RudiInviteController(
    RudiAuthController,
    ModelController[
        CustomPydanticFastSerializer,
        RudiUser,
        RudiRegisterGet,
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = RudiInviteCreateOperation

    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_ADD_PERM,),
    }

    @modify(status_code=HTTPStatus.CREATED)
    async def post(self, parsed_body: Body[RudiInvitePost]) -> RudiRegisterGet:
        return await self.build_operation(self.create_operation).run(parsed_body)
