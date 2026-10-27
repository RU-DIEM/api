from typing import Annotated, Literal

from pydantic import AfterValidator, StringConstraints
from pydantic.json_schema import SkipJsonSchema

from api_auth.enums import ApiUserTypes
from api_auth.schemas.user import ApiClientGroups, ApiClientPost
from api_core.schemas.base import DTO
from api_core.schemas.get import IsoDate, LaxEnum, RelatedId
from rudi_catalogos.enums import Etnias, Generos, TallasCamisa

from .types import TelefonoNI
from .user import RudiUserGet

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

    telefono: TelefonoNI

    genero: LaxEnum[Generos] | Literal[""] = ""
    etnia: LaxEnum[Etnias] | Literal[""] = ""
    talla: LaxEnum[TallasCamisa] | Literal[""] = ""


########################################################################################


class RudiIdentificadorWrite(DTO):
    tipo: RelatedId
    valor: Annotated[str, StringConstraints(max_length=20, min_length=4)]


########################################################################################


# the account half is the template's own registration body, so the template's
# `dump_user_post_data` reads it as is; the persona half (and its stricter
# names) comes first so its fields win. Personas are always clients.


class RudiRegisterPost(RudiPersonaWrite, ApiClientPost):
    group: ApiClientGroups = ApiUserTypes.CLIENT

    acepta_politica: AceptaPolitica

    identificador: RudiIdentificadorWrite | None = None


########################################################################################


# the invitee chooses the password when accepting, so the invitation carries
# none: the account is created with an unusable one


class RudiInvitePost(RudiPersonaWrite, ApiClientPost):
    group: ApiClientGroups = ApiUserTypes.CLIENT

    password1: SkipJsonSchema[None] = None
    password2: SkipJsonSchema[None] = None

    identificador: RudiIdentificadorWrite | None = None


########################################################################################


class RudiRegisterGet(RudiUserGet):
    pass
