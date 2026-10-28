from api_core.controllers.mixins import OpenReadMixin
from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.reconocimiento import TipoReconocimientoFilterSet
from rudi_catalogos.models import TipoReconocimiento
from rudi_catalogos.schemas.reconocimiento import (
    TipoReconocimientoFilterAllQuery,
    TipoReconocimientoFilterQuery,
    TipoReconocimientoGet,
    TipoReconocimientoInlineGet,
    TipoReconocimientoPatch,
    TipoReconocimientoPost,
    TipoReconocimientoPut,
)

########################################################################################


class TipoReconocimientoDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        TipoReconocimiento,
        TipoReconocimientoGet,
        TipoReconocimientoPut,
        TipoReconocimientoPatch,
    ],
):
    pass


########################################################################################


class TipoReconocimientoListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        TipoReconocimiento,
        TipoReconocimientoFilterSet,
        TipoReconocimientoFilterQuery,
        TipoReconocimientoGet,
        TipoReconocimientoPost,
        Paginated[TipoReconocimientoGet],
    ],
):
    pass


########################################################################################


class TipoReconocimientoListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        TipoReconocimiento,
        TipoReconocimientoFilterSet,
        TipoReconocimientoFilterAllQuery,
        TipoReconocimientoInlineGet,
        list[TipoReconocimientoInlineGet],
    ],
):
    pass
