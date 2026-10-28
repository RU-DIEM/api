from typing import Annotated, Literal

from pydantic import AfterValidator, StringConstraints

from api_auth.models import ApiUser
from api_auth.schemas.types import Email, Password, Username
from api_core.schemas.base import DTO
from api_core.schemas.get import IsoDate, LaxEnum, RelatedId
from rudi_catalogos.enums import Etnias, Generos, TallasCamisa

from .user import RudiUserGet, Telefono

########################################################################################


def check_accepted(value: bool) -> bool:  # ruff: ignore[boolean-type-hint-positional-argument]
    if not value:
        raise ValueError("Debe aceptar la política de privacidad para registrarse.")

    return value


########################################################################################

type AceptaPolitica = Annotated[bool, AfterValidator(func=check_accepted)]

########################################################################################


class RudiPersonaWrite(DTO):
    first_name: Annotated[str, StringConstraints(max_length=100, min_length=1)]
    last_name: Annotated[str, StringConstraints(max_length=100, min_length=1)]

    fecha_nacimiento: IsoDate | None = None

    telefono: Telefono

    genero: LaxEnum[Generos] | Literal[""] = ""
    etnia: LaxEnum[Etnias] | Literal[""] = ""
    talla: LaxEnum[TallasCamisa] | Literal[""] = ""


########################################################################################


class RudiIdentificadorWrite(DTO):
    tipo: RelatedId
    valor: Annotated[str, StringConstraints(max_length=20, min_length=4)]


########################################################################################


class RudiRegisterPost(RudiPersonaWrite):
    email: Email

    username: Annotated[Username, AfterValidator(func=ApiUser.normalize_username)]

    password1: Password
    password2: Password

    acepta_politica: AceptaPolitica

    identificador: RudiIdentificadorWrite | None = None


########################################################################################


class RudiInvitePost(RudiPersonaWrite):
    email: Email

    username: Annotated[Username, AfterValidator(func=ApiUser.normalize_username)]

    identificador: RudiIdentificadorWrite | None = None


########################################################################################


class RudiRegisterGet(RudiUserGet):
    pass
