from typing import TYPE_CHECKING

from .constancia import Constancia, ConstanciaParticipacion
from .plantilla import PlantillaConstancia

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "Constancia",
    "ConstanciaParticipacion",
    "PlantillaConstancia",
)
