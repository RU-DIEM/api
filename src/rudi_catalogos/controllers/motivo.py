from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.motivo import MotivoFilterSet
from rudi_catalogos.models import Motivo
from rudi_catalogos.schemas.motivo import (
    MotivoFilterAllQuery,
    MotivoFilterQuery,
    MotivoGet,
    MotivoInlineGet,
    MotivoPatch,
    MotivoPost,
    MotivoPut,
)
from rudi_core.mixins import OpenReadMixin

########################################################################################


class MotivoDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        Motivo,
        MotivoGet,
        MotivoPut,
        MotivoPatch,
    ],
):
    pass


########################################################################################


class MotivoListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        Motivo,
        MotivoFilterSet,
        MotivoFilterQuery,
        MotivoGet,
        MotivoPost,
        Paginated[MotivoGet],
    ],
):
    pass


########################################################################################


class MotivoListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Motivo,
        MotivoFilterSet,
        MotivoFilterAllQuery,
        MotivoInlineGet,
        list[MotivoInlineGet],
    ],
):
    pass
