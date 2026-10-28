from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from dmr import Body, modify

from api_auth.services.permissions import T_CHANGE_PERM
from api_core.controllers.mixins import OpenReadMixin
from api_core.controllers.models import (
    ModelController,
    ModelDetailController,
    ModelListAllController,
    ModelListController,
    ModelReadOnlyDetailController,
    ModelReadOnlyListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from api_core.services.operations import CreateOperation, UpdateOperation
from rudi_auth.controllers.me import SelfScopedMixin
from rudi_auth.services.persona import persona_de
from rudi_core.services import ejecutar
from rudi_puntos.filtersets import MovimientoPuntoFilterSet, ReglaPuntuacionFilterSet
from rudi_puntos.models import MovimientoPunto, ReglaPuntuacion
from rudi_puntos.schemas import (
    MovimientoPuntoFilterQuery,
    MovimientoPuntoGet,
    MovimientoPuntoPost,
    MovimientoRevertirPost,
    ReglaPuntuacionFilterAllQuery,
    ReglaPuntuacionFilterQuery,
    ReglaPuntuacionGet,
    ReglaPuntuacionPatch,
    ReglaPuntuacionPost,
    ReglaPuntuacionPut,
    SaldoGet,
)
from rudi_puntos.services import (
    ReglaPuntuacionCreateOperation,
    ReglaPuntuacionUpdateOperation,
    ajustar_puntos,
    revertir_movimiento,
    saldo,
)

########################################################################################


class ReglaPuntuacionDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        ReglaPuntuacion,
        ReglaPuntuacionGet,
        ReglaPuntuacionPut,
        ReglaPuntuacionPatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ReglaPuntuacionUpdateOperation


class ReglaPuntuacionListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        ReglaPuntuacion,
        ReglaPuntuacionFilterSet,
        ReglaPuntuacionFilterQuery,
        ReglaPuntuacionGet,
        ReglaPuntuacionPost,
        Paginated[ReglaPuntuacionGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ReglaPuntuacionCreateOperation


class ReglaPuntuacionListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        ReglaPuntuacion,
        ReglaPuntuacionFilterSet,
        ReglaPuntuacionFilterAllQuery,
        ReglaPuntuacionGet,
        list[ReglaPuntuacionGet],
    ],
):
    pass


########################################################################################


class MovimientoPuntoDetailController(
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        MovimientoPunto,
        MovimientoPuntoGet,
    ],
):
    pass


class MovimientoPuntoListController(
    ModelListController[
        CustomPydanticFastSerializer,
        MovimientoPunto,
        MovimientoPuntoFilterSet,
        MovimientoPuntoFilterQuery,
        MovimientoPuntoGet,
        MovimientoPuntoPost,
        Paginated[MovimientoPuntoGet],
    ],
):
    async def post(self, parsed_body: Body[MovimientoPuntoPost]) -> MovimientoPuntoGet:
        movimiento: MovimientoPunto = await ejecutar(
            ajustar_puntos,
            anio=parsed_body.anio,
            descripcion=parsed_body.descripcion,
            motivo_id=parsed_body.motivo,
            participacion_id=parsed_body.participacion,
            puntos=parsed_body.puntos,
            qs=self.qs,
            registrado_por=self.request.user,
            user_id=parsed_body.user,
        )

        return self.mapper(movimiento, self.schema)


class RevertirMovimientoController(
    ModelController[CustomPydanticFastSerializer, MovimientoPunto, MovimientoPuntoGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_CHANGE_PERM,),
    }

    async def post(
        self,
        parsed_body: Body[MovimientoRevertirPost],
    ) -> MovimientoPuntoGet:
        reverso: MovimientoPunto = await ejecutar(
            revertir_movimiento,
            descripcion=parsed_body.descripcion,
            motivo_id=parsed_body.motivo_id,
            movimiento_id=parsed_body.movimiento_id,
            qs=self.qs,
            registrado_por=self.request.user,
        )

        return self.mapper(reverso, self.schema)


########################################################################################


class MisMovimientosController(
    SelfScopedMixin,
    ModelReadOnlyListController[
        CustomPydanticFastSerializer,
        MovimientoPunto,
        MovimientoPuntoFilterSet,
        MovimientoPuntoFilterQuery,
        MovimientoPuntoGet,
        Paginated[MovimientoPuntoGet],
    ],
):
    """
    The detail of one's own balance (RF-P-22).
    """

    namespace = "mis"

    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {HTTPMethod.GET: ()}

    self_field: ClassVar[str] = "user__user"


class MiSaldoController(
    ModelController[CustomPydanticFastSerializer, MovimientoPunto, SaldoGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {HTTPMethod.GET: ()}

    @modify(status_code=HTTPStatus.OK)
    async def get(self) -> SaldoGet:
        persona = await ejecutar(persona_de, cuenta=self.request.user)

        return SaldoGet(**await ejecutar(saldo, user_id=persona.pk))


########################################################################################

__all__ = (
    "MiSaldoController",
    "MisMovimientosController",
    "MovimientoPuntoDetailController",
    "MovimientoPuntoListController",
    "ReglaPuntuacionDetailController",
    "ReglaPuntuacionListAllController",
    "ReglaPuntuacionListController",
    "RevertirMovimientoController",
)
