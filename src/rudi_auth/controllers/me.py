from collections.abc import Sequence
from http import HTTPMethod
from typing import ClassVar, override

from django.db.models import QuerySet
from dmr import Body

from api_core.controllers.mixins import ReadOnlyMixin
from api_core.controllers.models import (
    ModelController,
    ModelReadOnlyListController,
)
from api_core.controllers.providers import QuerySetProvider
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.pagination import Paginated
from api_core.services.operations import (
    FlatRetrieveOperation,
    FlatUpdateOperation,
    RetrieveOperation,
    UpdateOperation,
)
from api_exceptions.errors import NotFoundError
from rudi_auth.filtersets.identificador import IdentificadorUserFilterSet
from rudi_auth.models import ConsentimientoDatos, IdentificadorUser, RudiUser
from rudi_auth.schemas.consentimiento import ConsentimientoDatosGet
from rudi_auth.schemas.identificador import (
    IdentificadorUserFilterQuery,
    IdentificadorUserGet,
)
from rudi_auth.schemas.user import RudiUserGet, RudiUserPatch, UserPath

########################################################################################


class SelfScopedMixin(QuerySetProvider):
    self_field: ClassVar[str] = "user"

    @override
    def build_qs(self) -> QuerySet:
        scope: dict = {
            self.__class__.self_field: self.request.user.pk,  # ty: ignore[unresolved-attribute]
        }

        return super().build_qs().filter(**scope)


########################################################################################


class MeDetailController(
    SelfScopedMixin,
    ModelController[
        CustomPydanticFastSerializer,
        RudiUser,
        RudiUserGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.GET: (),
        HTTPMethod.PATCH: (),
    }

    retrieve_operation: ClassVar[type[RetrieveOperation]] = FlatRetrieveOperation
    update_operation: ClassVar[type[UpdateOperation]] = FlatUpdateOperation

    async def get(self) -> RudiUserGet:
        return await self.build_operation(self.retrieve_operation).run(
            path=self.lookup(),  # ty: ignore[invalid-argument-type]
        )

    async def patch(self, parsed_body: Body[RudiUserPatch]) -> RudiUserGet:
        return await self.build_operation(
            self.update_operation,
            partial=True,
        ).run(
            body=parsed_body,
            path=self.lookup(),  # ty: ignore[invalid-argument-type]
        )

    def lookup(self) -> UserPath:
        return UserPath(user_id=self.request.user.pk)


########################################################################################


class MeConsentimientoController(
    SelfScopedMixin,
    ModelController[
        CustomPydanticFastSerializer,
        ConsentimientoDatos,
        ConsentimientoDatosGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {HTTPMethod.GET: ()}

    self_field: ClassVar[str] = "user__user"

    async def get(self) -> ConsentimientoDatosGet:
        consentimiento: ConsentimientoDatos | None = await self.qs.afirst()

        if consentimiento is None:
            raise NotFoundError(
                detail="Su cuenta no tiene un consentimiento registrado.",
            )

        return self.mapper(consentimiento, self.schema)


########################################################################################


class MeIdentificadoresController(
    ReadOnlyMixin,
    SelfScopedMixin,
    ModelReadOnlyListController[
        CustomPydanticFastSerializer,
        IdentificadorUser,
        IdentificadorUserFilterSet,
        IdentificadorUserFilterQuery,
        IdentificadorUserGet,
        Paginated[IdentificadorUserGet],
    ],
):
    self_field: ClassVar[str] = "user__user"
