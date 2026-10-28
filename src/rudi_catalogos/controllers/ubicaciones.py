from api_core.controllers.mixins import ReadOnlyMixin
from api_core.controllers.models import ModelListAllController
from api_core.controllers.serializers import CustomPydanticFastSerializer
from rudi_catalogos.filtersets.ubicaciones import (
    DepartamentoFilterSet,
    MunicipioFilterSet,
)
from rudi_catalogos.models import Departamento, Municipio
from rudi_catalogos.schemas.ubicaciones import (
    DepartamentoFilterAllQuery,
    DepartamentoGet,
    MunicipioFilterAllQuery,
    MunicipioGet,
)

########################################################################################


class DepartamentoListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Departamento,
        DepartamentoFilterSet,
        DepartamentoFilterAllQuery,
        DepartamentoGet,
        list[DepartamentoGet],
    ],
):
    pass


########################################################################################


class MunicipioListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Municipio,
        MunicipioFilterSet,
        MunicipioFilterAllQuery,
        MunicipioGet,
        list[MunicipioGet],
    ],
):
    pass
