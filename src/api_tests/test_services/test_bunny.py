from base64 import urlsafe_b64encode
from hashlib import sha256
from http import HTTPMethod

import httpx
import pytest
import respx

from api_media.config import MEDIA_CONFIG
from api_media.enums import MediaVisibility
from api_media.services import bunny
from api_media.services.bunny import BUNNY_CLIENT, BunnyStorageError
from api_tests.sync import run

########################################################################################

KEY: str = "public/file name.png"

########################################################################################


def test_storage_url_quotes_key() -> None:
    assert BUNNY_CLIENT.storage_url(KEY) == (
        f"https://{MEDIA_CONFIG.BUNNY_STORAGE_HOST}/"
        f"{MEDIA_CONFIG.BUNNY_STORAGE_ZONE}/public/file%20name.png"
    )


def test_put_sends_checksum_and_access_key(bunny_storage: respx.MockRouter) -> None:
    run(
        BUNNY_CLIENT.put,
        checksum="ab" * 32,
        content=b"data",
        content_type="image/png",
        storage_key=KEY,
    )

    request: httpx.Request = bunny_storage["put"].calls.last.request

    assert request.content == b"data"
    assert request.headers["Checksum"] == "AB" * 32
    assert request.headers["Content-Type"] == "image/png"
    assert request.headers["AccessKey"] == (
        MEDIA_CONFIG.BUNNY_STORAGE_API_KEY.get_secret_value()
    )


def test_put_raises_on_unexpected_status(bunny_storage: respx.MockRouter) -> None:
    bunny_storage["put"].respond(400)

    with pytest.raises(BunnyStorageError) as exc:
        run(
            BUNNY_CLIENT.put,
            checksum="ab" * 32,
            content=b"data",
            content_type="image/png",
            storage_key=KEY,
        )

    assert exc.value.method == HTTPMethod.PUT
    assert exc.value.status_code == 400
    assert exc.value.storage_key == KEY


@pytest.mark.parametrize("status", [200, 404])
def test_delete_accepts_ok_and_missing(
    bunny_storage: respx.MockRouter,
    status: int,
) -> None:
    bunny_storage["delete"].respond(status)

    run(BUNNY_CLIENT.delete, storage_key=KEY)

    assert bunny_storage["delete"].called


def test_delete_raises_on_unexpected_status(bunny_storage: respx.MockRouter) -> None:
    bunny_storage["delete"].respond(500)

    with pytest.raises(BunnyStorageError):
        run(BUNNY_CLIENT.delete, storage_key=KEY)


########################################################################################


def test_public_url() -> None:
    assert BUNNY_CLIENT.resolve_url(
        storage_key=KEY,
        visibility=MediaVisibility.PUBLIC,
    ) == (f"https://{MEDIA_CONFIG.BUNNY_PULL_ZONE_HOST}/public/file%20name.png")


def test_signed_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bunny, "time", lambda: 1_000)

    expires: int = 1_000 + MEDIA_CONFIG.BUNNY_SIGNED_URL_TTL_SECONDS
    path: str = "/private/a.pdf"
    secret: str = MEDIA_CONFIG.BUNNY_TOKEN_AUTH_KEY.get_secret_value()

    token: str = (
        urlsafe_b64encode(sha256(f"{secret}{path}{expires}".encode()).digest())
        .decode()
        .rstrip("=")
    )

    assert BUNNY_CLIENT.resolve_url(
        storage_key="private/a.pdf",
        visibility=MediaVisibility.PRIVATE,
    ) == (
        f"https://{MEDIA_CONFIG.BUNNY_PRIVATE_PULL_ZONE_HOST}{path}"
        f"?token={token}&expires={expires}"
    )
