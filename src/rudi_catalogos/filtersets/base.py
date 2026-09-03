from typing import TYPE_CHECKING, Final

from django_filters import BooleanFilter, FilterSet, OrderingFilter, UUIDFilter

from api_core.filters import LoweredFilter, LoweredSearchFilter

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

CATALOGO_SEARCH: Final[Sequence[str]] = ("codigo", "descripcion", "etiqueta")

CATALOGO_SEARCH_NO_DESC: Final[Sequence[str]] = ("codigo", "etiqueta")

########################################################################################


class RudiCatalogoFilterSet(FilterSet):
    id = UUIDFilter()

    codigo = LoweredFilter()
    etiqueta = LoweredFilter()

    is_active = BooleanFilter()

    search = LoweredSearchFilter(*CATALOGO_SEARCH)

    order = OrderingFilter(fields=("codigo", "created_at", "etiqueta"))

    class Meta:
        fields: Sequence[str] = ()
