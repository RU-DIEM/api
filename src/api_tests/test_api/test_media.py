from http import HTTPStatus
from typing import Final
from uuid import UUID

import pytest
import respx

from django.test.client import MULTIPART_CONTENT
from dmr.test import DMRClient

from api_auth.models import ApiUser
from api_auth.services.jwt import EncodedJwtPair
from api_exceptions.enums import ContentTooLargeErrorTypes, RequestScopes
from api_media.config import MEDIA_CONFIG
from api_media.enums import MediaVisibility
from api_media.models import ApiMedia
from api_tests.helpers import (
    PatchedHttpResponse,
    assert_detail,
    assert_field_error,
    bearer,
    route,
    scoped_key,
    unauthenticate,
)
from api_tests.media import PDF, image_bytes, upload

pytestmark = pytest.mark.django_db(transaction=True)

########################################################################################

LIST: Final[str] = "media-list"
DETAIL: Final[str] = "media-detail"

########################################################################################


# `dmr_client` is tracked by tracecov, which reads `request.body` after every request:
# multipart bodies are consumed while parsing, so tracking them raises
# `RawPostDataException`. uploads go through untracked clients instead
#
@pytest.fixture
def admin_upload_client(admin_tokens: EncodedJwtPair) -> DMRClient:
    return bearer(DMRClient(), admin_tokens)


@pytest.fixture
def client_upload_client(client_tokens: EncodedJwtPair) -> DMRClient:
    return bearer(DMRClient(), client_tokens)


########################################################################################


def post_upload(
    client: DMRClient,
    content: bytes,
    *,
    visibility: MediaVisibility | None = None,
    **kwargs: str,
) -> PatchedHttpResponse:
    data: dict = {"file": upload(content, **kwargs)}

    if visibility is not None:
        data["visibility"] = visibility.value

    return client.post(route(LIST), content_type=MULTIPART_CONTENT, data=data)


########################################################################################


def test_upload_public_image(
    admin_upload_client: DMRClient,
    admin_user: ApiUser,
    bunny_storage: respx.MockRouter,
) -> None:
    content: bytes = image_bytes()

    response: PatchedHttpResponse = post_upload(admin_upload_client, content)

    assert response.status_code == HTTPStatus.CREATED, response.content

    payload: dict = response.json()
    media: ApiMedia = ApiMedia.objects.get(pk=payload["id"])

    assert "storage_key" not in payload
    assert payload["visibility"] == MediaVisibility.PUBLIC
    assert payload["mime"] == "image/png"
    assert payload["size"] == len(content)
    assert (payload["width"], payload["height"]) == (256, 128)
    assert payload["uploaded_by_id"] == str(admin_user.pk)
    assert payload["url"] == (
        f"https://{MEDIA_CONFIG.BUNNY_PULL_ZONE_HOST}/{media.storage_key}"
    )

    assert media.storage_key == f"public/{media.pk}.png"
    assert bunny_storage["put"].calls.last.request.content == content


def test_upload_private_pdf_is_signed(admin_upload_client: DMRClient) -> None:
    response: PatchedHttpResponse = post_upload(
        admin_upload_client,
        PDF,
        content_type="application/pdf",
        name="doc.pdf",
        visibility=MediaVisibility.PRIVATE,
    )

    assert response.status_code == HTTPStatus.CREATED, response.content

    payload: dict = response.json()

    assert payload["mime"] == "application/pdf"
    assert payload["width"] is None
    assert payload["url"].startswith(
        f"https://{MEDIA_CONFIG.BUNNY_PRIVATE_PULL_ZONE_HOST}/private/",
    )
    assert "token=" in payload["url"]
    assert "expires=" in payload["url"]


def test_upload_ignores_spoofed_content_type(
    admin_upload_client: DMRClient,
    bunny_storage: respx.MockRouter,
) -> None:
    response: PatchedHttpResponse = post_upload(
        admin_upload_client, b"<?php echo 1; ?>"
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert_field_error(response, scoped_key(RequestScopes.FILES, "file"))
    assert not bunny_storage["put"].called
    assert not ApiMedia.objects.exists()


def test_upload_rejects_oversized_files(
    admin_upload_client: DMRClient,
    bunny_storage: respx.MockRouter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(MEDIA_CONFIG, "MEDIA_MAX_BYTES", 10)

    response: PatchedHttpResponse = post_upload(admin_upload_client, image_bytes())

    assert response.status_code == HTTPStatus.CONTENT_TOO_LARGE
    assert_detail(response, ContentTooLargeErrorTypes.FILE.value)
    assert not bunny_storage["put"].called


def test_upload_reports_storage_failures(
    admin_upload_client: DMRClient,
    bunny_storage: respx.MockRouter,
) -> None:
    bunny_storage["put"].respond(503)

    response: PatchedHttpResponse = post_upload(admin_upload_client, image_bytes())

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert_detail(response, "No se pudo almacenar el archivo.")
    assert not ApiMedia.objects.exists()


def test_upload_requires_authentication(admin_upload_client: DMRClient) -> None:
    response: PatchedHttpResponse = post_upload(
        unauthenticate(admin_upload_client),
        image_bytes(),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_upload_requires_permission(client_upload_client: DMRClient) -> None:
    response: PatchedHttpResponse = post_upload(client_upload_client, image_bytes())

    assert response.status_code == HTTPStatus.FORBIDDEN


########################################################################################


def test_list_filters_by_visibility(
    admin_client: DMRClient,
    admin_upload_client: DMRClient,
) -> None:
    post_upload(admin_upload_client, image_bytes())
    post_upload(admin_upload_client, PDF, visibility=MediaVisibility.PRIVATE)

    response: PatchedHttpResponse = admin_client.get(
        route(LIST),
        query_params={"visibility": MediaVisibility.PRIVATE.value},
    )

    assert response.status_code == HTTPStatus.OK

    results: list[dict] = response.json()["results"]

    assert [r["visibility"] for r in results] == [MediaVisibility.PRIVATE]
    assert "token=" in results[0]["url"]


def test_detail(admin_client: DMRClient, admin_upload_client: DMRClient) -> None:
    created: dict = post_upload(admin_upload_client, image_bytes()).json()

    response: PatchedHttpResponse = admin_client.get(
        route(DETAIL, id=UUID(created["id"])),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == created
