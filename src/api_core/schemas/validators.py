from datetime import date, datetime, time, timedelta
from typing import Final
from uuid import UUID

from pydantic import (
    HttpUrl,
    TypeAdapter,
    ValidationError as PydanticValidationError,
)
from pydantic_core import PydanticCustomError

########################################################################################

DATE_ADAPTER: Final[TypeAdapter[date]] = TypeAdapter(date)
DATETIME_ADAPTER: Final[TypeAdapter[datetime]] = TypeAdapter(datetime)
URL_ADAPTER: Final[TypeAdapter[HttpUrl]] = TypeAdapter(HttpUrl)

# postgres rejects utc offsets of 16 hours or more
MAX_UTC_OFFSET: Final[timedelta] = timedelta(hours=16)

########################################################################################


def coerce_date(value: object) -> object:
    """
    Read a date off the wire without giving up strict validation.

    Schemas are strict, and a json body only ever carries strings,
    so a date has to be built before the field is validated. Input
    that is not a date is handed over untouched, for the field to
    reject with its own error message.

    Args:
        value: Whatever the client sent for the field.

    Returns:
        The parsed date, or *value* unchanged.

    """

    if not isinstance(value, str):
        return value

    try:
        return DATE_ADAPTER.validate_python(value, strict=False)
    except PydanticValidationError:
        return value


########################################################################################


def coerce_datetime(value: object) -> object:
    """
    Read a timestamp off the wire without giving up strict validation.

    Args:
        value: Whatever the client sent for the field.

    Returns:
        The parsed timestamp, or *value* unchanged.

    """

    if not isinstance(value, str):
        return value

    try:
        return DATETIME_ADAPTER.validate_python(value, strict=False)
    except PydanticValidationError:
        return value


########################################################################################


def check_utc_offset[T: datetime | time](value: T) -> T:
    offset: timedelta | None = value.utcoffset()

    if offset is not None and abs(offset) >= MAX_UTC_OFFSET:
        raise PydanticCustomError(
            "api_custom",
            "",
            {"msg": "La zona horaria está fuera de rango."},
        )

    return value


########################################################################################


def coerce_uuid(value: object) -> object:
    """
    Read a UUID off the wire without giving up strict validation.

    Args:
        value: Whatever the client sent for the field.

    Returns:
        The parsed uuid, or *value* unchanged.

    """

    if not isinstance(value, str):
        return value

    try:
        return UUID(value)
    except ValueError:
        return value


########################################################################################


def empty_or_url(value: str) -> str:
    if value:
        try:
            URL_ADAPTER.validate_python(value)
        except PydanticValidationError as p:
            raise PydanticCustomError(
                "api_custom",
                "",
                {"msg": "Debe ser un URL válido."},
            ) from p

    return value
