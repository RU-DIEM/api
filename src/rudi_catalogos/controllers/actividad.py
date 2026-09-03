from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.actividad import TipoActividadFilterSet
from rudi_catalogos.models import TipoActividad
from rudi_catalogos.schemas.actividad import (
    TipoActividadFilterAllQuery,
    TipoActividadFilterQuery,
    TipoActividadGet,
    TipoActividadInlineGet,
    TipoActividadPatch,
    TipoActividadPost,
    TipoActividadPut,
)
from rudi_core.mixins import OpenReadMixin

########################################################################################


class TipoActividadDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        TipoActividad,
        TipoActividadGet,
        TipoActividadPut,
        TipoActividadPatch,
    ],
):
    pass


########################################################################################


class TipoActividadListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        TipoActividad,
        TipoActividadFilterSet,
        TipoActividadFilterQuery,
        TipoActividadGet,
        TipoActividadPost,
        Paginated[TipoActividadGet],
    ],
):
    pass


########################################################################################


class TipoActividadListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        TipoActividad,
        TipoActividadFilterSet,
        TipoActividadFilterAllQuery,
        TipoActividadInlineGet,
        list[TipoActividadInlineGet],
    ],
):
    pass
