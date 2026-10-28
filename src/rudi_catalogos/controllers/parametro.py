from typing import ClassVar, override

from dmr import Body, Path

from api_core.controllers.mixins import OpenReadMixin
from api_core.controllers.models import (
    ModelListAllController,
    ModelReadUpdateDetailController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.path import UuidInstancePath
from api_core.services.operations import UpdateOperation
from rudi_catalogos.filtersets.parametro import ParametroFilterSet
from rudi_catalogos.models import Parametro
from rudi_catalogos.schemas.parametro import (
    ParametroFilterAllQuery,
    ParametroGet,
    ParametroInlineGet,
    ParametroPatch,
    ParametroPut,
)
from rudi_catalogos.services.parametro import ParametroUpdateOperation

########################################################################################


class ParametroDetailController(
    OpenReadMixin,
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        Parametro,
        ParametroGet,
        ParametroPut,
        ParametroPatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ParametroUpdateOperation

    @override
    async def put(
        self,
        parsed_body: Body[ParametroPut],
        parsed_path: Path[UuidInstancePath],
    ) -> ParametroGet:
        return await self.build_operation(
            self.update_operation,
            actor=self.request.user,
            partial=False,
        ).run(
            body=parsed_body,
            path=parsed_path,
        )

    @override
    async def patch(
        self,
        parsed_body: Body[ParametroPatch],
        parsed_path: Path[UuidInstancePath],
    ) -> ParametroGet:
        return await self.build_operation(
            self.update_operation,
            actor=self.request.user,
            partial=True,
        ).run(
            body=parsed_body,
            path=parsed_path,
        )


########################################################################################


class ParametroListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Parametro,
        ParametroFilterSet,
        ParametroFilterAllQuery,
        ParametroInlineGet,
        list[ParametroInlineGet],
    ],
):
    pass
