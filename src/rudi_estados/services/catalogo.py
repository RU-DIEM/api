from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist

from api_exceptions.enums import BadRequestErrorTypes, RequestScopes
from api_exceptions.errors import BadRequestError, ConflictError
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


def resolve_estado_id(entidad: str, codigo: str, *, campo: str | None = None) -> UUID:
    """
    Look up an active state by its stable `codigo`.

    Services name states by code, never by id: ids differ between databases,
    codes are seeded and read-only (`trg_readonly_codigo`).

    Args:
        entidad: The state domain, a key of `ESTADOS`.
        codigo: The state's code.
        campo: The body field the code came from, when a client sent it; a
            missing state is then the client's mistake (`400`), not a
            configuration gap (`409`).

    Returns:
        The state's primary key.

    Raises:
        BadRequestError: *campo* names a state that does not exist.
        ConflictError: A state a service relies on is not configured.

    """  # ruff: ignore[docstring-extraneous-exception]

    try:
        return (
            ESTADOS[entidad]
            .objects.values_list("pk", flat=True)
            .get(codigo=codigo, is_active=True)
        )
    except ObjectDoesNotExist as e:
        if campo is not None:
            raise BadRequestError(
                field_errors={campo: f"No hay un estado activo `{codigo}`."},
                type=BadRequestErrorTypes.FAILED_VALIDATION,
            ).scoped(RequestScopes.BODY) from e

        raise ConflictError(
            detail=f"El estado `{codigo}` de `{entidad}` no está configurado.",
        ) from e


########################################################################################


def initial_estado_id(entidad: str, source: str | None = None) -> UUID:
    """
    Look up the state a new row starts in, per input source where it applies.

    Returns:
        The state's primary key.

    Raises:
        ConflictError: No initial state is configured.

    """

    qs = ESTADOS[entidad].objects.filter(initial=True, is_active=True)

    if source is not None:
        qs = qs.filter(source=source)

    try:
        return qs.values_list("pk", flat=True).get()
    except ObjectDoesNotExist as e:
        raise ConflictError(
            detail=f"No hay un estado inicial de `{entidad}` configurado.",
        ) from e
