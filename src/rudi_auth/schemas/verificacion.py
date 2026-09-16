from typing import Annotated

from pydantic import AfterValidator, StringConstraints

from api_auth.models import ApiUser
from api_core.schemas.base import DTO
from api_core.schemas.validators import empty_or_email

########################################################################################

type VerificationToken = Annotated[
    str,
    StringConstraints(max_length=64, min_length=32, pattern=r"^[A-Za-z0-9_-]+$"),
]

########################################################################################


class EmailConfirmPost(DTO):
    token: VerificationToken


########################################################################################


class EmailResendPost(DTO):
    email: Annotated[
        str,
        AfterValidator(func=empty_or_email),
        AfterValidator(func=ApiUser.objects.normalize_email),
        StringConstraints(max_length=254, min_length=1),
    ]
