from django.db.models import TextChoices

########################################################################################


class InstitucionTypes(TextChoices):
    COLEGIO = "colegio"
    EMPRESA = "empresa"
    GOBIERNO = "gobierno"
    ORGANIZACION = "organizacion"
    OTRA = "otra"
    TECNICO = "centro_tecnico"
    UNIVERSIDAD = "universidad"


########################################################################################


class OcupacionTypes(TextChoices):
    COLABORADOR = "colaborador_empresa", "Colaborador de una empresa"
    EMPRENDEDOR = "emprendedor", "Emprendedor"
    ESTUDIANTE = "estudiante", "Estudiante de otra institución"
    INDEPENDIENTE = "profesional_independiente", "Profesional independiente"
    OTRA = "otra", "Otro perfil"
