from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.utils.timezone import now

from api_exceptions.enums import RequestScopes
from api_exceptions.errors import NotFoundError
from rudi_profiles.models import Institucion

if TYPE_CHECKING:
    from uuid import UUID

########################################################################################


async def normalizar_institucion(institucion_id: UUID) -> None:
    institucion: Institucion | None = await Institucion.objects.filter(
        pk=institucion_id,
    ).afirst()

    if institucion is None:
        raise NotFoundError(field_errors={"id": str(institucion_id)}).scoped(
            RequestScopes.PATH,
        )

    if institucion.normalizada_at is not None:
        return

    @atomic
    def persist() -> None:
        institucion.normalizada_at = now()

        institucion.save(update_fields=("normalizada_at", "updated_at"))

    await sync_to_async(func=persist)()
