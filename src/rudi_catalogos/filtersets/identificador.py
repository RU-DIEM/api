from typing import TYPE_CHECKING

from django_filters import BooleanFilter

from api_core.filters import LoweredSearchFilter
from rudi_catalogos.models import TipoIdentificador

from .base import CATALOGO_SEARCH_NO_DESC, RudiCatalogoFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class TipoIdentificadorFilterSet(RudiCatalogoFilterSet):
    is_institucional = BooleanFilter()

    search = LoweredSearchFilter(*CATALOGO_SEARCH_NO_DESC)

    class Meta(RudiCatalogoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = TipoIdentificador
