from typing import TYPE_CHECKING

from api_exceptions.errors import ForbiddenError
from rudi_auth.models import RudiUser

if TYPE_CHECKING:
    from api_auth.models import ApiUser

########################################################################################


def persona_de(cuenta: ApiUser) -> RudiUser:
    """
    Find the persona behind an account, for a participant's own actions.

    Returns:
        The account's persona.

    Raises:
        ForbiddenError: The account has no persona (a staff account).

    """

    persona: RudiUser | None = RudiUser.objects.filter(user=cuenta).first()

    if persona is None:
        raise ForbiddenError(detail="Esta acción exige una cuenta de participante.")

    return persona


def puede(cuenta: ApiUser, perm: str) -> bool:
    return bool(cuenta.is_superuser) or cuenta.has_perm(perm)
