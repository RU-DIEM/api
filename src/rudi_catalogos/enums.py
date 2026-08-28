from datetime import timedelta
from typing import Final, override

from django.db.models import TextChoices

########################################################################################


class EstudianteTypes(TextChoices):
    EXT = "externo", "Estudiante externo"
    UAM = "uam", "Estudiante UAM"


class MotivoAmbitoTypes(TextChoices):
    NULL_CONSTANCIA = "anulacion_constancia"
    NULL_PARTICIPACION = "anulacion_participacion"
    CANCEL_ACTIVIDAD = "cancelacion_actividad"
    CANCEL_INSCRIPCION = "cancelacion_inscripcion"
    REJECT_MENTORIA = "rechazo_mentoria"
    REJECT_IMPORT = "rechazo_importacion"
    REVOKE_CONSENTIMIENTO = "revocar_consentimiento"


class MotivoVisibilidadTypes(TextChoices):
    ADMIN = "administracion"
    GLOBAL = "global"
    USER = "participante"


class ParametroGrupoTypes(TextChoices):
    REGISTRO = "registro"
    SESION = "sesion"
    INSCRIPCION = "inscripcion"
    VIGENCIA = "vigencia"
    IMPORTACION = "importacion"


class ParametroTypes(TextChoices):
    BOOL = "binario"
    INT = "entero"
    LIST = "lista"
    STR = "texto"
    TIME = "duracion"


########################################################################################


PARAMETRO_TYPES_MAP: Final[dict[ParametroTypes, type]] = {
    ParametroTypes.BOOL: bool,
    ParametroTypes.INT: int,
    ParametroTypes.LIST: list,
    ParametroTypes.STR: str,
    ParametroTypes.TIME: timedelta,
}

########################################################################################


class Etnias(TextChoices):
    CACAOPERA = "cacaopera", "Cacaopera"
    CHOROTEGA = "chorotega", "Chorotega"
    CREOLE = "creole", "Kriol/Creole"
    GARIFUNA = "garifuna", "Garífuna"
    MATAGALPA = "matagalpa", "Matagalpa"
    MAYANGNA = "mayangna", "Mayangna"
    MESTIZO = "mestizo", "Mestizo"
    MISKITU = "miskitu", "Miskitu"
    NAHUATL = "nahuatl", "Nahuatl/Nahoa"
    NICARAO = "nicarao", "Nicarao"
    RAMA = "rama", "Rama"
    SUMU = "sumu", "Sumu"
    SUTIABA = "sutiaba", "Sutiaba/Xiu"
    ULWA = "ulwa", "Ulwa"
    X = "sin_declara", "Prefiero no decirlo"


class Generos(TextChoices):
    F = "femenino", "Mujer"
    M = "masculino", "Hombre"
    X = "sin_declara", "Prefiero no decirlo"


class NivelesAcademicos(TextChoices):
    BACHILLER = "bachiller", "Bachiller"
    TECNICO = "tecnico", "Técnico"
    LICENCIATURA = "licenciatura", "Licenciatura"
    ESPECIALIZACION = "especializacion", "Especialización"
    MAESTRIA = "maestria", "Maestría"
    DOCTORADO = "doctorado", "Doctorado"


class NivelesCarrera(TextChoices):
    PRIMERO = "primero", "1ro"
    SEGUNDO = "segundo", "2do"
    TERCERO = "tercero", "3ro"
    CUARTO = "cuarto", "4to"
    QUINTO = "quinto", "5to"
    SEXTO = "sexto", "6to"
    EGRESADO = "egresado", "Egresado"
    N_A = "no_aplica", "No aplica"


class TallasCamisa(TextChoices):
    XS = "xs", "XS"
    S = "s", "S"
    M = "m", "M"
    L = "l", "L"
    XL = "xl", "XL"
    XXL = "xxl", "XXL"
    XXXL = "xxxl", "XXXL"


########################################################################################


class RudiTaxonomia(TextChoices):
    @classmethod
    def classified(cls) -> frozenset[str]:
        return frozenset(cls.values) - cls.neutrals()

    @classmethod
    def neutrals(cls) -> frozenset[str]:
        return frozenset()


########################################################################################


class AmbitosAplicacion(RudiTaxonomia):
    ACADEMIA = "academia", "Academia y sistema educativo"
    AMBIENTE = "ambiente", "Medio ambiente"
    EMPRESA = "empresa", "Empresa e industria"
    GOBIERNO = "gobierno", "Gobierno y sector público"
    SOCIEDAD = "sociedad", "Sociedad civil y comunidad"


class EtapasDesarrollo(RudiTaxonomia):
    ESTRUCTURACION = "estructuracion", "Estructuración"
    PREINCUBACION = "preincubacion", "Preincubación"
    INCUBACION = "incubacion", "Incubación"
    ACELERACION = "aceleracion", "Aceleración"
    ESCALAMIENTO = "escalamiento", "Escalamiento"
    P_D = "por_determinar", "Por determinar"

    @classmethod
    @override
    def neutrals(cls) -> frozenset[str]:
        return frozenset({cls.P_D.value})


class NivelesFormalizacion(RudiTaxonomia):
    IDEA = "idea", "Idea"
    INICIATIVA = "iniciativa", "Iniciativa"
    PROYECTO = "proyecto", "Proyecto de innovación"


class SectoresAplicacion(RudiTaxonomia):
    SEC_A = "cuaen_a", "Agricultura, ganadería, silvicultura y pesca"
    SEC_B = "cuaen_b", "Explotación de minas y canteras"
    SEC_C = "cuaen_c", "Industrias manufactureras"
    SEC_D = "cuaen_d", "Suministro de electricidad, gas, vapor y aire acondicionado"
    SEC_E = "cuaen_e", "Agua, alcantarillado, desechos y saneamiento"
    SEC_F = "cuaen_f", "Construcción"
    SEC_G = "cuaen_g", "Comercio y reparación de vehículos"
    SEC_H = "cuaen_h", "Transporte y almacenamiento"
    SEC_I = "cuaen_i", "Alojamiento y servicios de comidas"
    SEC_J = "cuaen_j", "Información y comunicaciones"
    SEC_K = "cuaen_k", "Actividades financieras y de seguros"
    SEC_L = "cuaen_l", "Actividades inmobiliarias"
    SEC_M = "cuaen_m", "Actividades profesionales, científicas y técnicas"
    SEC_N = "cuaen_n", "Servicios administrativos y de apoyo"
    SEC_O = "cuaen_o", "Administración pública y defensa"
    SEC_P = "cuaen_p", "Enseñanza"
    SEC_Q = "cuaen_q", "Salud humana y asistencia social"
    SEC_R = "cuaen_r", "Actividades artísticas, de entretenimiento y recreativas"
    SEC_S = "cuaen_s", "Otras actividades de servicios"
    SEC_T = "cuaen_t", "Actividades de los hogares"
    SEC_U = "cuaen_u", "Organizaciones y órganos extraterritoriales"
    MULTI = "multisectorial", "Multisectorial"
    P_D = "por_determinar", "Por determinar"

    @classmethod
    @override
    def neutrals(cls) -> frozenset[str]:
        return frozenset({cls.P_D.value})


class TiposInnovacion(RudiTaxonomia):
    CANAL = "canal", "Canal"
    COMPROMISO = "compromiso", "Compromiso"
    DESEMPENO = "desempeno", "Desempeño del producto"
    ESTRUCTURA = "estructura", "Estructura"
    MARCA = "marca", "Marca"
    MODELO = "modelo", "Modelo de beneficios/ingresos"
    PROCESO = "proceso", "Proceso"
    RED = "red", "Red"
    SERVICIO = "servicio", "Servicio"
    SISTEMA = "sistema", "Sistema de productos"
    P_D = "por_determinar", "Por determinar"

    @classmethod
    @override
    def neutrals(cls) -> frozenset[str]:
        return frozenset({cls.P_D.value})


class VerticalesInnovacion(RudiTaxonomia):
    AG = "agtech", "AgTech"
    BIOTECH = "biotech", "BioTech"
    CIBERSEGURIDAD = "ciberseguridad", "Ciberseguridad y privacidad digital"
    CIVIC = "civictech", "CiviTech"
    CLEAN = "cleantech", "CleanTech"
    CLIMATE = "climatetech", "ClimateTech"
    ECONOMIA = "economia_circular", "Economía circular"
    ED = "edtech", "EdTech"
    ENERGY = "energytech", "EnergyTech"
    FIN = "fintech", "FinTech"
    FOOD = "foodtech", "FoodTech"
    GOV = "govtech", "GovTech"
    HEALTH = "healthtech", "HealthTech"
    LEGAL = "legaltech", "LegalTech"
    IA = "ia", "IA y analítica"
    INCLUSION = "inclusion", "Inclusión y accesibilidad digital"
    INDUSTRIA = "industria", "Industria 4.0 y manufactura avanzada"
    MOVILIDAD = "movilidad", "Movilidad inteligente"
    PROP = "proptech", "PropTech"
    ROBOTICA = "robotica", "Robótica y automatización"
    WATER = "watertech", "WaterTech"
    MULTI = "otra", "Otra vertical emergente"
    P_D = "por_determinar", "Por determinar"

    @classmethod
    @override
    def neutrals(cls) -> frozenset[str]:
        return frozenset({cls.P_D.value})


########################################################################################


class MRL(RudiTaxonomia):
    L1 = "mrl_1", "Identificación de oportunidad"
    L2 = "mrl_2", "Comprensión del mercado y cliente"
    L3 = "mrl_3", "Análisis competitivo"
    L4 = "mrl_4", "Estrategia comercial"
    L5 = "mrl_5", "Validación temprana"
    L6 = "mrl_6", "Tracción inicial"
    L7 = "mrl_7", "Introducción comercial"
    L8 = "mrl_8", "Expansión y escalabilidad"
    L9 = "mrl_9", "Adopción generalizada"
    N_A = "no_aplica", "No aplica"
    P_D = "por_determinar", "Por determinar"

    @classmethod
    @override
    def neutrals(cls) -> frozenset[str]:
        return frozenset({cls.N_A.value, cls.P_D.value})


class TRL(RudiTaxonomia):
    L1 = "trl_1", "Investigación básica"
    L2 = "trl_2", "Investigación aplicada"
    L3 = "trl_3", "Prueba de concepto"
    L4 = "trl_4", "Validación en laboratorio"
    L5 = "trl_5", "Validación en entorno relevante"
    L6 = "trl_6", "Demostración en entorno relevante"
    L7 = "trl_7", "Demostración en entorno operativo"
    L8 = "trl_8", "Sistema completo"
    L9 = "trl_9", "Sistema probado con éxito"
    N_A = "no_aplica", "No aplica"
    P_D = "por_determinar", "Por determinar"

    @classmethod
    @override
    def neutrals(cls) -> frozenset[str]:
        return frozenset({cls.N_A.value, cls.P_D.value})


class ODS(RudiTaxonomia):
    O1 = "ods_1", "Fin de la pobreza"
    O2 = "ods_2", "Hambre cero"
    O3 = "ods_3", "Salud y bienestar"
    O4 = "ods_4", "Educación de calidad"
    O5 = "ods_5", "Igualdad de género"
    O6 = "ods_6", "Agua limpia y saneamiento"
    O7 = "ods_7", "Energía asequible y no contaminante"
    O8 = "ods_8", "Trabajo decente y crecimiento económico"
    O9 = "ods_9", "Industria, innovación e infraestructura"
    O10 = "ods_10", "Reducción de las desigualdades"
    O11 = "ods_11", "Ciudades y comunidades sostenibles"
    O12 = "ods_12", "Producción y consumo responsables"
    O13 = "ods_13", "Acción por el clima"
    O14 = "ods_14", "Vida submarina"
    O15 = "ods_15", "Vida de ecosistemas terrestres"
    O16 = "ods_16", "Paz, justicia e instituciones sólidas"
    O17 = "ods_17", "Alianzas para lograr los objetivos"
    N_A = "no_aplica", "No aplica"
    P_D = "por_determinar", "Por determinar"
    S_A = "sin_alineacion", "Sin alineación demostrada"

    @classmethod
    @override
    def neutrals(cls) -> frozenset[str]:
        return frozenset({cls.N_A.value, cls.P_D.value, cls.S_A.value})
