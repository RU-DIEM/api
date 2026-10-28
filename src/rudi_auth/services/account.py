from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.utils.timezone import now
from django.views.decorators.debug import sensitive_variables

from api_auth.enums import VerificationPurposes
from api_auth.models import ApiUser
from api_auth.services import account as api_account
from api_exceptions.errors import NotFoundError
from rudi_auth.models import RudiUser
from rudi_estados.models import EstadoRudiUser

from .verificacion import issue_codigo

########################################################################################


def resolve_estado_activo() -> EstadoRudiUser:
    estado: EstadoRudiUser | None = (
        EstadoRudiUser.objects
        .filter(
            allow_ingreso=True,
            allow_inscripcion=False,
            is_active=True,
            terminal=False,
        )
        .order_by("pk")
        .first()
    )

    if estado is None:
        raise NotFoundError(
            detail="No hay un estado de cuenta activa configurado.",
        )

    return estado


########################################################################################


def mark_email_verified(user: ApiUser) -> None:
    ApiUser.objects.filter(
        email_verified_at__isnull=True,
        pk=user.pk,
    ).update(email_verified_at=now())


########################################################################################


def activate(user: ApiUser) -> None:
    """
    Move a freshly registered persona out of its initial state.

    Proving ownership of the address is what lets a persona in, so
    this runs after every verified code. Personas that already left
    the initial state (suspended, anonymized, ...) are left alone,
    so a later re-verification can never undo an administrative
    decision. Accounts without a persona are not rudi's business.

    Args:
        user: The account whose address was just verified.

    """

    persona: RudiUser | None = (
        RudiUser.objects
        .select_for_update(of=("self",))
        .select_related("estado")
        .filter(user=user)
        .first()
    )

    if persona is None or not persona.estado.initial:  # ty: ignore[unresolved-attribute]
        return

    persona.estado = resolve_estado_activo()  # ty: ignore[invalid-assignment]

    persona.save(update_fields=("estado", "updated_at"))


########################################################################################


@sensitive_variables()
def settle_email(token: str) -> ApiUser:
    with atomic():
        user: ApiUser = api_account.settle_email(token)

        activate(user)

        return user


########################################################################################


@sensitive_variables()
async def confirm_email(token: str) -> ApiUser:
    return await sync_to_async(func=settle_email)(token)


########################################################################################


async def resend_verification(email: str) -> None:
    """
    Send a new verification code to an address, if it still needs one.

    Pending personas get rudi's message; any other account falls
    through to the template's own flow. Nothing is reported back,
    so the endpoint cannot be used to probe for registered addresses.

    Args:
        email: The address that requested a new code.

    """

    persona: RudiUser | None = (
        await RudiUser.objects
        .select_related("user")
        .filter(
            anonimizado_at__isnull=True,
            user__email__iexact=email,
            user__email_verified_at__isnull=True,
        )
        .afirst()
    )

    if persona is None:
        await api_account.resend_verification(email)
        return

    await issue_codigo(
        proposito=VerificationPurposes.EMAIL,
        user=persona.user,
    )
