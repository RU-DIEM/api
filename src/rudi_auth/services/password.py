from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.views.decorators.debug import sensitive_variables

from api_auth.enums import VerificationPurposes
from api_auth.services.user import check_password_match, check_password_strength
from api_auth.services.verification import claim_code
from rudi_auth.models import RudiUser

from .account import activate, mark_email_verified
from .verificacion import check_codigo_email, issue_codigo

if TYPE_CHECKING:
    from api_auth.models import ApiUser, VerificationCode
    from rudi_auth.schemas.password import PasswordConfirmPost

########################################################################################


async def request_reset(email: str) -> None:
    persona: RudiUser | None = (
        await RudiUser.objects
        .select_related("user")
        .filter(
            anonimizado_at__isnull=True,
            user__email__iexact=email,
        )
        .afirst()
    )

    if persona is None:
        return

    await issue_codigo(
        proposito=VerificationPurposes.PASSWORD_RESET,
        user=persona.user,
    )


########################################################################################


@sensitive_variables()
def settle_password(
    data: PasswordConfirmPost,
    proposito: VerificationPurposes,
) -> ApiUser:
    # any error below rolls the claim back, so the code stays usable
    with atomic():
        codigo: VerificationCode = claim_code(data.token, proposito)

        check_codigo_email(codigo)

        user: ApiUser = codigo.api_user  # ty: ignore[invalid-assignment]

        check_password_strength(data, user=user)

        user.set_password(data.password1)
        user.save(update_fields=("password",))

        # an accepted invitation proves the address, just like a confirmation
        if proposito is VerificationPurposes.INVITATION:
            mark_email_verified(user)
            activate(user)

        return user


########################################################################################


@sensitive_variables()
async def apply_password(
    data: PasswordConfirmPost,
    proposito: VerificationPurposes,
) -> ApiUser:
    check_password_match(data)

    return await sync_to_async(func=settle_password)(data, proposito)


########################################################################################


@sensitive_variables()
async def accept_invite(data: PasswordConfirmPost) -> ApiUser:
    return await apply_password(data, VerificationPurposes.INVITATION)


########################################################################################


@sensitive_variables()
async def confirm_reset(data: PasswordConfirmPost) -> ApiUser:
    return await apply_password(data, VerificationPurposes.PASSWORD_RESET)
