from typing import TYPE_CHECKING

from api_core.filters import LoweredFilter, LoweredSearchFilter
from rudi_catalogos.models import PlantillaMensaje

from .base import CATALOGO_SEARCH_NO_DESC, RudiCatalogoFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class PlantillaMensajeFilterSet(RudiCatalogoFilterSet):
    asunto = LoweredFilter()

    search = LoweredSearchFilter(*CATALOGO_SEARCH_NO_DESC, "asunto", "cuerpo")

    class Meta(RudiCatalogoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = PlantillaMensaje
