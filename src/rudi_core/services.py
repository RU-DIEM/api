from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db import IntegrityError

from api_exceptions.enums import RequestScopes
from api_exceptions.errors import ConflictError

if TYPE_CHECKING:
    from collections.abc import Callable

########################################################################################


async def ejecutar[T](func: Callable[..., T], /, **kwargs: object) -> T:
    """
    Run a synchronous service from an async controller.

    A service opens its own `atomic` block, so a deferred trigger or foreign
    key can only fail when that block commits, after the service's own
    `try`; this catches it there and answers `409` instead of `500`.

    Returns:
        Whatever *func* returns.

    """

    try:
        return await sync_to_async(func=func)(**kwargs)
    except IntegrityError as i:
        raise ConflictError.from_integrity_error(i).scoped(RequestScopes.BODY) from i
