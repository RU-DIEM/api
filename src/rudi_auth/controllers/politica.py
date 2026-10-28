from collections.abc import Sequence
from http import HTTPMethod
from typing import ClassVar

from api_core.controllers.mixins import OpenReadMixin, PublicControllerMixin
from api_core.controllers.models import (
    ModelController,
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
from api_exceptions.errors import NotFoundError
from rudi_auth.filtersets.politica import PoliticaPrivacidadFilterSet
from rudi_auth.models import PoliticaPrivacidad
from rudi_auth.schemas.politica import (
    PoliticaPrivacidadFilterAllQuery,
    PoliticaPrivacidadFilterQuery,
    PoliticaPrivacidadGet,
    PoliticaPrivacidadInlineGet,
    PoliticaPrivacidadPatch,
    PoliticaPrivacidadPost,
    PoliticaPrivacidadPut,
)
from rudi_auth.services.politica import PoliticaCreateOperation

########################################################################################


class PoliticaPrivacidadDetailController(
    OpenReadMixin,
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        PoliticaPrivacidad,
        PoliticaPrivacidadGet,
        PoliticaPrivacidadPut,
        PoliticaPrivacidadPatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ForeignKeyUpdateOperation


########################################################################################


class PoliticaPrivacidadListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        PoliticaPrivacidad,
        PoliticaPrivacidadFilterSet,
        PoliticaPrivacidadFilterQuery,
        PoliticaPrivacidadGet,
        PoliticaPrivacidadPost,
        Paginated[PoliticaPrivacidadGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = PoliticaCreateOperation


########################################################################################


class PoliticaPrivacidadListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        PoliticaPrivacidad,
        PoliticaPrivacidadFilterSet,
        PoliticaPrivacidadFilterAllQuery,
        PoliticaPrivacidadInlineGet,
        list[PoliticaPrivacidadInlineGet],
    ],
):
    pass


########################################################################################


class PoliticaVigenteController(
    PublicControllerMixin,
    ModelController[
        CustomPydanticFastSerializer,
        PoliticaPrivacidad,
        PoliticaPrivacidadGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {HTTPMethod.GET: ()}

    async def get(self) -> PoliticaPrivacidadGet:
        politica: PoliticaPrivacidad | None = await self.qs.filter(
            vigente_hasta__isnull=True,
        ).afirst()

        if politica is None:
            raise NotFoundError(
                detail="No hay una política de privacidad vigente.",
            )

        return self.mapper(politica, self.schema)
