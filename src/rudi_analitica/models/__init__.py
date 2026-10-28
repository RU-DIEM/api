from typing import TYPE_CHECKING

from .indicador import IndicadorPeriodo
from .vistas import (
    MvCoberturaCarrera,
    MvParticipacionActividad,
    MvParticipanteUnicoAnio,
    MvSaldoPuntosUser,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "IndicadorPeriodo",
    "MvCoberturaCarrera",
    "MvParticipacionActividad",
    "MvParticipanteUnicoAnio",
    "MvSaldoPuntosUser",
)
