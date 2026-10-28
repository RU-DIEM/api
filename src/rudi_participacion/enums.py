from django.db.models import TextChoices

########################################################################################


class AcompanamientoTypes(TextChoices):
    CHARLA = "charla", "Charla"
    FACILITACION = "facilitacion", "Facilitación"
    JURADO = "jurado", "Jurado"
    NEGOCIO = "mentoria_negocio", "Mentoría de negocio"
    OTRO = "otro", "Otro"
    TECNICA = "mentoria_tecnica", "Mentoría técnica"


########################################################################################


class ParticipacionOrigenTypes(TextChoices):
    ADMIN = "administracion"
    BULK = "carga_masiva"
    LEGACY = "importacion"
