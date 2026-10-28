from typing import TYPE_CHECKING

from rudi_estados.models import (
    EstadoActividad,
    EstadoAsignacionMentor,
    EstadoConsentimiento,
    EstadoConstancia,
    EstadoInscripcion,
    EstadoParticipacion,
    EstadoPropuesta,
    EstadoRudiUser,
)

if TYPE_CHECKING:
    from uuid import UUID

    from rudi_estados.models.base import RudiEstado

########################################################################################

ESTADOS: dict[str, type[RudiEstado]] = {
    "actividad": EstadoActividad,
    "asignacion_mentor": EstadoAsignacionMentor,
    "consentimiento": EstadoConsentimiento,
    "constancia": EstadoConstancia,
    "inscripcion": EstadoInscripcion,
    "participacion": EstadoParticipacion,
    "propuesta": EstadoPropuesta,
    "usuario": EstadoRudiUser,
}

########################################################################################


def resolve_estado_id(entidad: str, codigo: str) -> UUID:
    """
    Look up an active state by its stable `codigo`.

    Services name states by code, never by id: ids differ between databases,
    codes are seeded and read-only (`trg_readonly_codigo`).

    Returns:
        The state's primary key.

    """

    return (
        ESTADOS[entidad]
        .objects.values_list("pk", flat=True)
        .get(
            codigo=codigo,
            is_active=True,
        )
    )
