from django.db.models import TextChoices

########################################################################################


class ApiUserTypes(TextChoices):
    ADMIN = "Administrador"
    CLIENT = "Cliente"
    STAFF = "Personal"


########################################################################################


class TokenTypes(TextChoices):
    ACCESS = "access"
    CHALLENGE = "challenge"
    REFRESH = "refresh"


########################################################################################


class VerificationPurposes(TextChoices):
    EMAIL = "email_verification"
    INVITATION = "invitation"
    PASSWORD_RESET = "password_reset"  # ruff: ignore[hardcoded-password-string]


########################################################################################


class PermissionTypes(TextChoices):
    ADD = "add"
    CHANGE = "change"
    DELETE = "delete"
    VIEW = "view"
