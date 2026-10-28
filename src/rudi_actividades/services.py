from typing import TYPE_CHECKING, override

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.utils.timezone import now

from api_core.services.operations import ForeignKeyCreateOperation
from rudi_actividades.models import Actividad
from rudi_estados.enums import ActorTypes
from rudi_estados.services.catalogo import initial_estado_id
from rudi_estados.services.transicion import transicionar

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID

    from django.db.models import QuerySet

    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel

########################################################################################


class ActividadCreateOperation[Get: DTO, Post: DTO](
    ForeignKeyCreateOperation[Get, Post],
):
    """
    A new activity starts in the initial state, whatever the body says.
    """

    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        estado_id: UUID = await sync_to_async(func=initial_estado_id)("actividad")

        return await super().execute(data | {"estado_id": estado_id})


########################################################################################


def cancelar_actividad(
    *,
    actividad_id: UUID,
    motivo_descripcion: str,
    motivo_id: UUID,
    qs: QuerySet,
) -> Actividad:
    # closing its live inscriptions is `trg_actividad_cancelar_inscripciones`' job
    return transicionar(
        actor=ActorTypes.ADMIN,
        cancelada_at=now(),
        codigo="cancelada",
        entidad="actividad",
        motivo_descripcion=motivo_descripcion,
        motivo_id=motivo_id,
        pk=actividad_id,
        qs=qs,
    )


########################################################################################


def transicionar_actividades(hoy: date) -> int:
    """
    Move activities along by date, acting as `sistema` (procesos.md).

    `publicada` becomes `en_curso` on `fecha_inicio`; `en_curso` becomes
    `finalizada` the day after `fecha_fin`. The transition catalog declares
    both for `sistema`, so the triggers accept them; the service only picks
    the rows.

    Returns:
        How many activities moved.

    """

    movidas: int = 0

    for desde, hasta, filtro in (
        ("publicada", "en_curso", {"fecha_inicio__lte": hoy}),
        ("en_curso", "finalizada", {"fecha_fin__lt": hoy}),
    ):
        ids = list(
            Actividad.objects.filter(
                cancelada_at__isnull=True,
                estado__codigo=desde,
                **filtro,
            ).values_list("pk", flat=True)
        )

        for pk in ids:
            # one activity the triggers refuse does not stop the others
            try:
                transicionar(
                    actor=ActorTypes.SYS,
                    codigo=hasta,
                    entidad="actividad",
                    pk=pk,
                    qs=Actividad.objects.all(),
                )
            except IntegrityError:
                continue

            movidas += 1

    return movidas
