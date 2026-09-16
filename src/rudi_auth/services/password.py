from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.views.decorators.debug import sensitive_variables

from api_auth.services.user import check_password_match, check_password_strength
from api_exceptions.enums import BadRequestErrorTypes, RequestScopes
from api_exceptions.errors import BadRequestError
from rudi_auth.enums import VerificacionPropositoTypes
from rudi_auth.models import CodigoVerificacion, RudiUser

from .account import activate, resolve_estado_activo
from .verificacion import claim_codigo, issue_codigo, peek_codigo

if TYPE_CHECKING:
    from api_auth.models import ApiUser
    from rudi_auth.schemas.password import PasswordConfirmPost
    from rudi_estados.models import EstadoRudiUser

########################################################################################


async def request_reset(email: str) -> None:
    user: RudiUser | None = (
        await RudiUser.objects
        .select_related("user")
        .filter(
            anonimizado_at__isnull=True,
            user__email__iexact=email,
        )
        .afirst()
    )

    if user is None:
        return

    await issue_codigo(
        email=user.user.email,  # ty: ignore[unresolved-attribute]
        proposito=VerificacionPropositoTypes.RECOVER,
        user=user,
    )


########################################################################################


@sensitive_variables()
async def apply_password(
    data: PasswordConfirmPost,
    proposito: VerificacionPropositoTypes,
) -> RudiUser:
    codigo: CodigoVerificacion = await peek_codigo(
        proposito=proposito,
        token=data.token,
    )

    if codigo.user is None:
        raise BadRequestError(
            field_errors={"token": "El enlace no está asociado a una cuenta."},
            type=BadRequestErrorTypes.FAILED_VALIDATION,
        ).scoped(RequestScopes.BODY)

    user: RudiUser = codigo.user  # ty: ignore[invalid-assignment]
    cuenta: ApiUser = user.user  # ty: ignore[invalid-assignment]

    check_password_match(data)
    check_password_strength(data, user=cuenta)

    estado: EstadoRudiUser | None = (
        await resolve_estado_activo()
        if proposito is VerificacionPropositoTypes.INVITE
        else None
    )

    @atomic
    @sensitive_variables()
    def persist() -> None:
        claim_codigo(proposito=proposito, token=data.token)

        cuenta.set_password(data.password1)
        cuenta.save(update_fields=("password",))

        if estado is not None:
            activate(estado=estado, user=user)

    await sync_to_async(func=persist)()

    return user


########################################################################################


@sensitive_variables()
async def accept_invite(data: PasswordConfirmPost) -> RudiUser:
    return await apply_password(data, VerificacionPropositoTypes.INVITE)


########################################################################################


@sensitive_variables()
async def confirm_reset(data: PasswordConfirmPost) -> RudiUser:
    return await apply_password(data, VerificacionPropositoTypes.RECOVER)
