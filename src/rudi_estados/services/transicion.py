from typing import TYPE_CHECKING

from rudi_estados.enums import ActorTypes
from rudi_estados.models import (
    TransicionEstadoActividad,
    TransicionEstadoInscripcion,
    TransicionEstadoParticipacion,
    TransicionEstadoPropuesta,
)

from .catalogo import ESTADOS

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet

    from rudi_estados.models.base import RudiTransicion

########################################################################################

TRANSICIONES: dict[str, type[RudiTransicion]] = {
    "actividad": TransicionEstadoActividad,
    "inscripcion": TransicionEstadoInscripcion,
    "participacion": TransicionEstadoParticipacion,
    "propuesta": TransicionEstadoPropuesta,
}

########################################################################################


def transiciones_validas(
    *,
    actor: ActorTypes | str,
    entidad: str,
    from_id: UUID,
) -> QuerySet:
    """
    List the transitions *actor* may take out of state *from_id*.

    Returns:
        The active transitions, as a queryset.

    """

    value: str = actor.value if isinstance(actor, ActorTypes) else actor

    return TRANSICIONES[entidad].objects.filter(
        actor=value,
        from_estado_id=from_id,
        is_active=True,
    )


########################################################################################


def exige_motivo(
    *,
    actor: ActorTypes | str,
    entidad: str,
    from_id: UUID,
    to_id: UUID,
) -> bool:
    """
    Tell whether moving from *from_id* to *to_id* needs a reason.

    Entities with a transition catalog declare it on the transition;
    the rest (`usuario`, `constancia`, `asignacion_mentor`) on the target state.

    Returns:
        Whether the change must carry a `Motivo`.

    """

    if entidad in TRANSICIONES:
        return (
            transiciones_validas(
                actor=actor,
                entidad=entidad,
                from_id=from_id,
            )
            .filter(require_motivo=True, to_estado_id=to_id)
            .exists()
        )

    estado = ESTADOS[entidad]

    if not any(f.name == "require_motivo" for f in estado._meta.concrete_fields):  # ruff: ignore[private-member-access]
        return False

    return estado.objects.filter(pk=to_id, require_motivo=True).exists()
