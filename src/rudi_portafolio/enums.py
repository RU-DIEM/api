from django.db.models import TextChoices

########################################################################################


class IntegranteRolTypes(TextChoices):
    COLABORADOR = "colaborador_externo", "Colaborador externo"
    INTEGRANTE = "integrante", "Integrante"
    MENTOR = "mentor", "Mentor"
    RESPONSABLE = "responsable", "Responsable"
    TUTOR = "docente_tutor", "Docente tutor"


########################################################################################


class PropuestaActividadRolTypes(TextChoices):
    ORIGINA = "origina", "Origina"
    PARTICIPA = "participa", "Participa"
    PRESENTA = "se_presenta", "Se presenta"
