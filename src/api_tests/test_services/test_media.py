from uuid import UUID

import pytest
import respx

from PIL import Image

from api_exceptions.enums import ContentTooLargeErrorTypes, RequestScopes
from api_exceptions.errors import ApiError, BadRequestError, ContentTooLargeError
from api_media.config import MEDIA_CONFIG
from api_media.enums import MediaVisibility
from api_media.schemas import ApiMediaGet
from api_media.services.media import (
    MediaUploadOperation,
    ValidatedMedia,
    media_mapper,
    sniff_content,
    validate_media,
)
from api_tests.media import PDF, image_bytes
from api_tests.sync import run

########################################################################################


class FailingQuerySet:
    async def acreate(self, **kwargs: object) -> None:  # ruff: ignore[no-self-use, unused-method-argument]
        raise RuntimeError("insert failed")


def failing_operation() -> MediaUploadOperation:
    return MediaUploadOperation(
        mapper=media_mapper,  # ty: ignore[invalid-argument-type]
        schema=ApiMediaGet,
        qs=FailingQuerySet(),  # ty: ignore[invalid-argument-type]
        user=None,  # ty: ignore[invalid-argument-type]
    )


########################################################################################


@pytest.mark.parametrize(
    ("fmt", "mime"),
    [("PNG", "image/png"), ("JPEG", "image/jpeg"), ("WEBP", "image/webp")],
)
def test_sniff_content_detects_images(fmt: str, mime: str) -> None:
    sniffed = sniff_content(image_bytes(fmt, size=(300, 200)))

    assert sniffed.mime == mime
    assert (sniffed.width, sniffed.height) == (300, 200)


def test_sniff_content_detects_pdf() -> None:
    sniffed = sniff_content(PDF)

    assert sniffed.mime == "application/pdf"
    assert sniffed.width is None
    assert sniffed.height is None


@pytest.mark.parametrize(
    "content",
    [b"plain text", image_bytes()[:40]],
    ids=["unknown", "truncated"],
)
def test_sniff_content_rejects_unknown(content: bytes) -> None:
    assert sniff_content(content).mime is None


def test_sniff_content_rejects_decompression_bombs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 10)

    with pytest.raises(BadRequestError) as exc:
        sniff_content(image_bytes())

    assert f"{RequestScopes.FILES}.file" in exc.value.field_errors


########################################################################################


def test_validate_media_computes_metadata() -> None:
    content: bytes = image_bytes()

    media: ValidatedMedia = validate_media(content)

    assert media.mime == "image/png"
    assert media.extension == "png"
    assert len(media.checksum) == 64
    assert (media.width, media.height) == (256, 128)


@pytest.mark.parametrize(
    "content",
    [b"plain text", image_bytes("GIF")],
    ids=["unknown", "not-allowed"],
)
def test_validate_media_rejects_types(content: bytes) -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_media(content)

    assert f"{RequestScopes.FILES}.file" in exc.value.field_errors


def test_validate_media_rejects_oversized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(MEDIA_CONFIG, "MEDIA_MAX_BYTES", 10)

    with pytest.raises(ContentTooLargeError) as exc:
        validate_media(image_bytes())

    assert exc.value.detail == ContentTooLargeErrorTypes.FILE.value


########################################################################################


def test_upload_removes_stored_file_when_insert_fails(
    bunny_storage: respx.MockRouter,
) -> None:
    media: ValidatedMedia = validate_media(image_bytes())

    with pytest.raises(RuntimeError, match="insert failed"):
        run(
            failing_operation().execute,
            {"media": media, "visibility": MediaVisibility.PRIVATE},
        )

    stored: str = str(bunny_storage["put"].calls.last.request.url)
    removed: str = str(bunny_storage["delete"].calls.last.request.url)

    assert stored == removed
    assert "/private/" in stored
    assert UUID(stored.rsplit("/", 1)[-1].removesuffix(".png"))


def test_upload_wraps_storage_failures(bunny_storage: respx.MockRouter) -> None:
    bunny_storage["put"].respond(401)

    with pytest.raises(ApiError) as exc:
        run(
            failing_operation().execute,
            {"media": validate_media(PDF), "visibility": MediaVisibility.PUBLIC},
        )

    assert exc.value.detail == "No se pudo almacenar el archivo."
    assert not bunny_storage["delete"].called
