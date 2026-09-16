from typing import ClassVar

from api_core.controllers.models import (
    ModelListAllController,
    ModelReadOnlyDetailController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from api_core.services.operations import CreateOperation
from rudi_core.controllers import (
    RelationListController,
    ScopedDetailController,
    ScopedListController,
)
from rudi_core.schemas import ProfileScopedPath
from rudi_profiles.filtersets.estudiante import (
    EstudianteCarreraFilterSet,
    EstudianteProfileFilterSet,
)
from rudi_profiles.models import EstudianteCarrera, EstudianteProfile
from rudi_profiles.schemas.estudiante import (
    EstudianteCarreraFilterQuery,
    EstudianteCarreraGet,
    EstudianteCarreraPatch,
    EstudianteCarreraPost,
    EstudianteCarreraPut,
    EstudianteProfileFilterAllQuery,
    EstudianteProfileFilterQuery,
    EstudianteProfileGet,
    EstudianteProfileInlineGet,
    EstudianteProfilePost,
)
from rudi_profiles.services.estudiante import EstudianteProfileCreateOperation

########################################################################################


class EstudianteProfileDetailController(
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstudianteProfile,
        EstudianteProfileGet,
    ],
):
    pass


########################################################################################


class EstudianteProfileListController(
    RelationListController[
        CustomPydanticFastSerializer,
        EstudianteProfile,
        EstudianteProfileFilterSet,
        EstudianteProfileFilterQuery,
        EstudianteProfileGet,
        EstudianteProfilePost,
        Paginated[EstudianteProfileGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = EstudianteProfileCreateOperation


########################################################################################


class EstudianteProfileListAllController(
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstudianteProfile,
        EstudianteProfileFilterSet,
        EstudianteProfileFilterAllQuery,
        EstudianteProfileInlineGet,
        list[EstudianteProfileInlineGet],
    ],
):
    pass


########################################################################################


class EstudianteCarreraDetailController(
    ScopedDetailController[
        CustomPydanticFastSerializer,
        EstudianteCarrera,
        EstudianteCarreraGet,
        EstudianteCarreraPut,
        EstudianteCarreraPatch,
        ProfileScopedPath,
    ],
):
    parent_field: ClassVar[str] = "profile"
    parent_param: ClassVar[str] = "profile_id"


########################################################################################


class EstudianteCarreraListController(
    ScopedListController[
        CustomPydanticFastSerializer,
        EstudianteCarrera,
        EstudianteCarreraFilterSet,
        EstudianteCarreraFilterQuery,
        EstudianteCarreraGet,
        EstudianteCarreraPost,
        Paginated[EstudianteCarreraGet],
    ],
):
    parent_field: ClassVar[str] = "profile"
    parent_param: ClassVar[str] = "profile_id"
