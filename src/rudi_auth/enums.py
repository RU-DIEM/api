from django.db.models import TextChoices

########################################################################################


class AccesoDatoTypes(TextChoices):
    EXPORTACION = "exportacion"
    LECTURA = "lectura"


########################################################################################


class ConsentimientoCanalTypes(TextChoices):
    IMPORT = "importacion"
    PAPER = "formulario_fisico"
    PORTAL = "portal"
