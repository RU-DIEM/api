from datetime import timedelta
from typing import Final

from django.db.models import TextChoices

########################################################################################


class EstudianteTypes(TextChoices):
    EXT = "Estudiante Externo"
    UAM = "Estudiante UAM"


########################################################################################


class MotivoAmbitoTypes(TextChoices):
    ANNUL_CONSTANCIA = "anulacion_constancia"
    ANNUL_PARTICIPACION = "anulacion_participacion"
    CANCEL_ACTIVIDAD = "cancelacion_actividad"
    CANCEL_INSCRIPCION = "cancelacion_inscripcion"
    FUSE_USER = "fusion_usuario"
    REJECT_MENTORIA = "rechazo_mentoria"
    REJECT_IMPORT = "rechazo_importacion"
    REVOKE_CONSENTIMIENTO = "revocar_consentimiento"


########################################################################################


class MotivoVisibilidadTypes(TextChoices):
    ADMIN = "administracion"
    PUB = "publico"
    USER = "participante"


########################################################################################


class ParametroGrupoTypes(TextChoices):
    REGISTRO = "registro"
    SESION = "sesion"
    INSCRIPCION = "inscripcion"
    VIGENCIA = "vigencia"
    IMPORTACION = "importacion"


########################################################################################


class ParametroTypes(TextChoices):
    BOOL = "binario"
    INT = "entero"
    LIST = "lista"
    STR = "texto"
    TIME = "duracion"


PARAMETRO_TYPES_MAP: Final[dict[ParametroTypes, type]] = {
    ParametroTypes.BOOL: bool,
    ParametroTypes.INT: int,
    ParametroTypes.LIST: list,
    ParametroTypes.STR: str,
    ParametroTypes.TIME: timedelta,
}


########################################################################################


class Etnias(TextChoices):
    CACAOPERA = "Cacaopera"
    CHOROTEGA = "Chorotega"
    CREOLE = "Kriol/Creole"
    GARIFUNA = "Garífuna"
    MATAGALPA = "Matagalpa"
    MAYANGNA = "Mayangna"
    MESTIZO = "Mestizo"
    MISKITU = "Miskitu"
    NAHUATL = "Nahuatl/Nahoa"
    NICARAO = "Nicarao"
    RAMA = "Rama"
    SUMU = "Sumu"
    SUTIABA = "Sutiaba/Xiu"
    ULWA = "Ulwa"


class Generos(TextChoices):
    F = "Mujer"
    M = "Hombre"
    X = "Prefiero no decirlo"


class NivelesCarrera(TextChoices):
    PRIMERO = "1ro"
    SEGUNDO = "2do"
    TERCERO = "3ro"
    CUARTO = "4to"
    QUINTO = "5to"
    SEXTO = "6to"
    EGRESADO = "Egresado"
    N_A = "No aplica"


class NivelesAcademicos(TextChoices):
    BACHILLER = "Bachiller"
    TECNICO = "Técnico"
    LICENCIATURA = "Licenciatura"
    ESPECIALIZACION = "Especialización"
    MAESTRIA = "Maestría"
    DOCTORADO = "Doctorado"


class TallasCamisa(TextChoices):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    XXXL = "XXXL"
