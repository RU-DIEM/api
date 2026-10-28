from typing import ClassVar

from api_core.controllers.models import (
    ModelListAllController,
    ModelListController,
    ModelReadUpdateDetailController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from api_core.services.operations import (
    CreateOperation,
    ForeignKeyUpdateOperation,
    UpdateOperation,
)
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
from rudi_profiles.services.base import ProfileCreateOperation

########################################################################################


class ExternoProfileDetailController(
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        ExternoProfile,
        ExternoProfileGet,
        ExternoProfilePut,
        ExternoProfilePatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ForeignKeyUpdateOperation


########################################################################################


class ExternoProfileListController(
    ModelListController[
        CustomPydanticFastSerializer,
        ExternoProfile,
        ExternoProfileFilterSet,
        ExternoProfileFilterQuery,
        ExternoProfileGet,
        ExternoProfilePost,
        Paginated[ExternoProfileGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ProfileCreateOperation


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
