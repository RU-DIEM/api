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
    ModelReadUpdateDetailController,
    ScopedDetailController,
    ScopedListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.factories import build_scoped_path
from api_core.schemas.pagination import Paginated
from api_core.services.operations import (
    CreateOperation,
    ForeignKeyCreateOperation,
    ForeignKeyUpdateOperation,
    UpdateOperation,
)
from rudi_actividades.filtersets import (
    ActividadFilterSet,
    ActividadResponsableFilterSet,
    ProgramaFilterSet,
)
from rudi_actividades.models import Actividad, ActividadResponsable, Programa
from rudi_actividades.schemas import (
    ActividadAccionPost,
    ActividadCancelarPost,
    ActividadFilterAllQuery,
    ActividadFilterQuery,
    ActividadGet,
    ActividadInlineGet,
    ActividadPatch,
    ActividadPost,
    ActividadPut,
    ActividadResponsableFilterQuery,
    ActividadResponsableGet,
    ActividadResponsablePatch,
    ActividadResponsablePost,
    ActividadResponsablePut,
    ProgramaFilterAllQuery,
    ProgramaFilterQuery,
    ProgramaGet,
    ProgramaInlineGet,
    ProgramaPatch,
    ProgramaPost,
    ProgramaPut,
)
from rudi_actividades.services import ActividadCreateOperation, cancelar_actividad
from rudi_core.services import ejecutar
from rudi_estados.enums import ActorTypes
from rudi_estados.services.transicion import transicionar

########################################################################################

# every state change is an administrative action on the activity
ACCION_PERMISSIONS: dict[HTTPMethod, Sequence[str]] = {
    HTTPMethod.POST: (T_CHANGE_PERM,)
}

########################################################################################


class ProgramaDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        Programa,
        ProgramaGet,
        ProgramaPut,
        ProgramaPatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ForeignKeyUpdateOperation


class ProgramaListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        Programa,
        ProgramaFilterSet,
        ProgramaFilterQuery,
        ProgramaGet,
        ProgramaPost,
        Paginated[ProgramaGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ForeignKeyCreateOperation


class ProgramaListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Programa,
        ProgramaFilterSet,
        ProgramaFilterAllQuery,
        ProgramaInlineGet,
        list[ProgramaInlineGet],
    ],
):
    pass


########################################################################################


class ActividadDetailController(
    OpenReadMixin,
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        Actividad,
        ActividadGet,
        ActividadPut,
        ActividadPatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ForeignKeyUpdateOperation


class ActividadListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        Actividad,
        ActividadFilterSet,
        ActividadFilterQuery,
        ActividadGet,
        ActividadPost,
        Paginated[ActividadGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ActividadCreateOperation


class ActividadListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Actividad,
        ActividadFilterSet,
        ActividadFilterAllQuery,
        ActividadInlineGet,
        list[ActividadInlineGet],
    ],
):
    pass


########################################################################################


class ActividadResponsableDetailController(
    OpenReadMixin,
    ScopedDetailController[
        CustomPydanticFastSerializer,
        ActividadResponsable,
        ActividadResponsableGet,
        ActividadResponsablePut,
        ActividadResponsablePatch,
        build_scoped_path(ActividadResponsable, "actividad"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "actividad"


class ActividadResponsableListController(
    OpenReadMixin,
    ScopedListController[
        CustomPydanticFastSerializer,
        ActividadResponsable,
        ActividadResponsableFilterSet,
        ActividadResponsableFilterQuery,
        ActividadResponsableGet,
        ActividadResponsablePost,
        Paginated[ActividadResponsableGet],
    ],
):
    parent_field: ClassVar[str] = "actividad"


########################################################################################


class ActividadAccionController(
    ModelController[
        CustomPydanticFastSerializer,
        Actividad,
        ActividadGet,
    ],
):
    """
    Base of the one-controller-per-transition endpoints (hz-api's pattern).

    The controller names the target state; the triggers decide if the move is
    legal for the `administracion` actor.
    """

    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = ACCION_PERMISSIONS

    codigo: ClassVar[str]

    async def transicionar(self, actividad_id: object) -> ActividadGet:
        actividad: Actividad = await ejecutar(
            transicionar,
            actor=ActorTypes.ADMIN,
            codigo=self.codigo,
            entidad="actividad",
            pk=actividad_id,
            qs=self.qs,
        )

        return self.mapper(actividad, self.schema)


class PublicarActividadController(ActividadAccionController):
    codigo: ClassVar[str] = "publicada"

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[ActividadAccionPost]) -> ActividadGet:
        return await self.transicionar(parsed_body.actividad_id)


class IniciarActividadController(ActividadAccionController):
    codigo: ClassVar[str] = "en_curso"

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[ActividadAccionPost]) -> ActividadGet:
        return await self.transicionar(parsed_body.actividad_id)


class FinalizarActividadController(ActividadAccionController):
    codigo: ClassVar[str] = "finalizada"

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[ActividadAccionPost]) -> ActividadGet:
        return await self.transicionar(parsed_body.actividad_id)


class CancelarActividadController(ActividadAccionController):
    codigo: ClassVar[str] = "cancelada"

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[ActividadCancelarPost]) -> ActividadGet:
        actividad: Actividad = await ejecutar(
            cancelar_actividad,
            actividad_id=parsed_body.actividad_id,
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
            qs=self.qs,
        )

        return self.mapper(actividad, self.schema)
