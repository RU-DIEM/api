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
    ForeignKeyCreateOperation,
    ForeignKeyUpdateOperation,
    UpdateOperation,
)
from rudi_profiles.filtersets.docente import DocenteProfileFilterSet
from rudi_profiles.models import DocenteProfile
from rudi_profiles.schemas.docente import (
    DocenteProfileFilterAllQuery,
    DocenteProfileFilterQuery,
    DocenteProfileGet,
    DocenteProfileInlineGet,
    DocenteProfilePatch,
    DocenteProfilePost,
    DocenteProfilePut,
)

########################################################################################


class DocenteProfileDetailController(
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        DocenteProfile,
        DocenteProfileGet,
        DocenteProfilePut,
        DocenteProfilePatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ForeignKeyUpdateOperation


########################################################################################


class DocenteProfileListController(
    ModelListController[
        CustomPydanticFastSerializer,
        DocenteProfile,
        DocenteProfileFilterSet,
        DocenteProfileFilterQuery,
        DocenteProfileGet,
        DocenteProfilePost,
        Paginated[DocenteProfileGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ForeignKeyCreateOperation


########################################################################################


class DocenteProfileListAllController(
    ModelListAllController[
        CustomPydanticFastSerializer,
        DocenteProfile,
        DocenteProfileFilterSet,
        DocenteProfileFilterAllQuery,
        DocenteProfileInlineGet,
        list[DocenteProfileInlineGet],
    ],
):
    pass
