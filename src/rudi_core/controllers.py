from typing import ClassVar, override

from django.db.models import QuerySet
from django_filters import FilterSet
from dmr import Body
from dmr.serializer import BaseSerializer

from api_core.controllers.models import (
    ModelListController,
    ModelReadOnlyListController,
    ModelReadUpdateDetailController,
)
from api_core.controllers.providers import QuerySetProvider
from api_core.schemas.base import DTO
from api_core.schemas.filters import PaginatedFilterQuery
from api_core.schemas.path import InstancePath, UuidInstancePath
from api_core.services.operations import CreateOperation, UpdateOperation
from api_utils.types import DatabaseModel

from .services import (
    RelationCreateOperation,
    RelationUpdateOperation,
    ScopedCreateOperation,
)

########################################################################################


class ParentScopedMixin(QuerySetProvider):
    parent_field: ClassVar[str]
    parent_param: ClassVar[str]

    @property
    def parent_id(self) -> str:
        return self.kwargs[self.__class__.parent_param]  # ty: ignore[unresolved-attribute]

    @override
    def build_qs(self) -> QuerySet:
        scope: dict = {self.__class__.parent_field: self.parent_id}

        return super().build_qs().filter(**scope)


########################################################################################


class ScopedDetailController[
    Serializer: BaseSerializer,
    Model: DatabaseModel,
    Get: DTO,
    Put: DTO,
    Patch: DTO,
    PathSchema: InstancePath = UuidInstancePath,
](
    ParentScopedMixin,
    ModelReadUpdateDetailController[Serializer, Model, Get, Put, Patch, PathSchema],
):
    update_operation: ClassVar[type[UpdateOperation]] = RelationUpdateOperation


########################################################################################


class ScopedListController[
    Serializer: BaseSerializer,
    Model: DatabaseModel,
    ModelFilter: FilterSet,
    FilterQuery: PaginatedFilterQuery,
    Get: DTO,
    Post: DTO,
    PaginatedGet: DTO,
](
    ParentScopedMixin,
    ModelListController[
        Serializer,
        Model,
        ModelFilter,
        FilterQuery,
        Get,
        Post,
        PaginatedGet,
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ScopedCreateOperation

    @override
    async def post(self, parsed_body: Body[Post]) -> Get:
        return await self.build_operation(
            self.create_operation,
            defaults={f"{self.__class__.parent_field}_id": self.parent_id},
        ).run(body=parsed_body)


########################################################################################


class ScopedReadOnlyListController[
    Serializer: BaseSerializer,
    Model: DatabaseModel,
    ModelFilter: FilterSet,
    FilterQuery: PaginatedFilterQuery,
    Get: DTO,
    PaginatedGet: DTO,
](
    ParentScopedMixin,
    ModelReadOnlyListController[
        Serializer,
        Model,
        ModelFilter,
        FilterQuery,
        Get,
        PaginatedGet,
    ],
):
    pass


########################################################################################


class RelationDetailController[
    Serializer: BaseSerializer,
    Model: DatabaseModel,
    Get: DTO,
    Put: DTO,
    Patch: DTO,
    PathSchema: InstancePath = UuidInstancePath,
](ModelReadUpdateDetailController[Serializer, Model, Get, Put, Patch, PathSchema]):
    update_operation: ClassVar[type[UpdateOperation]] = RelationUpdateOperation


########################################################################################


class RelationListController[
    Serializer: BaseSerializer,
    Model: DatabaseModel,
    ModelFilter: FilterSet,
    FilterQuery: PaginatedFilterQuery,
    Get: DTO,
    Post: DTO,
    PaginatedGet: DTO,
](
    ModelListController[
        Serializer,
        Model,
        ModelFilter,
        FilterQuery,
        Get,
        Post,
        PaginatedGet,
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = RelationCreateOperation
