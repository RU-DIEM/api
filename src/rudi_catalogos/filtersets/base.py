from typing import TYPE_CHECKING, Final

from django_filters import OrderingFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter
from api_core.filtersets import ApiSoftDeleteFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

CATALOGO_SEARCH: Final[Sequence[str]] = ("codigo", "descripcion", "etiqueta")

CATALOGO_SEARCH_NO_DESC: Final[Sequence[str]] = ("codigo", "etiqueta")

########################################################################################


class RudiCatalogoFilterSet(ApiSoftDeleteFilterSet):
    codigo = LoweredFilter()
    etiqueta = LoweredFilter()

    search = LoweredSearchFilter(*CATALOGO_SEARCH)

    order = OrderingFilter(fields=("codigo", "created_at", "etiqueta"))
