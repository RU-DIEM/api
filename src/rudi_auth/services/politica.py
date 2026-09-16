from typing import TYPE_CHECKING, override

from asgiref.sync import sync_to_async
from django.db.transaction import atomic

from api_exceptions.errors import ApiError
from rudi_auth.models import PoliticaPrivacidad
from rudi_core.services import RelationCreateOperation

if TYPE_CHECKING:
    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel

########################################################################################


async def load_politica_vigente() -> PoliticaPrivacidad:
    politica: PoliticaPrivacidad | None = await PoliticaPrivacidad.objects.filter(
        vigente_hasta__isnull=True,
    ).afirst()

    if politica is None:
        raise ApiError(detail="No hay una política de privacidad vigente.")

    return politica


########################################################################################


class PoliticaCreateOperation[Get: DTO, Post: DTO](RelationCreateOperation[Get, Post]):
    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        return await sync_to_async(func=self.persist)(data)

    @atomic
    def persist(self, data: dict) -> DatabaseModel:
        if data.get("vigente_hasta") is None:
            PoliticaPrivacidad.objects.filter(vigente_hasta__isnull=True).update(
                vigente_hasta=data["vigente_desde"],
            )

        obj: DatabaseModel = self.qs.create(**data)

        return self.qs.get(pk=obj.pk)
