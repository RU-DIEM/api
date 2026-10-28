from api_core.controllers.mixins import OpenReadMixin
from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.rol import RolParticipacionFilterSet
from rudi_catalogos.models import RolParticipacion
from rudi_catalogos.schemas.rol import (
    RolParticipacionFilterAllQuery,
    RolParticipacionFilterQuery,
    RolParticipacionGet,
    RolParticipacionInlineGet,
    RolParticipacionPatch,
    RolParticipacionPost,
    RolParticipacionPut,
)

########################################################################################


class RolParticipacionDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        RolParticipacion,
        RolParticipacionGet,
        RolParticipacionPut,
        RolParticipacionPatch,
    ],
):
    pass


########################################################################################


class RolParticipacionListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        RolParticipacion,
        RolParticipacionFilterSet,
        RolParticipacionFilterQuery,
        RolParticipacionGet,
        RolParticipacionPost,
        Paginated[RolParticipacionGet],
    ],
):
    pass


########################################################################################


class RolParticipacionListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        RolParticipacion,
        RolParticipacionFilterSet,
        RolParticipacionFilterAllQuery,
        RolParticipacionInlineGet,
        list[RolParticipacionInlineGet],
    ],
):
    pass
