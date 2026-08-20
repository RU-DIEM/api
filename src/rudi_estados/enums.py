from django.db.models import TextChoices

########################################################################################


class ActorTypes(TextChoices):
    ADMIN = "administracion"
    SYS = "sistema"
    USER = "participante"


########################################################################################


class InputSourceTypes(TextChoices):
    LEGACY = "importacion"
    MODERN = "sistema"


########################################################################################


class InscripcionTypes(TextChoices):
    CUPO_DISPONIBLE = "cupo_disponible"
    LISTA_ESPERA = "lista_espera"
