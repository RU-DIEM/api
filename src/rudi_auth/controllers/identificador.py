from typing import ClassVar

from api_core.controllers.models import ScopedDetailController, ScopedListController
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.factories import build_scoped_path
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

########################################################################################


class IdentificadorUserDetailController(
    ScopedDetailController[
        CustomPydanticFastSerializer,
        IdentificadorUser,
        IdentificadorUserGet,
        IdentificadorUserPut,
        IdentificadorUserPatch,
        build_scoped_path(IdentificadorUser, "user"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "user"


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
