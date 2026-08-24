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


class AmbitosAplicacion(TextChoices):
    ACADEMIA = "Academia y sistema educativo"
    AMBIENTE = "Medio ambiente"
    EMPRESA = "Empresa e industria"
    GOBIERNO = "Gobierno y sector público"
    SOCIEDAD = "Sociedad civil y comunidad"


class EstadosPortafolio(TextChoices):
    ACTIVA = "Activa"
    CERRADA = "Cerrada"
    FINALIZADA = "Finalizada"
    IMPLEMENTADA = "Implementada"
    INTEGRADA = "Integrada"
    PAUSA = "En pausa"
    TRANSFERIDA = "Transferida"


class EtapasDesarrollo(TextChoices):
    ESTRUCTURACION = "Estructuración"
    PREINCUBACION = "Preincubación"
    INCUBACION = "Incubación"
    ACELERACION = "Aceleración"
    ESCALAMIENTO = "Escalamiento"


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


class MRL(TextChoices):
    L1 = "Identificación de oportunidad"
    L2 = "Comprensión del mercado y cliente"
    L3 = "Análisis competitivo"
    L4 = "Estrategia comercial"
    L5 = "Validación temprana"
    L6 = "Tracción inicial"
    L7 = "Introducción comercial"
    L8 = "Expansión y escalabilidad"
    L9 = "Adopción generalizada"


class NivelesAcademicos(TextChoices):
    BACHILLER = "Bachiller"
    TECNICO = "Técnico"
    LICENCIATURA = "Licenciatura"
    ESPECIALIZACION = "Especialización"
    MAESTRIA = "Maestría"
    DOCTORADO = "Doctorado"


class NivelesCarrera(TextChoices):
    PRIMERO = "1ro"
    SEGUNDO = "2do"
    TERCERO = "3ro"
    CUARTO = "4to"
    QUINTO = "5to"
    SEXTO = "6to"
    EGRESADO = "Egresado"
    N_A = "No aplica"


class NivelesFormalizacion(TextChoices):
    IDEA = "Idea"
    INICIATIVA = "Iniciativa"
    PROYECTO = "Proyecto de innovación"


class ODS(TextChoices):
    O1 = "Fin de la pobreza"
    O2 = "Hambre cero"
    O3 = "Salud y bienestar"
    O4 = "Educación de calidad"
    O5 = "Igualdad de género"
    O6 = "Agua limpia y saneamiento"
    O7 = "Energía asequible y no contaminante"
    O8 = "Trabajo decente y crecimiento económico"
    O9 = "Industria, innovación e infraestructura"
    O10 = "Reducción de las desigualdades"
    O11 = "Ciudades y comunidades sostenibles"
    O12 = "Producción y consumo responsables"
    O13 = "Acción por el clima"
    O14 = "Vida submarina"
    O15 = "Vida de ecosistemas terrestres"
    O16 = "Paz, justicia e instituciones sólidas"
    O17 = "Alianzas para lograr los objetivos"
    P_D = "Por determinar"
    N_A = "Sin alineación demostrada"


class SectoresAplicacion(TextChoices):
    A = "Agricultura, ganadería, silvicultura y pesca"
    B = "Explotación de minas y canteras"
    C = "Industrias manufactureras"
    D = "Suministro de electricidad, gas, vapor y aire acondicionado"
    E = "Agua, alcantarillado, desechos y saneamiento"
    F = "Construcción"
    G = "Comercio y reparación de vehículos"
    H = "Transporte y almacenamiento"
    I = "Alojamiento y servicios de comidas"  # ruff: ignore[ambiguous-variable-name]
    J = "Información y comunicaciones"
    K = "Actividades financieras y de seguros"
    L = "Actividades inmobiliarias"
    M = "Actividades profesionales, científicas y técnicas"
    N = "Servicios administrativos y de apoyo"
    O = "Administración pública y defensa"  # ruff: ignore[ambiguous-variable-name]
    P = "Enseñanza"
    Q = "Salud humana y asistencia social"
    R = "Actividades artísticas, de entrenimiento y recreativas"
    S = "Otras activdades de servicios"
    T = "Actividades de los hogares"
    U = "Organizaciones y órganos extraterritoriales"
    MULTI = "Multisectorial"
    P_D = "Por determinar"


class TallasCamisa(TextChoices):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    XXXL = "XXXL"


class TiposInnovacion(TextChoices):
    CANAL = "Canal"
    COMPROMISO = "Compromiso"
    DESEMPENO = "Desempeño del producto"
    ESTRUCTURA = "Estructura"
    MARCA = "Marca"
    MODELO = "Modelo de beneficios/ingresos"
    PROCESO = "Proceso"
    RED = "Red"
    SERVICIO = "Servicio"
    SISTEMA = "Sistema de productos"


class TRL(TextChoices):
    L1 = "Investigación básica"
    L2 = "Investigación aplicada"
    L3 = "Prueba de concepto"
    L4 = "Validación en laboratorio"
    L5 = "Validación en entorno relevante"
    L6 = "Demostración en entorno relevante"
    L7 = "Dmoestración en entorno operativo"
    L8 = "Sistema completo"
    L9 = "Sistema probado con éxito"


class VerticalesInnovacion(TextChoices):
    AG = "AgTech"
    BIOTECH = "BioTech"
    CIBERSEGURIDAD = "Ciberseguridad y privacidad digital"
    CIVIC = "CiviTech"
    CLEAN = "CleanTech"
    CLIMATE = "ClimateTech"
    ECONOMIA = "Economía circular"
    ED = "EdTech"
    ENERGY = "EnergyTech"
    FIN = "FinTech"
    FOOD = "FoodTech"
    GOV = "GovTech"
    HEALTH = "HealthTech"
    LEGAL = "LegalTech"
    IA = "IA y analítica"
    INCLUSION = "Inclusión y accesibilidad digital"
    INDUSTRIA = "Industria 4.0 y manufactura avanzada"
    MOVILIDAD = "Movilidad inteligente"
    PROP = "PropTech"
    ROBOTICA = "Robótica y automatización"
    WATER = "WaterTech"
    MULTI = "Otra vertical emergente"
    P_D = "Por determinar"
