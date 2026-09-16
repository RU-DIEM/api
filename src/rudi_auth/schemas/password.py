from typing import Annotated

from pydantic import AfterValidator, StringConstraints

from api_auth.models import ApiUser
from api_auth.schemas.types import Password
from api_core.schemas.base import DTO
from api_core.schemas.validators import empty_or_email

from .verificacion import VerificationToken

########################################################################################


class PasswordResetPost(DTO):
    email: Annotated[
        str,
        AfterValidator(func=empty_or_email),
        AfterValidator(func=ApiUser.objects.normalize_email),
        StringConstraints(max_length=254, min_length=1),
    ]


########################################################################################


class PasswordConfirmPost(DTO):
    token: VerificationToken

    password1: Password
    password2: Password
