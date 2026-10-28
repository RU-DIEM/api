from typing import TYPE_CHECKING

from .indicador import IndicadorPeriodo

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = ("IndicadorPeriodo",)
