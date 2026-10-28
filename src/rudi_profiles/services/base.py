from typing import TYPE_CHECKING, override

from asgiref.sync import sync_to_async
from django.db.transaction import atomic

from api_core.services.operations import CreateOperation
from api_core.services.relations import resolve_fk_attnames
from rudi_auth.models import RudiUser
from rudi_estados.enums import ActorTypes
from rudi_estados.services.actor import set_actor
from rudi_estados.services.catalogo import resolve_estado_id

if TYPE_CHECKING:
    from uuid import UUID

    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel

########################################################################################


def activar_persona(user_id: UUID) -> None:
    """
    Move a verified person to `activa` once they declare a profile (estados.md).

    Only `verificada` moves: a suspended person stays suspended, and an active
    one adding a second profile has nothing to change.
    """

    set_actor(ActorTypes.SYS)

    RudiUser.objects.filter(estado__codigo="verificada", pk=user_id).update(
        estado_id=resolve_estado_id("usuario", "activa"),
    )


class ProfileCreateOperation[Get: DTO, Post: DTO](CreateOperation[Get, Post]):
    """
    Create a profile sent with bare foreign key IDs, activating its person.
    """

    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        model: type[DatabaseModel] = self.qs.model  # ty: ignore[invalid-assignment]

        return await sync_to_async(func=self.persist)(resolve_fk_attnames(data, model))

    @atomic
    def persist(self, data: dict) -> DatabaseModel:
        profile: DatabaseModel = self.qs.model.objects.create(**data)  # ty: ignore[unresolved-attribute]

        activar_persona(profile.user_id)  # ty: ignore[unresolved-attribute]

        return self.qs.get(pk=profile.pk)
