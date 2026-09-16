from typing import TYPE_CHECKING

from api_exceptions.errors import NotFoundError
from rudi_estados.models import EstadoConsentimiento, EstadoRudiUser

if TYPE_CHECKING:
    from rudi_estados.enums import InputSourceTypes

########################################################################################


async def initial_estado_consentimiento(
    source: InputSourceTypes,
) -> EstadoConsentimiento:
    estado: EstadoConsentimiento | None = await EstadoConsentimiento.objects.filter(
        initial=True,
        is_active=True,
        source=source,
    ).afirst()

    if estado is None:
        raise NotFoundError(field_errors={"source": source})

    return estado


########################################################################################


async def initial_estado_user() -> EstadoRudiUser:
    estado: EstadoRudiUser | None = await EstadoRudiUser.objects.filter(
        initial=True,
        is_active=True,
    ).afirst()

    if estado is None:
        raise NotFoundError(detail="No hay un estado inicial de cuenta configurado.")

    return estado
