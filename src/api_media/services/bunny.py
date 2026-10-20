from base64 import urlsafe_b64encode
from hashlib import sha256
from http import HTTPMethod
from time import time
from typing import TYPE_CHECKING, Final
from urllib.parse import quote

import httpx

from api_media.config import MEDIA_CONFIG
from api_media.enums import MediaVisibility

if TYPE_CHECKING:
    from collections.abc import Collection

########################################################################################


class BunnyStorageError(Exception):
    def __init__(
        self,
        *,
        method: HTTPMethod,
        status_code: int,
        storage_key: str,
    ) -> None:
        self.method: HTTPMethod = method
        self.status_code: int = status_code
        self.storage_key: str = storage_key

        super().__init__(
            f"Bunny Storage {method} failed ({status_code}) for {storage_key!r}.",
        )


########################################################################################


class BunnyClient:
    """
    Minimal async client for Bunny Storage and its pull zones.

    A fresh `httpx.AsyncClient` is opened per call: requests are rare
    (one per upload), and a shared client would be bound to whichever
    event loop first used it.
    """

    __slots__ = ()

    async def put(
        self,
        *,
        checksum: str,
        content: bytes,
        content_type: str,
        storage_key: str,
    ) -> None:
        # `checksum` is the hex sha256 of `content`:
        # bunny rejects the upload if what it received doesn't match
        await self._request(
            expected=frozenset({httpx.codes.CREATED}),
            content=content,
            headers={"Checksum": checksum.upper(), "Content-Type": content_type},
            method=HTTPMethod.PUT,
            storage_key=storage_key,
        )

    async def delete(self, *, storage_key: str) -> None:
        # a 404 is acceptable here:
        # a cleanup may retry a delete that already landed
        await self._request(
            expected=frozenset({httpx.codes.OK, httpx.codes.NOT_FOUND}),
            method=HTTPMethod.DELETE,
            storage_key=storage_key,
        )

    def resolve_url(self, *, storage_key: str, visibility: MediaVisibility) -> str:
        if visibility == MediaVisibility.PRIVATE:
            return self.signed_url(storage_key)

        return self.public_url(storage_key)

    @staticmethod
    def public_url(storage_key: str) -> str:
        return f"https://{MEDIA_CONFIG.BUNNY_PULL_ZONE_HOST}/{quote(storage_key)}"

    @staticmethod
    def signed_url(storage_key: str) -> str:
        # bunny's (basic) token authentication:
        # `token = base64url(sha256(key + path + expires))`, without padding
        expires: int = int(time()) + MEDIA_CONFIG.BUNNY_SIGNED_URL_TTL_SECONDS

        path: str = f"/{quote(storage_key)}"

        hashable: str = (
            f"{MEDIA_CONFIG.BUNNY_TOKEN_AUTH_KEY.get_secret_value()}{path}{expires}"
        )

        token: str = (
            urlsafe_b64encode(sha256(hashable.encode()).digest()).decode().rstrip("=")
        )

        return (
            f"https://{MEDIA_CONFIG.BUNNY_PRIVATE_PULL_ZONE_HOST}{path}?"
            f"token={token}&expires={expires}"
        )

    @staticmethod
    def storage_url(storage_key: str) -> str:
        return (
            f"https://{MEDIA_CONFIG.BUNNY_STORAGE_HOST}/"
            f"{MEDIA_CONFIG.BUNNY_STORAGE_ZONE}/{quote(storage_key)}"
        )

    async def _request(
        self,
        *,
        expected: Collection[int],
        method: HTTPMethod,
        storage_key: str,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        async with httpx.AsyncClient(
            timeout=MEDIA_CONFIG.BUNNY_TIMEOUT_SECONDS,
        ) as client:
            response: httpx.Response = await client.request(
                content=content,
                headers={
                    "AccessKey": MEDIA_CONFIG.BUNNY_STORAGE_API_KEY.get_secret_value(),
                    **(headers or {}),
                },
                method=method,
                url=self.storage_url(storage_key),
            )

        if response.status_code not in expected:
            raise BunnyStorageError(
                method=method,
                status_code=response.status_code,
                storage_key=storage_key,
            )


########################################################################################

BUNNY_CLIENT: Final[BunnyClient] = BunnyClient()
