from typing import Annotated, Final

from pydantic import PositiveFloat, PositiveInt, SecretStr, StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict

from api_utils.env import ROOT

########################################################################################

type BunnySecret = Annotated[SecretStr, StringConstraints(min_length=1)]

type Host = Annotated[str, StringConstraints(min_length=1, pattern=r"^[^/:\s]+$")]

########################################################################################


class MediaConfig(BaseSettings):
    """
    Bunny.net storage/CDN credentials and upload limits.

    Public files are served through `BUNNY_PULL_ZONE_HOST`; private ones only
    through `BUNNY_PRIVATE_PULL_ZONE_HOST`, with token authentication enabled.
    """

    model_config = SettingsConfigDict(
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

    MEDIA_ALLOWED_MIME: frozenset[str] = frozenset({
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
    })

    MEDIA_MAX_BYTES: PositiveInt = 5_242_880


########################################################################################

MEDIA_CONFIG: Final[MediaConfig] = MediaConfig()
