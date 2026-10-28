from api_auth.schemas.types import Email, Password, VerificationToken
from api_core.schemas.base import DTO

########################################################################################


class PasswordResetPost(DTO):
    email: Email


########################################################################################


class PasswordConfirmPost(DTO):
    token: VerificationToken

    password1: Password
    password2: Password
