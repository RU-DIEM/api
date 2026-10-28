from typing import Annotated

from pydantic import AfterValidator, Field, StringConstraints

from api_core.schemas.validators import empty_or_url

########################################################################################


def sin_nul(value: str) -> str:
    if "\x00" in value:
        raise ValueError("El texto no puede contener el carácter nulo.")

    return value


# PostgreSQL refuses NUL in `text`; without this a stray `\x00` answers `500`
SinNul = AfterValidator(func=sin_nul)

########################################################################################

# field types every module shares; each mirrors a database `CHECK`, so a bad value
# answers `400` at the schema instead of `409` at the constraint

type Anio = Annotated[int, Field(ge=2000, le=2100)]

type EnlaceUrl = Annotated[
    str,
    SinNul,
    AfterValidator(func=empty_or_url),
    StringConstraints(max_length=500),
]

type MotivoDescripcion = Annotated[str, SinNul, StringConstraints(max_length=2_000)]

type Puntos = Annotated[int, Field(ge=-500, le=500)]
