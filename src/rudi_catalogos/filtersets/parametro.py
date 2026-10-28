from typing import TYPE_CHECKING

from django_filters import OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter, TypedChoiceFilter
from api_core.filtersets import ApiSoftDeleteFilterSet
from rudi_catalogos.enums import ParametroGrupoTypes, ParametroTypes
from rudi_catalogos.models import Parametro

if TYPE_CHECKING:
    from django.db.models import Model

########################################################################################


class ParametroFilterSet(ApiSoftDeleteFilterSet):
    codigo = LoweredFilter()

    grupo = TypedChoiceFilter(enum=ParametroGrupoTypes)
    tipo = TypedChoiceFilter(enum=ParametroTypes)

    updated_by = UUIDFilter()

    search = LoweredSearchFilter("codigo", "descripcion")

    order = OrderingFilter(fields=("codigo", "grupo"))

    class Meta(ApiSoftDeleteFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        model: type[Model] = Parametro
