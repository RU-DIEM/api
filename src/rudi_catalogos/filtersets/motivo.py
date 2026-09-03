from typing import TYPE_CHECKING

from django_filters import BooleanFilter

from api_core.filters import LoweredSearchFilter, TypedChoiceFilter
from rudi_catalogos.enums import MotivoAmbitoTypes, MotivoVisibilidadTypes
from rudi_catalogos.models import Motivo

from .base import CATALOGO_SEARCH_NO_DESC, RudiCatalogoFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class MotivoFilterSet(RudiCatalogoFilterSet):
    ambito = TypedChoiceFilter(enum=MotivoAmbitoTypes)
    visibilidad = TypedChoiceFilter(enum=MotivoVisibilidadTypes)

    require_descripcion = BooleanFilter()

    search = LoweredSearchFilter(*CATALOGO_SEARCH_NO_DESC)

    class Meta(RudiCatalogoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = Motivo
