from django.db.models import TextChoices

########################################################################################


class IndicadorUnidadTypes(TextChoices):
    PERSONAS = "personas"
    PORCENTAJE = "porcentaje"
    PUNTOS = "puntos"
    REGISTROS = "registros"
