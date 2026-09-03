from typing import TYPE_CHECKING

from django_filters import BooleanFilter, FilterSet, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter, TypedChoiceFilter
from rudi_catalogos.enums import ParametroGrupoTypes, ParametroTypes
from rudi_catalogos.models import Parametro

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class ParametroFilterSet(FilterSet):
    id = UUIDFilter()

    codigo = LoweredFilter()

    grupo = TypedChoiceFilter(enum=ParametroGrupoTypes)
    tipo = TypedChoiceFilter(enum=ParametroTypes)

    is_active = BooleanFilter()

    updated_by = UUIDFilter()

    search = LoweredSearchFilter("codigo", "descripcion")

    order = OrderingFilter(fields=("codigo", "grupo"))

    class Meta:
        fields: Sequence[str] = ()
        model: type[Model] = Parametro
