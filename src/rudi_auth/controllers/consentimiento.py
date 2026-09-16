from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from dmr import Body, Path, modify

from api_auth.services.permissions import T_CHANGE_PERM, T_VIEW_PERM
from api_core.controllers.models import ModelController
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.services.operations import FlatRetrieveOperation, RetrieveOperation
from rudi_auth.models import ConsentimientoDatos
from rudi_auth.schemas.consentimiento import (
    ConsentimientoDatosGet,
    ConsentimientoRetiroPost,
)
from rudi_auth.services.consentimiento import retirar_consentimiento
from rudi_core.schemas import UserPath

########################################################################################


class ConsentimientoDatosDetailController(
    ModelController[
        CustomPydanticFastSerializer,
        ConsentimientoDatos,
        ConsentimientoDatosGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.GET: (T_VIEW_PERM,),
    }

    retrieve_operation: ClassVar[type[RetrieveOperation]] = FlatRetrieveOperation

    async def get(self, parsed_path: Path[UserPath]) -> ConsentimientoDatosGet:
        return await self.build_operation(self.retrieve_operation).run(
            path=parsed_path,  # ty: ignore[invalid-argument-type]
        )


########################################################################################


class ConsentimientoRetiroController(
    ModelController[
        CustomPydanticFastSerializer,
        ConsentimientoDatos,
        ConsentimientoDatosGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_CHANGE_PERM,),
    }

    @modify(status_code=HTTPStatus.OK)
    async def post(
        self,
        parsed_body: Body[ConsentimientoRetiroPost],
        parsed_path: Path[UserPath],
    ) -> ConsentimientoDatosGet:
        await retirar_consentimiento(data=parsed_body, user_id=parsed_path.user_id)

        return await self.build_operation(FlatRetrieveOperation).run(
            path=parsed_path,  # ty: ignore[invalid-argument-type]
        )
