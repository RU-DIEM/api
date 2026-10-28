from typing import TYPE_CHECKING

from .notificacion import Notificacion

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = ("Notificacion",)
