from typing import ClassVar

from api_core.controllers.models import (
    ModelListAllController,
    ModelListController,
    ModelReadOnlyDetailController,
    ScopedDetailController,
    ScopedListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.factories import build_scoped_path
from api_core.schemas.pagination import Paginated
from api_core.services.operations import CreateOperation
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
    ModelListController[
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
        build_scoped_path(EstudianteCarrera, "profile"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "profile"


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
