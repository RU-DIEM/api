from django.db.models import TextChoices

########################################################################################


class ConsentimientoCanalTypes(TextChoices):
    IMPORT = "importacion"
    PAPER = "formulario_fisico"
    PORTAL = "portal"
