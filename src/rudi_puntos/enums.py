from django.db.models import TextChoices

########################################################################################


class MovimientoOrigenTypes(TextChoices):
    AUTO = "automatico"
    LEGACY = "importacion"
    MANUAL = "manual"
    REVERSO = "reverso"
