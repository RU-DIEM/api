from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.identificador import TipoIdentificadorFilterSet
from rudi_catalogos.models import TipoIdentificador
from rudi_catalogos.schemas.identificador import (
    TipoIdentificadorFilterAllQuery,
    TipoIdentificadorFilterQuery,
    TipoIdentificadorGet,
    TipoIdentificadorInlineGet,
    TipoIdentificadorPatch,
    TipoIdentificadorPost,
    TipoIdentificadorPut,
)
from rudi_core.mixins import OpenReadMixin

########################################################################################


class TipoIdentificadorDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        TipoIdentificador,
        TipoIdentificadorGet,
        TipoIdentificadorPut,
        TipoIdentificadorPatch,
    ],
):
    pass


########################################################################################


class TipoIdentificadorListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        TipoIdentificador,
        TipoIdentificadorFilterSet,
        TipoIdentificadorFilterQuery,
        TipoIdentificadorGet,
        TipoIdentificadorPost,
        Paginated[TipoIdentificadorGet],
    ],
):
    pass


########################################################################################


class TipoIdentificadorListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        TipoIdentificador,
        TipoIdentificadorFilterSet,
        TipoIdentificadorFilterAllQuery,
        TipoIdentificadorInlineGet,
        list[TipoIdentificadorInlineGet],
    ],
):
    pass
