from django.db.models import TextChoices

########################################################################################


class ModalidadTypes(TextChoices):
    HIBRIDA = "hibrida", "Híbrida"
    PRESENCIAL = "presencial", "Presencial"
    VIRTUAL = "virtual", "Virtual"


########################################################################################


class ResponsableRolTypes(TextChoices):
    APOYO = "apoyo", "Apoyo"
    COORDINACION = "coordinacion", "Coordinación"
    FACILITACION = "facilitacion", "Facilitación"
    LOGISTICA = "logistica", "Logística"
