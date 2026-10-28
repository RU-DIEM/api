from typing import ClassVar, override

from dmr import Path

from api_core.controllers.models import (
    ModelListAllController,
    ModelReadOnlyListController,
    ModelReadUpdateDetailController,
    ScopedReadOnlyListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from api_core.schemas.path import UuidInstancePath
from rudi_auth.filtersets.acceso import AccesoDatoPersonalFilterSet
from rudi_auth.filtersets.user import RudiUserFilterSet
from rudi_auth.models import AccesoDatoPersonal, RudiUser
from rudi_auth.schemas.acceso import (
    AccesoDatoPersonalFilterQuery,
    AccesoDatoPersonalGet,
)
from rudi_auth.schemas.user import (
    RudiUserFilterAllQuery,
    RudiUserFilterQuery,
    RudiUserGet,
    RudiUserInlineGet,
    RudiUserPatch,
    RudiUserPut,
)
from rudi_auth.services.acceso import registrar_acceso
from rudi_core.services import ejecutar

########################################################################################


class RudiUserDetailController(
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        RudiUser,
        RudiUserGet,
        RudiUserPut,
        RudiUserPatch,
    ],
):
    @override
    async def get(
        self,
        parsed_path: Path[UuidInstancePath],
    ) -> RudiUserGet:
        persona: RudiUserGet = await super().get(parsed_path)

        # someone else's personal data was read: say who (acceso_dato_personal)
        await ejecutar(
            registrar_acceso,
            accedido_por=self.request.user,
            persona_id=parsed_path.id,
            recurso=self.request.path,
        )

        return persona


########################################################################################


class RudiUserListController(
    ModelReadOnlyListController[
        CustomPydanticFastSerializer,
        RudiUser,
        RudiUserFilterSet,
        RudiUserFilterQuery,
        RudiUserGet,
        Paginated[RudiUserGet],
    ],
):
    pass


########################################################################################


class RudiUserListAllController(
    ModelListAllController[
        CustomPydanticFastSerializer,
        RudiUser,
        RudiUserFilterSet,
        RudiUserFilterAllQuery,
        RudiUserInlineGet,
        list[RudiUserInlineGet],
    ],
):
    pass


########################################################################################


class AccesoDatoPersonalListController(
    ScopedReadOnlyListController[
        CustomPydanticFastSerializer,
        AccesoDatoPersonal,
        AccesoDatoPersonalFilterSet,
        AccesoDatoPersonalFilterQuery,
        AccesoDatoPersonalGet,
        Paginated[AccesoDatoPersonalGet],
    ],
):
    parent_field: ClassVar[str] = "user"
