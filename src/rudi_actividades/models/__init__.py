from typing import TYPE_CHECKING

from .actividad import Actividad, ActividadResponsable
from .programa import Programa

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "Actividad",
    "ActividadResponsable",
    "Programa",
)
