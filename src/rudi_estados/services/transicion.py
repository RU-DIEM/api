from typing import TYPE_CHECKING

from django.db.transaction import atomic

from api_exceptions.enums import RequestScopes
from api_exceptions.errors import NotFoundError
from rudi_estados.enums import ActorTypes
from rudi_estados.models import (
    TransicionEstadoActividad,
    TransicionEstadoInscripcion,
    TransicionEstadoParticipacion,
    TransicionEstadoPropuesta,
)

from .actor import set_actor
from .catalogo import ESTADOS, resolve_estado_id

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet

    from api_utils.types import DatabaseModel
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


########################################################################################


@atomic
def transicionar(  # ruff: ignore[too-many-arguments]
    *,
    actor: ActorTypes | str,
    campo: str | None = None,
    codigo: str,
    entidad: str,
    pk: UUID,
    qs: QuerySet,
    **cambios: object,
) -> DatabaseModel:
    """
    Move one row to the state with *codigo*, acting as *actor*.

    The service only names the target; whether the move is legal is the
    triggers' call (`trg_<tabla>_transicion_valida` reads the actor this
    sets). *cambios* are the columns that change with the state, such as the
    closing timestamp and its reason.

    Args:
        actor: Who is acting, as the transition catalog names it.
        campo: The body field *codigo* came from, if the client chose it.
        codigo: The target state's code.
        entidad: The state domain, a key of `ESTADOS`.
        pk: The row to move.
        qs: The queryset to read the moved row back from.
        **cambios: Other columns to write in the same `UPDATE`.

    Returns:
        The moved row, read back through *qs*.

    Raises:
        NotFoundError: There is no row *pk*.

    """  # ruff: ignore[docstring-extraneous-exception]

    set_actor(actor)

    estado_id: UUID = resolve_estado_id(entidad, codigo, campo=campo)

    if not qs.model.objects.filter(pk=pk).update(estado_id=estado_id, **cambios):  # ty: ignore[unresolved-attribute]
        raise NotFoundError(field_errors={f"{entidad}_id": str(pk)}).scoped(
            RequestScopes.BODY,
        )

    return qs.get(pk=pk)
