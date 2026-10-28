from typing import TYPE_CHECKING, override

from asgiref.sync import sync_to_async
from django.utils.timezone import now

from api_core.services.operations import ForeignKeyCreateOperation
from rudi_estados.enums import ActorTypes
from rudi_estados.services.catalogo import initial_estado_id
from rudi_estados.services.transicion import transicionar

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet

    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel
    from rudi_portafolio.models import Propuesta

########################################################################################


class PropuestaCreateOperation[Get: DTO, Post: DTO](
    ForeignKeyCreateOperation[Get, Post],
):
    """
    A proposal starts in the initial state; its code comes from the trigger.
    """

    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        estado_id: UUID = await sync_to_async(func=initial_estado_id)("propuesta")

        return await super().execute(data | {"estado_id": estado_id})


def cerrar_propuesta(
    *,
    desenlace: str,
    motivo_descripcion: str,
    motivo_id: UUID,
    propuesta_id: UUID,
    qs: QuerySet,
) -> Propuesta:
    # any terminal state closes it; `trg_propuesta_estado_coherente` pairs the
    # state with `cerrada_at`, so a non-terminal outcome is refused there
    return transicionar(
        actor=ActorTypes.ADMIN,
        campo="desenlace",
        cerrada_at=now(),
        codigo=desenlace,
        entidad="propuesta",
        motivo_descripcion=motivo_descripcion,
        motivo_id=motivo_id,
        pk=propuesta_id,
        qs=qs,
    )
