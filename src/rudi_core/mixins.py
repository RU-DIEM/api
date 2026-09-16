from http import HTTPMethod
from typing import TYPE_CHECKING, ClassVar

from api_auth.services.permissions import T_ADD_PERM, T_CHANGE_PERM, T_DELETE_PERM

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class OpenReadMixin:
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.GET: (),
        HTTPMethod.POST: (T_ADD_PERM,),
        HTTPMethod.PUT: (T_CHANGE_PERM,),
        HTTPMethod.PATCH: (T_CHANGE_PERM,),
        HTTPMethod.DELETE: (T_DELETE_PERM,),
    }


########################################################################################


class OpenWriteMixin:
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {
        HTTPMethod.GET: (),
        HTTPMethod.POST: (),
        HTTPMethod.PUT: (T_CHANGE_PERM,),
        HTTPMethod.PATCH: (T_CHANGE_PERM,),
        HTTPMethod.DELETE: (T_DELETE_PERM,),
    }


########################################################################################


class ReadOnlyMixin:
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = {HTTPMethod.GET: ()}
