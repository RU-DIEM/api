from api_core.controllers.mixins import OpenReadMixin
from api_core.controllers.models import (
    ModelDetailController,
    ModelListAllController,
    ModelListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from rudi_catalogos.filtersets.mentor import TipoMentorFilterSet
from rudi_catalogos.models import TipoMentor
from rudi_catalogos.schemas.mentor import (
    TipoMentorFilterAllQuery,
    TipoMentorFilterQuery,
    TipoMentorGet,
    TipoMentorInlineGet,
    TipoMentorPatch,
    TipoMentorPost,
    TipoMentorPut,
)

########################################################################################


class TipoMentorDetailController(
    OpenReadMixin,
    ModelDetailController[
        CustomPydanticFastSerializer,
        TipoMentor,
        TipoMentorGet,
        TipoMentorPut,
        TipoMentorPatch,
    ],
):
    pass


########################################################################################


class TipoMentorListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        TipoMentor,
        TipoMentorFilterSet,
        TipoMentorFilterQuery,
        TipoMentorGet,
        TipoMentorPost,
        Paginated[TipoMentorGet],
    ],
):
    pass


########################################################################################


class TipoMentorListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        TipoMentor,
        TipoMentorFilterSet,
        TipoMentorFilterAllQuery,
        TipoMentorInlineGet,
        list[TipoMentorInlineGet],
    ],
):
    pass
