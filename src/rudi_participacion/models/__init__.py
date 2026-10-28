from typing import TYPE_CHECKING

from .asignacion import AsignacionMentor
from .equipo import Equipo, EquipoMiembro
from .inscripcion import Inscripcion
from .participacion import Participacion, Reconocimiento

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "AsignacionMentor",
    "Equipo",
    "EquipoMiembro",
    "Inscripcion",
    "Participacion",
    "Reconocimiento",
)
