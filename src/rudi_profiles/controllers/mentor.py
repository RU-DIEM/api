from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from dmr import Path, modify

from api_auth.services.permissions import T_CHANGE_PERM
from api_core.controllers.models import (
    ModelController,
    ModelListAllController,
    ModelListController,
    ModelReadUpdateDetailController,
    ScopedDetailController,
    ScopedListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.factories import build_scoped_path
from api_core.schemas.pagination import Paginated
from api_core.schemas.path import UuidInstancePath
from api_core.services.operations import (
    CreateOperation,
    FlatRetrieveOperation,
    ForeignKeyUpdateOperation,
    UpdateOperation,
)
from rudi_profiles.filtersets.mentor import (
    MentorAreaExperienciaFilterSet,
    MentorCertificacionFilterSet,
    MentorProfileFilterSet,
)
from rudi_profiles.models import (
    MentorAreaExperiencia,
    MentorCertificacion,
    MentorProfile,
)
from rudi_profiles.schemas.mentor import (
    MentorAreaExperienciaFilterQuery,
    MentorAreaExperienciaGet,
    MentorAreaExperienciaPatch,
    MentorAreaExperienciaPost,
    MentorAreaExperienciaPut,
    MentorCertificacionFilterQuery,
    MentorCertificacionGet,
    MentorCertificacionPatch,
    MentorCertificacionPost,
    MentorCertificacionPut,
    MentorProfileFilterAllQuery,
    MentorProfileFilterQuery,
    MentorProfileGet,
    MentorProfileInlineGet,
    MentorProfilePatch,
    MentorProfilePost,
    MentorProfilePut,
)
from rudi_profiles.services.base import ProfileCreateOperation
from rudi_profiles.services.mentor import confirmar_mentor

########################################################################################


class MentorProfileDetailController(
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        MentorProfile,
        MentorProfileGet,
        MentorProfilePut,
        MentorProfilePatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ForeignKeyUpdateOperation


########################################################################################


class MentorProfileListController(
    ModelListController[
        CustomPydanticFastSerializer,
        MentorProfile,
        MentorProfileFilterSet,
        MentorProfileFilterQuery,
        MentorProfileGet,
        MentorProfilePost,
        Paginated[MentorProfileGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ProfileCreateOperation


########################################################################################


class MentorProfileListAllController(
    ModelListAllController[
        CustomPydanticFastSerializer,
        MentorProfile,
        MentorProfileFilterSet,
        MentorProfileFilterAllQuery,
        MentorProfileInlineGet,
        list[MentorProfileInlineGet],
    ],
):
    pass


########################################################################################


class MentorConfirmarController(
    ModelController[
        CustomPydanticFastSerializer,
        MentorProfile,
        MentorProfileGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_CHANGE_PERM,),
    }

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_path: Path[UuidInstancePath]) -> MentorProfileGet:
        await confirmar_mentor(actor=self.request.user, profile_id=parsed_path.id)

        return await self.build_operation(FlatRetrieveOperation).run(path=parsed_path)


########################################################################################


class MentorAreaExperienciaDetailController(
    ScopedDetailController[
        CustomPydanticFastSerializer,
        MentorAreaExperiencia,
        MentorAreaExperienciaGet,
        MentorAreaExperienciaPut,
        MentorAreaExperienciaPatch,
        build_scoped_path(MentorAreaExperiencia, "profile"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "profile"


########################################################################################


class MentorAreaExperienciaListController(
    ScopedListController[
        CustomPydanticFastSerializer,
        MentorAreaExperiencia,
        MentorAreaExperienciaFilterSet,
        MentorAreaExperienciaFilterQuery,
        MentorAreaExperienciaGet,
        MentorAreaExperienciaPost,
        Paginated[MentorAreaExperienciaGet],
    ],
):
    parent_field: ClassVar[str] = "profile"


########################################################################################


class MentorCertificacionDetailController(
    ScopedDetailController[
        CustomPydanticFastSerializer,
        MentorCertificacion,
        MentorCertificacionGet,
        MentorCertificacionPut,
        MentorCertificacionPatch,
        build_scoped_path(MentorCertificacion, "profile"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "profile"


########################################################################################


class MentorCertificacionListController(
    ScopedListController[
        CustomPydanticFastSerializer,
        MentorCertificacion,
        MentorCertificacionFilterSet,
        MentorCertificacionFilterQuery,
        MentorCertificacionGet,
        MentorCertificacionPost,
        Paginated[MentorCertificacionGet],
    ],
):
    parent_field: ClassVar[str] = "profile"
