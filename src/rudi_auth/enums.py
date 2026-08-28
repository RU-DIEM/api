from django.db.models import TextChoices

########################################################################################


class ConsentimientoCanalTypes(TextChoices):
    IMPORT = "importacion"
    PAPER = "formulario_fisico"
    PORTAL = "portal"


########################################################################################


class VerificacionPropositoTypes(TextChoices):
    INVITE = "invitacion_administrativa"
    RECOVER = "recuperacion_password"
    VERIFY = "verificacion_email"
