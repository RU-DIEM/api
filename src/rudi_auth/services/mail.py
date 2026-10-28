from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async

from api_exceptions.errors import BadRequestError, NotFoundError
from rudi_catalogos.models import PlantillaMensaje
from rudi_notificaciones.services import encolar

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


def render_plantilla(plantilla: PlantillaMensaje, context: dict) -> tuple[str, str]:
    missing: Sequence[str] = tuple(
        sorted(name for name in plantilla.variables if name not in context)  # ty: ignore[not-iterable]
    )

    if missing:
        raise BadRequestError(
            detail=(
                f"La plantilla '{plantilla.codigo}' exige variables "
                f"que no fueron provistas: {', '.join(missing)}."
            ),
        )

    asunto: str = plantilla.asunto  # ty: ignore[invalid-assignment]
    cuerpo: str = plantilla.cuerpo  # ty: ignore[invalid-assignment]

    for name in plantilla.variables:  # ty: ignore[not-iterable]
        marca: str = "{" + name + "}"
        valor: str = str(context[name])

        asunto = asunto.replace(marca, valor)
        cuerpo = cuerpo.replace(marca, valor)

    return asunto, cuerpo


########################################################################################


async def load_plantilla(codigo: str) -> PlantillaMensaje:
    plantilla: PlantillaMensaje | None = await PlantillaMensaje.objects.filter(
        codigo=codigo,
        is_active=True,
    ).afirst()

    if plantilla is None:
        raise NotFoundError(field_errors={"codigo": codigo})

    return plantilla


########################################################################################


async def send_plantilla(codigo: str, context: dict, to: str) -> None:
    """
    Render a template and queue the message (rudi_notificaciones).

    It is sent once the caller's transaction commits, and retried by
    `enviar_pendientes` if the provider fails.
    """

    plantilla: PlantillaMensaje = await load_plantilla(codigo)

    asunto, cuerpo = render_plantilla(plantilla, context)

    await sync_to_async(func=encolar)(
        asunto=asunto,
        cuerpo=cuerpo,
        destinatario=to,
        plantilla=plantilla,
    )
