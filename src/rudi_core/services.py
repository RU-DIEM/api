from functools import cache
from typing import TYPE_CHECKING, override

from api_core.services.operations import FlatCreateOperation, FlatUpdateOperation

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from api_core.schemas.base import DTO
    from api_core.services.mappers import ModelMapper
    from api_utils.types import DatabaseModel

########################################################################################


@cache
def relation_attnames(model: type[DatabaseModel]) -> dict[str, str]:
    return {
        field.name: field.attname
        for field in model._meta.concrete_fields  # ruff: ignore[private-member-access]
        if field.is_relation
    }


########################################################################################


def resolve_relations(data: dict, model: type[DatabaseModel]) -> dict:
    attnames: dict[str, str] = relation_attnames(model)

    return {attnames.get(name, name): value for name, value in data.items()}


########################################################################################


class RelationCreateOperation[Get: DTO, Post: DTO](FlatCreateOperation[Get, Post]):
    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        model: type[DatabaseModel] = self.qs.model  # ty: ignore[invalid-assignment]

        return await super().execute(resolve_relations(data, model))


########################################################################################


class RelationUpdateOperation[Get: DTO, Post: DTO](FlatUpdateOperation[Get, Post]):
    __slots__ = ()

    @override
    async def execute(self, data: dict, lookup: dict) -> DatabaseModel:
        model: type[DatabaseModel] = self.qs.model  # ty: ignore[invalid-assignment]

        return await super().execute(resolve_relations(data, model), lookup)


########################################################################################


class ScopedCreateOperation[Get: DTO, Post: DTO](RelationCreateOperation[Get, Post]):
    __slots__ = ("defaults",)

    def __init__(
        self,
        *fields: str,
        mapper: ModelMapper[Get],
        schema: type[Get],
        defaults: dict,
        qs: QuerySet,
    ) -> None:
        super().__init__(*fields, mapper=mapper, schema=schema, qs=qs)

        self.defaults: dict = defaults

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        return await super().execute(data | self.defaults)
