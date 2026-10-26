from asyncio import to_thread
from contextlib import suppress
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from typing import TYPE_CHECKING, Final, override
from uuid import uuid7

import httpx

from PIL import Image

from api_core.services.mappers import PrefetchedProxy
from api_core.services.operations import CreateOperation
from api_exceptions.enums import (
    BadRequestErrorTypes,
    ContentTooLargeErrorTypes,
    RequestScopes,
)
from api_exceptions.errors import ApiError, BadRequestError, ContentTooLargeError
from api_media.config import MEDIA_CONFIG
from api_media.enums import MediaVisibility
from api_media.schemas import ApiMediaGet, ApiMediaPost
from api_media.services.bunny import BUNNY_CLIENT, BunnyStorageError

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile
    from django.db.models import QuerySet

    from api_auth.models import ApiUser
    from api_core.schemas.base import DTO
    from api_core.services.mappers import ModelMapper
    from api_media.models import ApiMedia
    from api_utils.types import DatabaseModel

########################################################################################

# everything Pillow raises for corrupt, truncated, or unrecognized images
IMAGE_ERRORS: Final[tuple[type[Exception], ...]] = (OSError, SyntaxError, ValueError)

STORAGE_ERRORS: Final[tuple[type[Exception], ...]] = (
    BunnyStorageError,
    httpx.HTTPError,
)

########################################################################################


def media_mapper[Get: DTO](obj: ApiMedia, schema: type[Get]) -> Get:
    url: str = BUNNY_CLIENT.resolve_url(
        storage_key=obj.storage_key,  # ty: ignore[invalid-argument-type]
        visibility=MediaVisibility(obj.visibility),
    )

    return schema.model_validate(PrefetchedProxy(obj, {"url": url}))


########################################################################################


@dataclass(frozen=True, slots=True)
class SniffedContent:
    mime: str | None
    height: int | None = None
    width: int | None = None


@dataclass(frozen=True, slots=True)
class ValidatedMedia:
    checksum: str
    content: bytes
    extension: str
    height: int | None
    mime: str
    width: int | None


########################################################################################


def file_error(message: str) -> BadRequestError:
    return BadRequestError(
        field_errors={"file": message},
        type=BadRequestErrorTypes.FAILED_VALIDATION,
    ).scoped(RequestScopes.FILES)


def ensure_size(size: int | None) -> None:
    if size is None or size > MEDIA_CONFIG.MEDIA_MAX_BYTES:
        raise ContentTooLargeError(type=ContentTooLargeErrorTypes.FILE)


# a file's type is detected from its bytes;
# the client's `Content-Type` is never trusted
def sniff_content(content: bytes) -> SniffedContent:
    if content.startswith(b"%PDF-"):
        return SniffedContent(mime="application/pdf")

    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()

            width, height = img.size

            mime: str | None = Image.MIME.get(img.format or "")
    except Image.DecompressionBombError as e:
        raise file_error("La imagen excede el número máximo de píxeles.") from e
    except IMAGE_ERRORS:
        return SniffedContent(mime=None)

    return SniffedContent(mime=mime, height=height, width=width)


# CPU-bound: run it off the event loop
def validate_media(content: bytes) -> ValidatedMedia:
    ensure_size(len(content))

    sniffed: SniffedContent = sniff_content(content)

    if sniffed.mime is None or sniffed.mime not in MEDIA_CONFIG.MEDIA_ALLOWED_TYPES:
        raise file_error(
            f"El tipo de archivo detectado ({sniffed.mime or 'desconocido'}) "
            "no está permitido.",
        )

    return ValidatedMedia(
        checksum=sha256(content).hexdigest(),
        content=content,
        extension=MEDIA_CONFIG.MEDIA_ALLOWED_TYPES[sniffed.mime],
        height=sniffed.height,
        mime=sniffed.mime,
        width=sniffed.width,
    )


########################################################################################


class MediaUploadOperation(CreateOperation[ApiMediaGet, ApiMediaPost]):
    """
    Validate an upload, store it in Bunny, then record it.

    If recording fails, the stored file is removed again,
    so storage never accumulates objects without a row.
    """

    __slots__ = ("user",)

    def __init__(
        self,
        *fields: str,
        mapper: ModelMapper[ApiMediaGet],
        schema: type[ApiMediaGet],
        qs: QuerySet,
        user: ApiUser,
    ) -> None:
        super().__init__(*fields, mapper=mapper, schema=schema, qs=qs)

        self.user: ApiUser = user

    @override
    async def run(  # ty: ignore[invalid-method-override]
        self,
        body: ApiMediaPost,
        file: UploadedFile,
    ) -> ApiMediaGet:
        # reject oversized files before reading them into memory
        ensure_size(file.size)

        content: bytes = await to_thread(file.read)
        media: ValidatedMedia = await to_thread(validate_media, content)

        with self.exc_handler():
            obj: DatabaseModel = await self.execute(
                self.dump(dto=body) | {"media": media}
            )

        return self.map(obj)

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        media: ValidatedMedia = data["media"]
        visibility = MediaVisibility(data["visibility"])

        media_id = uuid7()
        storage_key: str = f"{visibility.value}/{media_id}.{media.extension}"

        try:
            await BUNNY_CLIENT.put(
                checksum=media.checksum,
                content=media.content,
                content_type=media.mime,
                storage_key=storage_key,
            )
        except STORAGE_ERRORS as e:
            raise ApiError(detail="No se pudo almacenar el archivo.") from e

        try:
            return await self.qs.acreate(
                id=media_id,
                checksum=media.checksum,
                height=media.height,
                mime=media.mime,
                size=len(media.content),
                storage_key=storage_key,
                uploaded_by=self.user,
                visibility=visibility,
                width=media.width,
            )
        except Exception:
            with suppress(*STORAGE_ERRORS):
                await BUNNY_CLIENT.delete(storage_key=storage_key)

            raise
