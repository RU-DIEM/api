from dataclasses import replace
from typing import TYPE_CHECKING, ClassVar, override

from dmr.openapi import OpenAPIConfig, OpenAPIContext
from dmr.openapi.generators import OperationIdGenerator
from dmr.openapi.objects import Components

from api_auth.security import CSRF_SCHEME_NAME, CSRF_SECURITY_SCHEME
from api_core.controllers.endpoints import PathOperationIdEndpoint
from api_utils.env import OPENAPI

if TYPE_CHECKING:
    from typing import Final

    from dmr import Controller
    from dmr.metadata import EndpointMetadata

########################################################################################

OPENAPI_CONFIG: Final[OpenAPIConfig] = replace(
    OPENAPI,
    components=Components(security_schemes={CSRF_SCHEME_NAME: CSRF_SECURITY_SCHEME}),
)

########################################################################################


class PathOperationIdGenerator(OperationIdGenerator):
    """
    Name every operation after its path and what it does there.

    `/auth/user/{id}/` answering `GET` becomes `auth-user-retrieve`, so
    clients generated from the schema get names that read like the API.
    The verb comes from the controller's endpoint class.
    """

    @override
    def __call__(
        self,
        path: str,
        metadata: EndpointMetadata,
        controller_cls: type[Controller],
    ) -> str:
        endpoint_cls: type = controller_cls.endpoint_cls

        if metadata.operation_id is not None or not issubclass(
            endpoint_cls,
            PathOperationIdEndpoint,
        ):
            return super().__call__(path, metadata, controller_cls)

        operation_id: str = "-".join((
            *endpoint_cls.get_segments(path),
            endpoint_cls.get_action(metadata.method, path),
        ))

        try:
            self._context.registries.operation_id.register(operation_id)
        except ValueError as v:
            raise ValueError(
                f"{controller_cls.__name__} genera el operation id duplicado "
                f"'{operation_id}' para {metadata.method} {path}.",
            ) from v

        return operation_id


########################################################################################


class ApiOpenAPIContext(OpenAPIContext):
    operation_id_cls: ClassVar[type[OperationIdGenerator]] = PathOperationIdGenerator
