from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from dmr import Body, modify

from api_auth.services.permissions import T_CHANGE_PERM
from api_core.controllers.mixins import OpenReadMixin
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
from api_core.services.operations import CreateOperation
from rudi_core.services import ejecutar
from rudi_estados.enums import ActorTypes
from rudi_estados.services.transicion import transicionar
from rudi_portafolio.filtersets import (
    PropuestaActividadFilterSet,
    PropuestaFilterSet,
    PropuestaIntegranteFilterSet,
)
from rudi_portafolio.models import Propuesta, PropuestaActividad, PropuestaIntegrante
from rudi_portafolio.schemas import (
    PropuestaAccionPost,
    PropuestaActividadFilterQuery,
    PropuestaActividadGet,
    PropuestaActividadPatch,
    PropuestaActividadPost,
    PropuestaActividadPut,
    PropuestaCerrarPost,
    PropuestaFilterAllQuery,
    PropuestaFilterQuery,
    PropuestaGet,
    PropuestaInlineGet,
    PropuestaIntegranteFilterQuery,
    PropuestaIntegranteGet,
    PropuestaIntegrantePatch,
    PropuestaIntegrantePost,
    PropuestaIntegrantePut,
    PropuestaPatch,
    PropuestaPost,
    PropuestaPut,
)
from rudi_portafolio.services import PropuestaCreateOperation, cerrar_propuesta

########################################################################################

ACCION_PERMISSIONS: dict[HTTPMethod, Sequence[str]] = {
    HTTPMethod.POST: (T_CHANGE_PERM,)
}

########################################################################################


class PropuestaDetailController(
    OpenReadMixin,
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        Propuesta,
        PropuestaGet,
        PropuestaPut,
        PropuestaPatch,
    ],
):
    pass


class PropuestaListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        Propuesta,
        PropuestaFilterSet,
        PropuestaFilterQuery,
        PropuestaGet,
        PropuestaPost,
        Paginated[PropuestaGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = PropuestaCreateOperation


class PropuestaListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Propuesta,
        PropuestaFilterSet,
        PropuestaFilterAllQuery,
        PropuestaInlineGet,
        list[PropuestaInlineGet],
    ],
):
    pass


########################################################################################


class PropuestaIntegranteDetailController(
    OpenReadMixin,
    ScopedDetailController[
        CustomPydanticFastSerializer,
        PropuestaIntegrante,
        PropuestaIntegranteGet,
        PropuestaIntegrantePut,
        PropuestaIntegrantePatch,
        build_scoped_path(PropuestaIntegrante, "propuesta"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "propuesta"


class PropuestaIntegranteListController(
    OpenReadMixin,
    ScopedListController[
        CustomPydanticFastSerializer,
        PropuestaIntegrante,
        PropuestaIntegranteFilterSet,
        PropuestaIntegranteFilterQuery,
        PropuestaIntegranteGet,
        PropuestaIntegrantePost,
        Paginated[PropuestaIntegranteGet],
    ],
):
    parent_field: ClassVar[str] = "propuesta"


class PropuestaActividadDetailController(
    OpenReadMixin,
    ScopedDetailController[
        CustomPydanticFastSerializer,
        PropuestaActividad,
        PropuestaActividadGet,
        PropuestaActividadPut,
        PropuestaActividadPatch,
        build_scoped_path(PropuestaActividad, "propuesta"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "propuesta"


class PropuestaActividadListController(
    OpenReadMixin,
    ScopedListController[
        CustomPydanticFastSerializer,
        PropuestaActividad,
        PropuestaActividadFilterSet,
        PropuestaActividadFilterQuery,
        PropuestaActividadGet,
        PropuestaActividadPost,
        Paginated[PropuestaActividadGet],
    ],
):
    parent_field: ClassVar[str] = "propuesta"


########################################################################################


class PropuestaAccionController(
    ModelController[CustomPydanticFastSerializer, Propuesta, PropuestaGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = ACCION_PERMISSIONS

    async def transicionar(
        self, body: PropuestaAccionPost, codigo: str
    ) -> PropuestaGet:
        propuesta: Propuesta = await ejecutar(
            transicionar,
            actor=ActorTypes.ADMIN,
            codigo=codigo,
            entidad="propuesta",
            pk=body.propuesta_id,
            qs=self.qs,
        )

        return self.mapper(propuesta, self.schema)


class PausarPropuestaController(PropuestaAccionController):
    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[PropuestaAccionPost]) -> PropuestaGet:
        return await self.transicionar(parsed_body, "en_pausa")


class ReanudarPropuestaController(PropuestaAccionController):
    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[PropuestaAccionPost]) -> PropuestaGet:
        return await self.transicionar(parsed_body, "activa")


class CerrarPropuestaController(PropuestaAccionController):
    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[PropuestaCerrarPost]) -> PropuestaGet:
        propuesta: Propuesta = await ejecutar(
            cerrar_propuesta,
            desenlace=parsed_body.desenlace,
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
            propuesta_id=parsed_body.propuesta_id,
            qs=self.qs,
        )

        return self.mapper(propuesta, self.schema)


########################################################################################

__all__ = (
    "CerrarPropuestaController",
    "PausarPropuestaController",
    "PropuestaActividadDetailController",
    "PropuestaActividadListController",
    "PropuestaDetailController",
    "PropuestaIntegranteDetailController",
    "PropuestaIntegranteListController",
    "PropuestaListAllController",
    "PropuestaListController",
    "ReanudarPropuestaController",
)
