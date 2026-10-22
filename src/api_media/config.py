from functools import cache
from re import fullmatch
from typing import Annotated, Final, Self

from PIL import Image
from pydantic import (
    PositiveFloat,
    PositiveInt,
    SecretStr,
    StringConstraints,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from api_utils.env import ROOT

########################################################################################

type BunnySecret = Annotated[SecretStr, StringConstraints(min_length=1)]

type Host = Annotated[str, StringConstraints(min_length=1, pattern=r"^[^/:\s]+$")]

########################################################################################

# same pattern as the `chk_apimedia_mime` constraint
EXTENSION_PATTERN: Final[str] = r"^[a-z0-9]+$"
MIME_PATTERN: Final[str] = r"^[a-z]+/[a-zA-Z0-9.+-]+$"

########################################################################################


# every type `sniff_content` can report; Pillow only fills `MIME` once
# its plugins are loaded, and also lists formats it can write but not read
@cache
def detectable_mimes() -> frozenset[str]:
    Image.init()

    return frozenset({
        "application/pdf",
        *(Image.MIME[fmt] for fmt in Image.OPEN if fmt in Image.MIME),
    })


# `"image/png:png, image/jpeg:jpg"` -> `{"image/png": "png", "image/jpeg": "jpg"}`
def parse_allowed_types(value: str) -> dict[str, str]:
    types: dict[str, str] = {}

    for entry in (part.strip() for part in value.split(",")):
        if not entry:
            continue

        mime, sep, extension = (part.strip() for part in entry.partition(":"))

        if not sep or not mime or not extension:
            raise ValueError(f"`{entry}` debería tener la forma `tipo/subtipo:ext`.")
        if mime in types:
            raise ValueError(f"`{mime}` está repetido.")
        if not fullmatch(MIME_PATTERN, mime):
            raise ValueError(f"`{mime}` no es un tipo MIME válido.")
        if not fullmatch(EXTENSION_PATTERN, extension):
            raise ValueError(f"`{extension}` no es una extensión válida.")

        types[mime] = extension

    if not types:
        raise ValueError("`MEDIA_ALLOWED_TYPES` no define ningún tipo.")

    return types


########################################################################################


class MediaConfig(BaseSettings):
    """
    Bunny.net storage/CDN credentials and upload limits.

    Public files are served through `BUNNY_PULL_ZONE_HOST`; private ones only
    through `BUNNY_PRIVATE_PULL_ZONE_HOST`, with token authentication enabled.
    `MEDIA_ALLOWED_TYPES` maps every accepted type to the extension its
    files are stored with.
    """

    model_config = SettingsConfigDict(
        enable_decoding=False,
        env_file=(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    BUNNY_STORAGE_ZONE: Annotated[str, StringConstraints(min_length=1)]
    BUNNY_STORAGE_HOST: Host = "storage.bunnycdn.com"
    BUNNY_STORAGE_API_KEY: BunnySecret

    BUNNY_PULL_ZONE_HOST: Host
    BUNNY_PRIVATE_PULL_ZONE_HOST: Host
    BUNNY_TOKEN_AUTH_KEY: BunnySecret

    BUNNY_SIGNED_URL_TTL_SECONDS: PositiveInt = 300
    BUNNY_TIMEOUT_SECONDS: PositiveFloat = 10.0

    MEDIA_ALLOWED_TYPES: dict[str, str] = {
        "application/pdf": "pdf",
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }

    MEDIA_MAX_BYTES: PositiveInt = 5_242_880

    @field_validator("MEDIA_ALLOWED_TYPES", mode="before")
    @classmethod
    def parse_media_allowed_types(
        cls,
        value: str | dict[str, str],
    ) -> dict[str, str]:
        return parse_allowed_types(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def check_allowed_types(self) -> Self:
        undetectable: list[str] = sorted(
            set(self.MEDIA_ALLOWED_TYPES) - detectable_mimes()
        )

        if undetectable:
            raise ValueError(
                f"{', '.join(f'`{mime}`' for mime in undetectable)} "
                "no se puede detectar a partir del contenido del archivo.",
            )

        return self


########################################################################################

MEDIA_CONFIG: Final[MediaConfig] = MediaConfig()
