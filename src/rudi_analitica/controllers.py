from collections.abc import Sequence
from http import HTTPMethod
from typing import ClassVar

from dmr import Body

from api_auth.services.permissions import T_ADD_PERM
from api_core.controllers.models import (
    ModelController,
    ModelListAllController,
    ModelListController,
    ModelReadOnlyDetailController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_analitica.filtersets import IndicadorPeriodoFilterSet
from rudi_analitica.models import IndicadorPeriodo
from rudi_analitica.schemas import (
    CerrarPeriodoPost,
    IndicadorPeriodoFilterAllQuery,
    IndicadorPeriodoFilterQuery,
    IndicadorPeriodoGet,
    IndicadorPeriodoPost,
)
from rudi_analitica.services import cerrar_periodo
from rudi_core.services import ejecutar

########################################################################################


class IndicadorPeriodoDetailController(
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        IndicadorPeriodo,
        IndicadorPeriodoGet,
    ],
):
    pass


class IndicadorPeriodoListController(
    ModelListController[
        CustomPydanticFastSerializer,
        IndicadorPeriodo,
        IndicadorPeriodoFilterSet,
        IndicadorPeriodoFilterQuery,
        IndicadorPeriodoGet,
        IndicadorPeriodoPost,
        Paginated[IndicadorPeriodoGet],
    ],
):
    async def post(
        self, parsed_body: Body[IndicadorPeriodoPost]
    ) -> IndicadorPeriodoGet:
        indicador: IndicadorPeriodo = await ejecutar(
            IndicadorPeriodo.objects.create,
            cerrado_por=self.request.user,
            **parsed_body.model_dump(),
        )

        return self.mapper(indicador, self.schema)


class IndicadorPeriodoListAllController(
    ModelListAllController[
        CustomPydanticFastSerializer,
        IndicadorPeriodo,
        IndicadorPeriodoFilterSet,
        IndicadorPeriodoFilterAllQuery,
        IndicadorPeriodoGet,
        list[IndicadorPeriodoGet],
    ],
):
    pass


class CerrarPeriodoController(
    ModelController[
        CustomPydanticFastSerializer,
        IndicadorPeriodo,
        IndicadorPeriodoGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.POST: (T_ADD_PERM,),
    }

    async def post(
        self,
        parsed_body: Body[CerrarPeriodoPost],
    ) -> list[IndicadorPeriodoGet]:
        indicadores: list[IndicadorPeriodo] = await ejecutar(
            cerrar_periodo,
            anio=parsed_body.anio,
            cerrado_por=self.request.user,
        )

        return [self.mapper(i, self.schema) for i in indicadores]


########################################################################################

__all__ = (
    "CerrarPeriodoController",
    "IndicadorPeriodoDetailController",
    "IndicadorPeriodoListAllController",
    "IndicadorPeriodoListController",
)
