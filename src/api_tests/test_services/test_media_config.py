import pytest

from pydantic import ValidationError

from api_media.config import MediaConfig, detectable_mimes, parse_allowed_types

########################################################################################


def test_parse_allowed_types_tolerates_spacing_and_empty_entries() -> None:
    assert parse_allowed_types(" image/png : png ,, application/pdf:pdf, ") == {
        "application/pdf": "pdf",
        "image/png": "png",
    }


@pytest.mark.parametrize(
    "value",
    [
        "",
        " , ",
        "image/png",
        "image/png:",
        ":png",
        "image/png:png,image/png:apng",
        "imagen:png",
        "image/png:.png",
    ],
    ids=[
        "empty",
        "only-separators",
        "missing-colon",
        "missing-extension",
        "missing-mime",
        "duplicate",
        "bad-mime",
        "bad-extension",
    ],
)
def test_parse_allowed_types_rejects(value: str) -> None:
    with pytest.raises(ValueError, match="`"):
        parse_allowed_types(value)


########################################################################################


def test_detectable_mimes_cover_the_defaults() -> None:
    assert {"application/pdf", "image/jpeg", "image/png", "image/webp"} <= (
        detectable_mimes()
    )


def test_config_parses_allowed_types() -> None:
    config = MediaConfig(MEDIA_ALLOWED_TYPES="image/png:png")

    assert config.MEDIA_ALLOWED_TYPES == {"image/png": "png"}


def test_config_rejects_undetectable_types() -> None:
    with pytest.raises(ValidationError, match="text/plain"):
        MediaConfig(MEDIA_ALLOWED_TYPES="image/png:png,text/plain:txt")
