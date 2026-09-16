from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from dmr import Path, modify

from api_auth.services.permissions import T_CHANGE_PERM
from api_core.controllers.models import (
    ModelController,
    ModelDetailController,
    ModelListAllController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from api_core.schemas.path import UuidInstancePath
from api_core.services.operations import FlatRetrieveOperation, UpdateOperation
from rudi_core.controllers import RelationListController
from rudi_core.mixins import OpenReadMixin, OpenWriteMixin
from rudi_core.services import RelationUpdateOperation
from rudi_profiles.filtersets.academia import (
    CarreraFilterSet,
    FacultadFilterSet,
    InstitucionFilterSet,
)
from rudi_profiles.models import Carrera, Facultad, Institucion
from rudi_profiles.schemas.academia import (
    CarreraFilterAllQuery,
    CarreraFilterQuery,
    CarreraGet,
    CarreraInlineGet,
    CarreraPatch,
    CarreraPost,
    CarreraPut,
    FacultadFilterAllQuery,
    FacultadFilterQuery,
    FacultadGet,
    FacultadInlineGet,
    FacultadPatch,
    FacultadPost,
    FacultadPut,
    InstitucionFilterAllQuery,
    InstitucionFilterQuery,
    InstitucionGet,
    InstitucionInlineGet,
    InstitucionPatch,
    InstitucionPost,
    InstitucionPut,
)
from rudi_profiles.services.academia import normalizar_institucion

########################################################################################


class FacultadDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        Facultad,
        FacultadGet,
        FacultadPut,
        FacultadPatch,
    ],
):
    pass


class FacultadListController(
    OpenReadMixin,
    RelationListController[
        CustomPydanticFastSerializer,
        Facultad,
        FacultadFilterSet,
        FacultadFilterQuery,
        FacultadGet,
        FacultadPost,
        Paginated[FacultadGet],
    ],
):
    pass


class FacultadListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Facultad,
        FacultadFilterSet,
        FacultadFilterAllQuery,
        FacultadInlineGet,
        list[FacultadInlineGet],
    ],
):
    pass


########################################################################################


class CarreraDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        Carrera,
        CarreraGet,
        CarreraPut,
        CarreraPatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = RelationUpdateOperation


class CarreraListController(
    OpenReadMixin,
    RelationListController[
        CustomPydanticFastSerializer,
        Carrera,
        CarreraFilterSet,
        CarreraFilterQuery,
        CarreraGet,
        CarreraPost,
        Paginated[CarreraGet],
    ],
):
    pass


class CarreraListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Carrera,
        CarreraFilterSet,
        CarreraFilterAllQuery,
        CarreraInlineGet,
        list[CarreraInlineGet],
    ],
):
    pass


########################################################################################


class InstitucionDetailController(
    OpenWriteMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        Institucion,
        InstitucionGet,
        InstitucionPut,
        InstitucionPatch,
    ],
):
    pass


class InstitucionListController(
    OpenWriteMixin,
    RelationListController[
        CustomPydanticFastSerializer,
        Institucion,
        InstitucionFilterSet,
        InstitucionFilterQuery,
        InstitucionGet,
        InstitucionPost,
        Paginated[InstitucionGet],
    ],
):
    pass


class InstitucionListAllController(
    OpenWriteMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Institucion,
        InstitucionFilterSet,
        InstitucionFilterAllQuery,
        InstitucionInlineGet,
        list[InstitucionInlineGet],
    ],
):
    pass


########################################################################################


class InstitucionNormalizarController(
    ModelController[
        CustomPydanticFastSerializer,
        Institucion,
        InstitucionGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_CHANGE_PERM,),
    }

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_path: Path[UuidInstancePath]) -> InstitucionGet:
        await normalizar_institucion(parsed_path.id)

        return await self.build_operation(FlatRetrieveOperation).run(path=parsed_path)
