from datetime import date, datetime
from typing import Final
from uuid import UUID

from pydantic import (
    EmailStr,
    HttpUrl,
    TypeAdapter,
    ValidationError as PydanticValidationError,
)
from pydantic_core import PydanticCustomError

########################################################################################

DATE_ADAPTER: Final[TypeAdapter[date]] = TypeAdapter(date)
DATETIME_ADAPTER: Final[TypeAdapter[datetime]] = TypeAdapter(datetime)
EMAIL_ADAPTER: Final[TypeAdapter[EmailStr]] = TypeAdapter(EmailStr)
URL_ADAPTER: Final[TypeAdapter[HttpUrl]] = TypeAdapter(HttpUrl)

########################################################################################


def coerce_date(value: object) -> object:
    if not isinstance(value, str):
        return value

    try:
        return DATE_ADAPTER.validate_python(value, strict=False)
    except PydanticValidationError:
        return value


########################################################################################


def coerce_datetime(value: object) -> object:
    if not isinstance(value, str):
        return value

    try:
        return DATETIME_ADAPTER.validate_python(value, strict=False)
    except PydanticValidationError:
        return value


########################################################################################


def coerce_uuid(value: object) -> object:
    if not isinstance(value, str):
        return value

    try:
        return UUID(value)
    except ValueError:
        return value


########################################################################################


def empty_or_email(value: str) -> str:
    if value:
        try:
            EMAIL_ADAPTER.validate_python(value)
        except PydanticValidationError as p:
            raise PydanticCustomError(
                "api_custom",
                "",
                {"msg": "Debe ser un correo válido."},
            ) from p

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
