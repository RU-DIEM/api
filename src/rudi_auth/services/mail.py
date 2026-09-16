from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.core.mail import send_mail
from django.db.transaction import on_commit

from api_exceptions.errors import BadRequestError, NotFoundError
from rudi_catalogos.models import PlantillaMensaje

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
    plantilla: PlantillaMensaje = await load_plantilla(codigo)

    asunto, cuerpo = render_plantilla(plantilla, context)

    await sync_to_async(func=on_commit)(
        lambda: send_mail(
            fail_silently=True,
            from_email=None,
            message=cuerpo,
            recipient_list=[to],
            subject=asunto,
        ),
    )
