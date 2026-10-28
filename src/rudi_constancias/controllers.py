from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from dmr import Body, modify

from api_auth.services.permissions import T_ADD_PERM, T_CHANGE_PERM
from api_core.controllers.mixins import (
    OpenReadMixin,
    PublicControllerMixin,
    StrictThrottlingMixin,
)
from api_core.controllers.models import (
    ModelController,
    ModelListAllController,
    ModelListController,
    ModelReadOnlyDetailController,
    ModelReadOnlyListController,
    ModelReadUpdateDetailController,
    ScopedReadOnlyListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_auth.controllers.me import SelfScopedMixin
from rudi_constancias.filtersets import (
    ConstanciaFilterSet,
    ConstanciaParticipacionFilterSet,
    PlantillaConstanciaFilterSet,
)
from rudi_constancias.models import (
    Constancia,
    ConstanciaParticipacion,
    PlantillaConstancia,
)
from rudi_constancias.schemas import (
    ConstanciaAnularPost,
    ConstanciaEmitirPost,
    ConstanciaFilterQuery,
    ConstanciaGet,
    ConstanciaParticipacionFilterQuery,
    ConstanciaParticipacionGet,
    ConstanciaVerificadaGet,
    ConstanciaVerificarPost,
    PlantillaConstanciaFilterAllQuery,
    PlantillaConstanciaFilterQuery,
    PlantillaConstanciaGet,
    PlantillaConstanciaInlineGet,
    PlantillaConstanciaPatch,
    PlantillaConstanciaPost,
    PlantillaConstanciaPut,
)
from rudi_constancias.services import (
    anular_constancia,
    crear_version,
    emitir_constancia,
    verificar_constancia,
)
from rudi_core.services import ejecutar

########################################################################################


class PlantillaConstanciaDetailController(
    OpenReadMixin,
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        PlantillaConstancia,
        PlantillaConstanciaGet,
        PlantillaConstanciaPut,
        PlantillaConstanciaPatch,
    ],
):
    pass


class PlantillaConstanciaListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        PlantillaConstancia,
        PlantillaConstanciaFilterSet,
        PlantillaConstanciaFilterQuery,
        PlantillaConstanciaGet,
        PlantillaConstanciaPost,
        Paginated[PlantillaConstanciaGet],
    ],
):
    async def post(
        self,
        parsed_body: Body[PlantillaConstanciaPost],
    ) -> PlantillaConstanciaGet:
        plantilla: PlantillaConstancia = await ejecutar(
            crear_version,
            data=parsed_body.model_dump(),
            qs=self.qs,
        )

        return self.mapper(plantilla, self.schema)


class PlantillaConstanciaListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        PlantillaConstancia,
        PlantillaConstanciaFilterSet,
        PlantillaConstanciaFilterAllQuery,
        PlantillaConstanciaInlineGet,
        list[PlantillaConstanciaInlineGet],
    ],
):
    pass


########################################################################################


class ConstanciaDetailController(
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        Constancia,
        ConstanciaGet,
    ],
):
    pass


class ConstanciaListController(
    ModelReadOnlyListController[
        CustomPydanticFastSerializer,
        Constancia,
        ConstanciaFilterSet,
        ConstanciaFilterQuery,
        ConstanciaGet,
        Paginated[ConstanciaGet],
    ],
):
    pass


class ConstanciaParticipacionListController(
    ScopedReadOnlyListController[
        CustomPydanticFastSerializer,
        ConstanciaParticipacion,
        ConstanciaParticipacionFilterSet,
        ConstanciaParticipacionFilterQuery,
        ConstanciaParticipacionGet,
        Paginated[ConstanciaParticipacionGet],
    ],
):
    parent_field: ClassVar[str] = "constancia"


class MisConstanciasController(
    SelfScopedMixin,
    ModelReadOnlyListController[
        CustomPydanticFastSerializer,
        Constancia,
        ConstanciaFilterSet,
        ConstanciaFilterQuery,
        ConstanciaGet,
        Paginated[ConstanciaGet],
    ],
):
    namespace = "mis"

    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {HTTPMethod.GET: ()}

    self_field: ClassVar[str] = "user__user"


########################################################################################


class EmitirConstanciaController(
    ModelController[CustomPydanticFastSerializer, Constancia, ConstanciaGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_ADD_PERM,),
    }

    async def post(self, parsed_body: Body[ConstanciaEmitirPost]) -> ConstanciaGet:
        constancia: Constancia = await ejecutar(
            emitir_constancia,
            emitida_por=self.request.user,
            participaciones=parsed_body.participaciones,
            plantilla_id=parsed_body.plantilla_id,
            qs=self.qs,
            reemplaza_a_id=parsed_body.reemplaza_a_id,
            solicitada_at=parsed_body.solicitada_at,
            user_id=parsed_body.user_id,
        )

        return self.mapper(constancia, self.schema)


class AnularConstanciaController(
    ModelController[CustomPydanticFastSerializer, Constancia, ConstanciaGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_CHANGE_PERM,),
    }

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[ConstanciaAnularPost]) -> ConstanciaGet:
        constancia: Constancia = await ejecutar(
            anular_constancia,
            constancia_id=parsed_body.constancia_id,
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
            qs=self.qs,
        )

        return self.mapper(constancia, self.schema)


class VerificarConstanciaController(
    PublicControllerMixin,
    StrictThrottlingMixin,
    ModelController[CustomPydanticFastSerializer, Constancia, ConstanciaVerificadaGet],
):
    """
    The public verification page: anyone holding a folio and its code.
    """

    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {HTTPMethod.POST: ()}

    @modify(status_code=HTTPStatus.OK)
    async def post(  # ruff: ignore[no-self-use]
        self,
        parsed_body: Body[ConstanciaVerificarPost],
    ) -> ConstanciaVerificadaGet:
        return ConstanciaVerificadaGet(
            **await ejecutar(
                verificar_constancia,
                codigo_verificacion=parsed_body.codigo_verificacion,
                folio=parsed_body.folio,
            ),
        )


########################################################################################

__all__ = (
    "AnularConstanciaController",
    "ConstanciaDetailController",
    "ConstanciaListController",
    "ConstanciaParticipacionListController",
    "EmitirConstanciaController",
    "MisConstanciasController",
    "PlantillaConstanciaDetailController",
    "PlantillaConstanciaListAllController",
    "PlantillaConstanciaListController",
    "VerificarConstanciaController",
)
