from collections.abc import Sequence
from dataclasses import dataclass
from http import HTTPMethod
from typing import Final, cast, override

from dmr import ResponseSpec
from dmr.endpoint import Endpoint
from dmr.types import EMPTY
from dmr.validation import MetadataMerger

from typing_extensions import Sentinel

########################################################################################

COLLECTION_ACTIONS: Final[dict[str, str]] = {
    HTTPMethod.DELETE: "clear",
    HTTPMethod.GET: "list",
    HTTPMethod.PATCH: "merge",
    HTTPMethod.POST: "create",
    HTTPMethod.PUT: "replace",
}

INSTANCE_ACTIONS: Final[dict[str, str]] = {
    HTTPMethod.DELETE: "destroy",
    HTTPMethod.GET: "retrieve",
    HTTPMethod.PATCH: "modify",
    HTTPMethod.POST: "append",
    HTTPMethod.PUT: "update",
}

########################################################################################


@dataclass(slots=True, frozen=True, kw_only=True)
class ApiMetadataMerger(MetadataMerger):
    @override
    def first_defined[T](self, *layers: T | Sentinel | None) -> T | Sentinel | None:
        if self.field_name != "responses":
            return super().first_defined(*layers)

        defined: list[Sequence[ResponseSpec]] = [
            cast("Sequence[ResponseSpec]", layer)
            for layer in reversed(layers)
            if layer is not None and not isinstance(layer, Sentinel)
        ]

        if not defined:
            return EMPTY

        return cast("T", [spec for layer in defined for spec in layer])


########################################################################################


class PathOperationIdEndpoint(Endpoint):
    __slots__ = ()

    metadata_merger_cls = ApiMetadataMerger

    @classmethod
    def get_action(cls, method: str, path: str) -> str:  # ruff: ignore[unused-class-method-argument]
        return method.lower()

    @classmethod
    def get_segments(cls, path: str) -> Sequence[str]:
        return tuple(
            part for part in path.split(sep="/") if part and not part.startswith("{")
        )

    @classmethod
    def is_instance_path(cls, path: str) -> bool:
        parts: Sequence[str] = tuple(part for part in path.split(sep="/") if part)

        return bool(parts) and parts[-1].startswith("{")


class ModelOperationIdEndpoint(PathOperationIdEndpoint):
    __slots__ = ()

    @classmethod
    @override
    def get_action(cls, method: str, path: str) -> str:
        actions: dict[str, str] = (
            INSTANCE_ACTIONS if cls.is_instance_path(path) else COLLECTION_ACTIONS
        )

        return actions.get(method.upper(), method.lower())
