from typing import ClassVar

from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_auth.filtersets.identificador import IdentificadorUserFilterSet
from rudi_auth.models import IdentificadorUser
from rudi_auth.schemas.identificador import (
    IdentificadorUserFilterQuery,
    IdentificadorUserGet,
    IdentificadorUserPatch,
    IdentificadorUserPost,
    IdentificadorUserPut,
)
from rudi_core.controllers import ScopedDetailController, ScopedListController
from rudi_core.schemas import UserScopedPath

########################################################################################


class IdentificadorUserDetailController(
    ScopedDetailController[
        CustomPydanticFastSerializer,
        IdentificadorUser,
        IdentificadorUserGet,
        IdentificadorUserPut,
        IdentificadorUserPatch,
        UserScopedPath,
    ],
):
    parent_field: ClassVar[str] = "user"
    parent_param: ClassVar[str] = "user_id"


########################################################################################


class IdentificadorUserListController(
    ScopedListController[
        CustomPydanticFastSerializer,
        IdentificadorUser,
        IdentificadorUserFilterSet,
        IdentificadorUserFilterQuery,
        IdentificadorUserGet,
        IdentificadorUserPost,
        Paginated[IdentificadorUserGet],
    ],
):
    parent_field: ClassVar[str] = "user"
    parent_param: ClassVar[str] = "user_id"
