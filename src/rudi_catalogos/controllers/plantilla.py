from api_core.controllers.mixins import OpenReadMixin
from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.plantilla import PlantillaMensajeFilterSet
from rudi_catalogos.models import PlantillaMensaje
from rudi_catalogos.schemas.plantilla import (
    PlantillaMensajeFilterAllQuery,
    PlantillaMensajeFilterQuery,
    PlantillaMensajeGet,
    PlantillaMensajeInlineGet,
    PlantillaMensajePatch,
    PlantillaMensajePost,
    PlantillaMensajePut,
)

########################################################################################


class PlantillaMensajeDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        PlantillaMensaje,
        PlantillaMensajeGet,
        PlantillaMensajePut,
        PlantillaMensajePatch,
    ],
):
    pass


########################################################################################


class PlantillaMensajeListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        PlantillaMensaje,
        PlantillaMensajeFilterSet,
        PlantillaMensajeFilterQuery,
        PlantillaMensajeGet,
        PlantillaMensajePost,
        Paginated[PlantillaMensajeGet],
    ],
):
    pass


########################################################################################


class PlantillaMensajeListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        PlantillaMensaje,
        PlantillaMensajeFilterSet,
        PlantillaMensajeFilterAllQuery,
        PlantillaMensajeInlineGet,
        list[PlantillaMensajeInlineGet],
    ],
):
    pass
