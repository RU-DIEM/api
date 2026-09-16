from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.utils.timezone import now

from api_exceptions.enums import RequestScopes
from api_exceptions.errors import NotFoundError
from rudi_profiles.models import MentorProfile

if TYPE_CHECKING:
    from uuid import UUID

    from api_auth.models import ApiUser

########################################################################################


async def confirmar_mentor(actor: ApiUser, profile_id: UUID) -> None:
    profile: MentorProfile | None = await MentorProfile.objects.filter(
        pk=profile_id,
    ).afirst()

    if profile is None:
        raise NotFoundError(field_errors={"id": str(profile_id)}).scoped(
            RequestScopes.PATH,
        )

    if profile.confirmado_at is not None:
        return

    @atomic
    def persist() -> None:
        profile.confirmado_at = now()
        profile.confirmado_por = actor

        profile.save(
            update_fields=("confirmado_at", "confirmado_por", "updated_at"),
        )

    await sync_to_async(func=persist)()
