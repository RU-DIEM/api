from typing import Annotated

from pydantic import BeforeValidator
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

########################################################################################


def validar_telefono_ni(value: object) -> object:
    if value == "":  # ruff: ignore[compare-to-empty-string]
        return value

    return PhoneNumberValidator._parse("NI", "E164", None, value)  # ruff: ignore[private-member-access]


########################################################################################

# E.164, defaulting to Nicaragua; `""` is the absence of a phone
type TelefonoNI = Annotated[str, BeforeValidator(validar_telefono_ni)]
