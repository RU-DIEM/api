from django.db.models import TextChoices

########################################################################################


class ActorTypes(TextChoices):
    ADMIN = "administracion"
    PART = "participante"
    SYS = "sistema"


########################################################################################


class InputSourceTypes(TextChoices):
    IMPORTACION = "importacion"
    PORTAL = "portal"


########################################################################################


class InscripcionTypes(TextChoices):
    CUPO_DISPONIBLE = "cupo_disponible"
    LISTA_ESPERA = "lista_espera"
