from typing import TYPE_CHECKING, Final

from api_core.seeding import register_structural
from rudi_catalogos.enums import ParametroGrupoTypes, ParametroTypes
from rudi_catalogos.models import Parametro, PlantillaMensaje, TipoIdentificador

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

DOMINIO_INSTITUCIONAL: Final[str] = "uamv.edu.ni"

PARAMETROS: Final[Sequence[dict]] = (
    {
        "codigo": "vigencia.verificacion",
        "descripcion": "Vigencia del enlace de confirmación de correo.",
        "grupo": ParametroGrupoTypes.VIGENCIA,
        "tipo": ParametroTypes.TIME,
        "valor": "PT24H",
    },
    {
        "codigo": "vigencia.recuperacion",
        "descripcion": "Vigencia del enlace de recuperación de contraseña.",
        "grupo": ParametroGrupoTypes.VIGENCIA,
        "tipo": ParametroTypes.TIME,
        "valor": "PT2H",
    },
    {
        "codigo": "vigencia.invitacion",
        "descripcion": "Vigencia del enlace de invitación administrativa.",
        "grupo": ParametroGrupoTypes.VIGENCIA,
        "tipo": ParametroTypes.TIME,
        "valor": "P7D",
    },
    {
        "codigo": "registro.dominio_institucional",
        "descripcion": "Dominio de correo exigido a los estudiantes de la UAM.",
        "grupo": ParametroGrupoTypes.REGISTRO,
        "tipo": ParametroTypes.STR,
        "valor": DOMINIO_INSTITUCIONAL,
    },
)

PLANTILLAS: Final[Sequence[dict]] = (
    {
        "asunto": "Confirmá tu correo en RUDI",
        "codigo": "verificacion_email",
        "cuerpo": (
            "Hola:\n\n"
            "Para terminar tu registro en RUDI, abrí este enlace:\n\n"
            "{enlace}\n\n"
            "Si tu cliente no admite enlaces, ingresá este código: {token}\n\n"
            "El enlace vence en {vigencia_horas} horas."
        ),
        "etiqueta": "Confirmación de correo",
        "variables": ["enlace", "token", "vigencia_horas"],
    },
    {
        "asunto": "Recuperá tu contraseña de RUDI",
        "codigo": "recuperacion_password",
        "cuerpo": (
            "Hola:\n\n"
            "Recibimos una solicitud para restablecer tu contraseña. "
            "Abrí este enlace para elegir una nueva:\n\n"
            "{enlace}\n\n"
            "Si tu cliente no admite enlaces, ingresá este código: {token}\n\n"
            "El enlace vence en {vigencia_horas} horas. "
            "Si no pediste este cambio, ignorá este mensaje."
        ),
        "etiqueta": "Recuperación de contraseña",
        "variables": ["enlace", "token", "vigencia_horas"],
    },
    {
        "asunto": "Te invitaron a RUDI",
        "codigo": "invitacion_administrativa",
        "cuerpo": (
            "Hola:\n\n"
            "La administración de RUDI creó una cuenta a tu nombre. "
            "Abrí este enlace para elegir tu contraseña y activarla:\n\n"
            "{enlace}\n\n"
            "Si tu cliente no admite enlaces, ingresá este código: {token}\n\n"
            "El enlace vence en {vigencia_horas} horas."
        ),
        "etiqueta": "Invitación administrativa",
        "variables": ["enlace", "token", "vigencia_horas"],
    },
)

TIPOS_IDENTIFICADOR: Final[Sequence[dict]] = (
    {
        "codigo": "cedula",
        "etiqueta": "Cédula",
        "regex": r"^[0-9]{3}[0-9]{6}[0-9]{4}[A-Z]$",
    },
    {
        "codigo": "pasaporte",
        "etiqueta": "Pasaporte",
    },
    {
        "codigo": "carnet_uam",
        "etiqueta": "Carné UAM",
        "is_institucional": True,
    },
)

########################################################################################


@register_structural(app_label="rudicatalogos", name="catalogos")
def seed_catalogos() -> None:
    for fields in PARAMETROS:
        Parametro.objects.get_or_create(codigo=fields["codigo"], defaults=fields)

    for fields in PLANTILLAS:
        PlantillaMensaje.objects.get_or_create(
            codigo=fields["codigo"],
            defaults=fields,
        )

    for fields in TIPOS_IDENTIFICADOR:
        TipoIdentificador.objects.get_or_create(
            codigo=fields["codigo"],
            defaults=fields,
        )
