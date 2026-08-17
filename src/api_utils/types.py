from typing import TYPE_CHECKING, ClassVar, Protocol, TypeVar

from django.http import HttpRequest

if TYPE_CHECKING:
    from django.db.models import Manager, QuerySet
    from django.db.models.options import Options

    from api_auth.models import ApiUser
    from api_core.models.base import ApiModel
    from api_core.schemas.get import PrimaryKey

    from ty_extensions import Intersection

########################################################################################


class AuthenticatedHttpRequest(HttpRequest):
    user: ApiUser


########################################################################################


class ParsedHttpRequest(HttpRequest):
    method: str


########################################################################################


class TypedDjangoModel(Protocol):
    pk: PrimaryKey

    objects: ClassVar[Intersection[Manager, QuerySet]]

    _default_manager: ClassVar[Intersection[Manager, QuerySet]]

    _meta: ClassVar[Options]


########################################################################################

# GRACIAS PYTHON POR!!!
# AMO LOS SISTEMAS DE TIPOS!!!!!

T = TypeVar(  # ruff: ignore[type-name-incorrect-variance]
    covariant=True,
    infer_variance=False,
    name="T",
)

type DatabaseModel[T: TypedDjangoModel] = ApiModel | T

type UsableHttpRequest = Intersection[AuthenticatedHttpRequest, ParsedHttpRequest]
