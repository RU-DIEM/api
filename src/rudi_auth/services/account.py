from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.utils.timezone import now

from api_exceptions.enums import BadRequestErrorTypes, RequestScopes
from api_exceptions.errors import BadRequestError, NotFoundError
from rudi_auth.enums import VerificacionPropositoTypes
from rudi_auth.models import CodigoVerificacion, RudiUser
from rudi_auth.services.verificacion import consume_codigo, issue_codigo
from rudi_estados.models import EstadoRudiUser

########################################################################################


async def resolve_estado_activo() -> EstadoRudiUser:
    estado: EstadoRudiUser | None = (
        await EstadoRudiUser.objects
        .filter(
            allow_ingreso=True,
            is_active=True,
            terminal=False,
        )
        .order_by("pk")
        .afirst()
    )

    if estado is None:
        raise NotFoundError(
            detail="No hay un estado de cuenta activa configurado.",
        )

    return estado


########################################################################################


def activate(user: RudiUser, estado: EstadoRudiUser) -> None:
    if user.email_verified_at is None:
        user.email_verified_at = now()

    user.estado = estado  # ty: ignore[invalid-assignment]

    user.save(update_fields=("email_verified_at", "estado", "updated_at"))


########################################################################################


async def confirm_email(token: str) -> RudiUser:
    codigo: CodigoVerificacion = await consume_codigo(
        proposito=VerificacionPropositoTypes.VERIFY,
        token=token,
    )

    if codigo.user is None:
        raise BadRequestError(
            field_errors={"token": "El enlace no está asociado a una cuenta."},
            type=BadRequestErrorTypes.FAILED_VALIDATION,
        ).scoped(RequestScopes.BODY)

    estado: EstadoRudiUser = await resolve_estado_activo()

    user: RudiUser = codigo.user  # ty: ignore[invalid-assignment]

    @atomic
    def persist() -> None:
        activate(estado=estado, user=user)

    await sync_to_async(func=persist)()

    return user


########################################################################################


async def resend_verification(email: str) -> None:
    user: RudiUser | None = (
        await RudiUser.objects
        .select_related("user")
        .filter(
            anonimizado_at__isnull=True,
            email_verified_at__isnull=True,
            user__email__iexact=email,
        )
        .afirst()
    )

    if user is None:
        return

    await issue_codigo(
        email=user.user.email,  # ty: ignore[unresolved-attribute]
        proposito=VerificacionPropositoTypes.VERIFY,
        user=user,
    )
