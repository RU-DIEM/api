from api_core.controllers.models import ModelListAllController
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_core.controllers import RelationDetailController, RelationListController
from rudi_profiles.filtersets.externo import ExternoProfileFilterSet
from rudi_profiles.models import ExternoProfile
from rudi_profiles.schemas.externo import (
    ExternoProfileFilterAllQuery,
    ExternoProfileFilterQuery,
    ExternoProfileGet,
    ExternoProfileInlineGet,
    ExternoProfilePatch,
    ExternoProfilePost,
    ExternoProfilePut,
)

########################################################################################


class ExternoProfileDetailController(
    RelationDetailController[
        CustomPydanticFastSerializer,
        ExternoProfile,
        ExternoProfileGet,
        ExternoProfilePut,
        ExternoProfilePatch,
    ],
):
    pass


########################################################################################


class ExternoProfileListController(
    RelationListController[
        CustomPydanticFastSerializer,
        ExternoProfile,
        ExternoProfileFilterSet,
        ExternoProfileFilterQuery,
        ExternoProfileGet,
        ExternoProfilePost,
        Paginated[ExternoProfileGet],
    ],
):
    pass


########################################################################################


class ExternoProfileListAllController(
    ModelListAllController[
        CustomPydanticFastSerializer,
        ExternoProfile,
        ExternoProfileFilterSet,
        ExternoProfileFilterAllQuery,
        ExternoProfileInlineGet,
        list[ExternoProfileInlineGet],
    ],
):
    pass
