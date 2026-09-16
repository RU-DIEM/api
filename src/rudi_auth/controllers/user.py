from api_core.controllers.models import (
    ModelListAllController,
    ModelReadOnlyListController,
    ModelReadUpdateDetailController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_auth.filtersets.user import RudiUserFilterSet
from rudi_auth.models import RudiUser
from rudi_auth.schemas.user import (
    RudiUserFilterAllQuery,
    RudiUserFilterQuery,
    RudiUserGet,
    RudiUserInlineGet,
    RudiUserPatch,
    RudiUserPut,
)

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
    pass


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
