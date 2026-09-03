from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.area import AreaExperienciaFilterSet
from rudi_catalogos.models import AreaExperiencia
from rudi_catalogos.schemas.area import (
    AreaExperienciaFilterAllQuery,
    AreaExperienciaFilterQuery,
    AreaExperienciaGet,
    AreaExperienciaInlineGet,
    AreaExperienciaPatch,
    AreaExperienciaPost,
    AreaExperienciaPut,
)
from rudi_core.mixins import OpenReadMixin

########################################################################################


class AreaExperienciaDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        AreaExperiencia,
        AreaExperienciaGet,
        AreaExperienciaPut,
        AreaExperienciaPatch,
    ],
):
    pass


########################################################################################


class AreaExperienciaListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        AreaExperiencia,
        AreaExperienciaFilterSet,
        AreaExperienciaFilterQuery,
        AreaExperienciaGet,
        AreaExperienciaPost,
        Paginated[AreaExperienciaGet],
    ],
):
    pass


########################################################################################


class AreaExperienciaListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        AreaExperiencia,
        AreaExperienciaFilterSet,
        AreaExperienciaFilterAllQuery,
        AreaExperienciaInlineGet,
        list[AreaExperienciaInlineGet],
    ],
):
    pass
