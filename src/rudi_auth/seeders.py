from datetime import date
from typing import TYPE_CHECKING, Final

from api_core.seeding import register_structural
from rudi_auth.models import PoliticaPrivacidad

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

POLITICA_TEXTO: Final[str] = (
    "El Registro Único de Innovación (RUDI) recolecta los datos personales "
    "estrictamente necesarios para administrar la participación de las personas "
    "en sus actividades, emitir constancias y elaborar reportes agregados.\n\n"
    "Los datos no se comparten con terceros ajenos al programa. "
    "La persona titular puede retirar su consentimiento en cualquier momento "
    "desde el portal, sin que ello afecte la validez de los reconocimientos "
    "ya emitidos.\n\n"
    "Este texto es una versión inicial de trabajo y debe sustituirse por la "
    "política aprobada por la institución antes de operar en producción."
)

POLITICAS: Final[Sequence[dict]] = (
    {
        "texto": POLITICA_TEXTO,
        "titulo": "Política de privacidad y tratamiento de datos",
        "version": "1.0",
        "vigente_desde": date(2026, 1, 1),
    },
)

########################################################################################


@register_structural(app_label="rudiauth", name="politicas")
def seed_politicas() -> None:
    for fields in POLITICAS:
        PoliticaPrivacidad.objects.get_or_create(
            version=fields["version"],
            defaults=fields,
        )
