from typing import TYPE_CHECKING

from .movimiento import MovimientoPunto
from .regla import ReglaPuntuacion

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "MovimientoPunto",
    "ReglaPuntuacion",
)
