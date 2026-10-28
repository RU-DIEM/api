from secrets import token_urlsafe
from typing import TYPE_CHECKING, Final
from urllib.parse import quote

from asgiref.sync import sync_to_async
from django.views.decorators.debug import sensitive_variables

from api_auth.enums import VerificationPurposes
from api_auth.services.verification import TOKEN_BYTES, persist_code, reject_code
from api_core.config import CONFIG
from rudi_catalogos.services.parametro import read_duracion

from .mail import send_plantilla

if TYPE_CHECKING:
    from datetime import timedelta

    from api_auth.models import ApiUser, VerificationCode

########################################################################################

# the codes themselves are the template's `VerificationCode`s; rudi only
# decides how long they live, which message carries them, and where they lead

VIGENCIA_PARAMETRO: Final[dict[VerificationPurposes, str]] = {
    VerificationPurposes.EMAIL: "vigencia.verificacion",
    VerificationPurposes.INVITATION: "vigencia.invitacion",
    VerificationPurposes.PASSWORD_RESET: "vigencia.recuperacion",
}

PLANTILLA_CODIGO: Final[dict[VerificationPurposes, str]] = {
    VerificationPurposes.EMAIL: "verificacion_email",
    VerificationPurposes.INVITATION: "invitacion_administrativa",
    VerificationPurposes.PASSWORD_RESET: "recuperacion_password",
}

FRONTEND_RUTA: Final[dict[VerificationPurposes, str]] = {
    VerificationPurposes.EMAIL: "verificar",
    VerificationPurposes.INVITATION: "invitacion",
    VerificationPurposes.PASSWORD_RESET: "recuperar",
}

########################################################################################


@sensitive_variables()
def build_enlace(proposito: VerificationPurposes, token: str) -> str:
    return (
        f"{CONFIG.frontend_url}/{FRONTEND_RUTA[proposito]}"
        f"?token={quote(string=token, safe='')}"
    )


########################################################################################


@sensitive_variables()
async def issue_codigo(user: ApiUser, proposito: VerificationPurposes) -> str:
    vigencia: timedelta = await read_duracion(VIGENCIA_PARAMETRO[proposito])

    token: str = token_urlsafe(TOKEN_BYTES)

    await sync_to_async(func=persist_code)(
        email=user.email,
        lifetime=vigencia,
        purpose=proposito,
        token=token,
        user=user,
    )

    await send_plantilla(
        codigo=PLANTILLA_CODIGO[proposito],
        context={
            "enlace": build_enlace(proposito=proposito, token=token),
            "token": token,
            "vigencia_horas": int(vigencia.total_seconds() // 3600),
        },
        to=user.email,  # ty: ignore[invalid-argument-type]
    )

    return token


########################################################################################


def check_codigo_email(codigo: VerificationCode) -> None:
    # a code is only good for the address it was mailed to
    if codigo.api_user.email.casefold() != codigo.email.casefold():  # ty: ignore[unresolved-attribute]
        raise reject_code()
