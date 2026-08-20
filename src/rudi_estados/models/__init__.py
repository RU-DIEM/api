from typing import TYPE_CHECKING

from .actividad import EstadoActividad, TransicionEstadoActividad
from .asignacion import EstadoAsignacionMentor
from .consentimiento import EstadoConsentimiento
from .constancia import EstadoConstancia
from .inscripcion import EstadoInscripcion, TransicionEstadoInscripcion
from .participacion import EstadoParticipacion, TransicionEstadoParticipacion
from .propuesta import EstadoPropuesta, TransicionEstadoPropuesta
from .user import EstadoRudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "EstadoActividad",
    "EstadoAsignacionMentor",
    "EstadoConsentimiento",
    "EstadoConstancia",
    "EstadoInscripcion",
    "EstadoParticipacion",
    "EstadoPropuesta",
    "EstadoRudiUser",
    "TransicionEstadoActividad",
    "TransicionEstadoInscripcion",
    "TransicionEstadoParticipacion",
    "TransicionEstadoPropuesta",
)
