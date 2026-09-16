from api_core.controllers.models import ModelListAllController
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_core.controllers import RelationDetailController, RelationListController
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
    RelationDetailController[
        CustomPydanticFastSerializer,
        DocenteProfile,
        DocenteProfileGet,
        DocenteProfilePut,
        DocenteProfilePatch,
    ],
):
    pass


########################################################################################


class DocenteProfileListController(
    RelationListController[
        CustomPydanticFastSerializer,
        DocenteProfile,
        DocenteProfileFilterSet,
        DocenteProfileFilterQuery,
        DocenteProfileGet,
        DocenteProfilePost,
        Paginated[DocenteProfileGet],
    ],
):
    pass


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
