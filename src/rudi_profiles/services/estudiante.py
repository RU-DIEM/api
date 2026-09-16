from typing import TYPE_CHECKING, override

from asgiref.sync import sync_to_async
from django.db.transaction import atomic

from api_core.services.operations import CreateOperation
from api_utils.db import set_immediate_constraints
from rudi_profiles.models import EstudianteCarrera, EstudianteProfile

if TYPE_CHECKING:
    from collections.abc import Sequence

    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel

########################################################################################


class EstudianteProfileCreateOperation[Get: DTO, Post: DTO](CreateOperation[Get, Post]):
    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        return await sync_to_async(func=self.persist)(data)

    @atomic
    def persist(self, data: dict) -> DatabaseModel:
        carreras: Sequence[dict] = data["carreras"]

        profile: EstudianteProfile = EstudianteProfile.objects.create(
            user_id=data["user"],
        )

        principal: bool = any(carrera["is_main"] for carrera in carreras)

        for index, carrera in enumerate(carreras):
            EstudianteCarrera.objects.create(
                carrera_id=carrera["carrera"],
                cerrada_at=carrera["cerrada_at"],
                iniciada_en=carrera["iniciada_en"],
                is_main=(carrera["is_main"] or (not principal and index == 0)),
                nivel=carrera["nivel"],
                profile=profile,
            )

        set_immediate_constraints()

        return self.qs.get(pk=profile.pk)
