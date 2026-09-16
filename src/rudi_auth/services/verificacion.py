from hashlib import sha256
from secrets import token_urlsafe
from typing import TYPE_CHECKING, Final
from urllib.parse import quote

from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.utils.timezone import now
from django.views.decorators.debug import sensitive_variables

from api_core.config import CONFIG
from api_exceptions.enums import BadRequestErrorTypes, RequestScopes
from api_exceptions.errors import BadRequestError
from rudi_auth.enums import VerificacionPropositoTypes
from rudi_auth.models import CodigoVerificacion, RudiUser
from rudi_catalogos.services.parametro import read_duracion

from .mail import send_plantilla

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from api_auth.models import ApiUser

########################################################################################

TOKEN_BYTES: Final[int] = 32

VIGENCIA_PARAMETRO: Final[dict[VerificacionPropositoTypes, str]] = {
    VerificacionPropositoTypes.INVITE: "vigencia.invitacion",
    VerificacionPropositoTypes.RECOVER: "vigencia.recuperacion",
    VerificacionPropositoTypes.VERIFY: "vigencia.verificacion",
}

PLANTILLA_CODIGO: Final[dict[VerificacionPropositoTypes, str]] = {
    VerificacionPropositoTypes.INVITE: "invitacion_administrativa",
    VerificacionPropositoTypes.RECOVER: "recuperacion_password",
    VerificacionPropositoTypes.VERIFY: "verificacion_email",
}

FRONTEND_RUTA: Final[dict[VerificacionPropositoTypes, str]] = {
    VerificacionPropositoTypes.INVITE: "invitacion",
    VerificacionPropositoTypes.RECOVER: "recuperar",
    VerificacionPropositoTypes.VERIFY: "verificar",
}

########################################################################################


@sensitive_variables()
def build_enlace(proposito: VerificacionPropositoTypes, token: str) -> str:
    base: str = str(CONFIG.FRONTEND_URL).rstrip("/")

    return f"{base}/{FRONTEND_RUTA[proposito]}?token={quote(string=token, safe='')}"


########################################################################################


@sensitive_variables()
def hash_token(token: str) -> str:
    return sha256(token.encode()).hexdigest()


########################################################################################


@sensitive_variables()
def invalidate_live(email: str, proposito: VerificacionPropositoTypes) -> int:
    return CodigoVerificacion.objects.filter(
        consumido_at__isnull=True,
        email__iexact=email,
        invalidado_at__isnull=True,
        proposito=proposito,
    ).update(invalidado_at=now())


########################################################################################


@sensitive_variables()
async def issue_codigo(
    email: str,
    proposito: VerificacionPropositoTypes,
    emitido_por: ApiUser | None = None,
    user: RudiUser | None = None,
) -> str:
    vigencia: timedelta = await read_duracion(VIGENCIA_PARAMETRO[proposito])

    token: str = token_urlsafe(TOKEN_BYTES)

    @atomic
    def persist() -> None:
        invalidate_live(email, proposito)

        CodigoVerificacion.objects.create(
            email=email,
            emitido_por=emitido_por,
            expira_at=(now() + vigencia),
            proposito=proposito,
            token_hash=hash_token(token),
            user=user,
        )

    await sync_to_async(func=persist)()

    await send_plantilla(
        codigo=PLANTILLA_CODIGO[proposito],
        context={
            "enlace": build_enlace(proposito=proposito, token=token),
            "token": token,
            "vigencia_horas": int(vigencia.total_seconds() // 3600),
        },
        to=email,
    )

    return token


########################################################################################


def reject_codigo() -> BadRequestError:
    return BadRequestError(
        field_errors={"token": "El enlace no es válido o ya expiró."},
        type=BadRequestErrorTypes.FAILED_VALIDATION,
    ).scoped(RequestScopes.BODY)


########################################################################################


@sensitive_variables()
async def peek_codigo(
    token: str,
    proposito: VerificacionPropositoTypes,
) -> CodigoVerificacion:
    codigo: CodigoVerificacion | None = (
        await CodigoVerificacion.objects
        .select_related("user__user")
        .filter(
            consumido_at__isnull=True,
            expira_at__gt=now(),
            invalidado_at__isnull=True,
            proposito=proposito,
            token_hash=hash_token(token),
        )
        .afirst()
    )

    if codigo is None:
        raise reject_codigo()

    return codigo


########################################################################################


@sensitive_variables()
def claim_codigo(token: str, proposito: VerificacionPropositoTypes) -> None:
    momento: datetime = now()

    consumido: int = CodigoVerificacion.objects.filter(
        consumido_at__isnull=True,
        expira_at__gt=momento,
        invalidado_at__isnull=True,
        proposito=proposito,
        token_hash=hash_token(token),
    ).update(consumido_at=momento)

    if not consumido:
        raise reject_codigo()


########################################################################################


@sensitive_variables()
async def consume_codigo(
    token: str,
    proposito: VerificacionPropositoTypes,
) -> CodigoVerificacion:
    codigo: CodigoVerificacion = await peek_codigo(
        proposito=proposito,
        token=token,
    )

    await sync_to_async(func=claim_codigo)(proposito=proposito, token=token)

    return codigo
