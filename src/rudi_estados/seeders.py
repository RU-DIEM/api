from typing import TYPE_CHECKING, Final

from api_core.seeding import register_structural
from rudi_estados.enums import ActorTypes, InputSourceTypes
from rudi_estados.models import (
    EstadoActividad,
    EstadoAsignacionMentor,
    EstadoConsentimiento,
    EstadoConstancia,
    EstadoInscripcion,
    EstadoParticipacion,
    EstadoPropuesta,
    EstadoRudiUser,
    TransicionEstadoActividad,
    TransicionEstadoInscripcion,
    TransicionEstadoParticipacion,
    TransicionEstadoPropuesta,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from rudi_estados.models.base import RudiEstado, RudiTransicion

########################################################################################

ADMIN: Final[str] = ActorTypes.ADMIN.value
SISTEMA: Final[str] = ActorTypes.SYS.value
USUARIO: Final[str] = ActorTypes.USER.value

########################################################################################


def seed_estado(
    model: type[RudiEstado],
    rows: Sequence[dict],
) -> dict[str, RudiEstado]:
    por_codigo: dict[str, RudiEstado] = {}

    for row in rows:
        codigo: str = row["codigo"]
        defaults: dict = {k: v for k, v in row.items() if k != "codigo"}

        instancia, _ = model.objects.get_or_create(codigo=codigo, defaults=defaults)
        por_codigo[codigo] = instancia

    return por_codigo


def seed_transicion(
    model: type[RudiTransicion],
    estados: dict[str, RudiEstado],
    pares: Sequence[tuple[str, str, str, bool]],
) -> None:
    for desde, hasta, actor, require_motivo in pares:
        model.objects.get_or_create(
            actor=actor,
            from_estado=estados[desde],
            to_estado=estados[hasta],
            defaults={"require_motivo": require_motivo},
        )


########################################################################################

USUARIO_ESTADOS: Final[Sequence[dict]] = (
    {
        "codigo": "pendiente_verificacion",
        "etiqueta": "Pendiente de verificación",
        "initial": True,
    },
    # a confirmed address lets the person in; enrolling also needs a profile
    # (`trg_rudiuser_profile`), so that is a second step
    {
        "allow_ingreso": True,
        "codigo": "verificada",
        "etiqueta": "Verificada",
    },
    {
        "allow_ingreso": True,
        "allow_inscripcion": True,
        "codigo": "activa",
        "etiqueta": "Activa",
    },
    {
        "codigo": "suspendida",
        "etiqueta": "Suspendida",
        "require_motivo": True,
    },
    {
        "codigo": "anonimizada",
        "etiqueta": "Anonimizada",
        "terminal": True,
        "visible_reportes": False,
    },
)

CONSENTIMIENTO_ESTADOS: Final[Sequence[dict]] = (
    {
        "allow_comunicacion": True,
        "allow_reporte": True,
        "codigo": "otorgado",
        "etiqueta": "Otorgado",
        "initial": True,
        "source": InputSourceTypes.SELF.value,
    },
    {
        "codigo": "pendiente_verificar",
        "etiqueta": "Pendiente de verificar",
        "initial": True,
        "source": InputSourceTypes.MODERN.value,
    },
    {
        "codigo": "no_autorizado",
        "etiqueta": "No autorizado",
        "initial": True,
        "source": InputSourceTypes.LEGACY.value,
    },
    {
        "codigo": "retirado",
        "etiqueta": "Retirado",
        "terminal": True,
    },
)

########################################################################################

ACTIVIDAD_ESTADOS: Final[Sequence[dict]] = (
    {"codigo": "borrador", "etiqueta": "Borrador", "initial": True},
    {
        "allow_inscripcion": True,
        "allow_validacion": True,
        "codigo": "publicada",
        "etiqueta": "Publicada",
        "public": True,
    },
    {
        "allow_validacion": True,
        "codigo": "en_curso",
        "etiqueta": "En curso",
        "public": True,
    },
    {
        "allow_validacion": True,
        "codigo": "finalizada",
        "etiqueta": "Finalizada",
        "public": True,
    },
    {"codigo": "cancelada", "etiqueta": "Cancelada", "terminal": True},
)

ACTIVIDAD_TRANSICIONES: Final[Sequence[tuple[str, str, str, bool]]] = (
    ("borrador", "publicada", ADMIN, False),
    ("publicada", "en_curso", ADMIN, False),
    ("publicada", "en_curso", SISTEMA, False),
    ("en_curso", "finalizada", ADMIN, False),
    ("en_curso", "finalizada", SISTEMA, False),
    ("borrador", "cancelada", ADMIN, True),
    ("publicada", "cancelada", ADMIN, True),
    ("en_curso", "cancelada", ADMIN, True),
)

########################################################################################

INSCRIPCION_ESTADOS: Final[Sequence[dict]] = (
    {
        "codigo": "pendiente",
        "consume_cupo": True,
        "etiqueta": "Pendiente",
        "initial": True,
        "source": InputSourceTypes.SELF.value,
    },
    {
        "allow_participacion": True,
        "codigo": "confirmada",
        "consume_cupo": True,
        "etiqueta": "Confirmada",
        "initial": True,
        "source": InputSourceTypes.MODERN.value,
    },
    {"codigo": "en_espera", "etiqueta": "En lista de espera"},
    {"codigo": "cancelada", "etiqueta": "Cancelada", "terminal": True},
    {"codigo": "rechazada", "etiqueta": "Rechazada", "terminal": True},
)

INSCRIPCION_TRANSICIONES: Final[Sequence[tuple[str, str, str, bool]]] = (
    ("pendiente", "confirmada", ADMIN, False),
    ("en_espera", "confirmada", ADMIN, False),
    ("pendiente", "rechazada", ADMIN, True),
    ("en_espera", "rechazada", ADMIN, True),
    ("pendiente", "cancelada", ADMIN, True),
    ("confirmada", "cancelada", ADMIN, True),
    ("en_espera", "cancelada", ADMIN, True),
    ("pendiente", "cancelada", USUARIO, True),
    ("confirmada", "cancelada", USUARIO, True),
    ("en_espera", "cancelada", USUARIO, True),
    # the waiting list promotes into `pendiente`: the person is told, and still
    # has to be confirmed (procesos.md, "el único proceso que decide")
    ("en_espera", "pendiente", SISTEMA, False),
    ("pendiente", "cancelada", SISTEMA, True),
    ("confirmada", "cancelada", SISTEMA, True),
    ("en_espera", "cancelada", SISTEMA, True),
)

########################################################################################

PARTICIPACION_ESTADOS: Final[Sequence[dict]] = (
    {"codigo": "registrada", "etiqueta": "Registrada", "initial": True},
    {"codigo": "en_curso", "etiqueta": "En curso"},
    {
        "allow_constancia": True,
        "allow_puntos": True,
        "codigo": "finalizada",
        "efectiva": True,
        "etiqueta": "Finalizada",
    },
    {
        "allow_puntos": True,
        "codigo": "no_completo",
        "efectiva": True,
        "etiqueta": "No completó",
    },
    {"codigo": "retirada", "etiqueta": "Retirada"},
    {"codigo": "anulada", "etiqueta": "Anulada", "terminal": True},
)

PARTICIPACION_TRANSICIONES: Final[Sequence[tuple[str, str, str, bool]]] = (
    ("registrada", "en_curso", ADMIN, False),
    ("registrada", "finalizada", ADMIN, False),
    ("registrada", "no_completo", ADMIN, False),
    ("registrada", "retirada", ADMIN, False),
    ("en_curso", "finalizada", ADMIN, False),
    ("en_curso", "no_completo", ADMIN, False),
    ("en_curso", "retirada", ADMIN, False),
    ("finalizada", "anulada", ADMIN, True),
    ("no_completo", "anulada", ADMIN, True),
    ("retirada", "anulada", ADMIN, True),
)

########################################################################################

ASIGNACION_ESTADOS: Final[Sequence[dict]] = (
    {"codigo": "propuesta", "etiqueta": "Propuesta", "initial": True},
    {
        "codigo": "confirmada",
        "etiqueta": "Confirmada",
        "public": True,
        "vigente": True,
    },
    {
        "codigo": "declinada",
        "etiqueta": "Declinada",
        "require_motivo": True,
        "terminal": True,
    },
    {
        "codigo": "finalizada",
        "etiqueta": "Finalizada",
        "public": True,
        "terminal": True,
    },
    {
        "codigo": "cancelada",
        "etiqueta": "Cancelada",
        "require_motivo": True,
        "terminal": True,
    },
    {"codigo": "vencida", "etiqueta": "Vencida", "terminal": True},
)

CONSTANCIA_ESTADOS: Final[Sequence[dict]] = (
    {"codigo": "emitida", "etiqueta": "Emitida", "initial": True, "valid": True},
    {
        "codigo": "anulada",
        "etiqueta": "Anulada",
        "require_motivo": True,
        "terminal": True,
    },
    {"codigo": "reemplazada", "etiqueta": "Reemplazada", "terminal": True},
)

########################################################################################

PROPUESTA_ESTADOS: Final[Sequence[dict]] = (
    {
        "allow_portafolio": True,
        "codigo": "activa",
        "etiqueta": "Activa",
        "initial": True,
        "vigente": True,
    },
    {"allow_portafolio": True, "codigo": "en_pausa", "etiqueta": "En pausa"},
    {
        "allow_portafolio": True,
        "codigo": "finalizada",
        "etiqueta": "Finalizada",
        "terminal": True,
    },
    {
        "allow_portafolio": True,
        "codigo": "implementada",
        "etiqueta": "Implementada",
        "terminal": True,
    },
    {
        "allow_portafolio": True,
        "codigo": "integrada",
        "etiqueta": "Integrada a otra propuesta",
        "terminal": True,
    },
    {"codigo": "cerrada", "etiqueta": "Cerrada", "terminal": True},
)

PROPUESTA_TRANSICIONES: Final[Sequence[tuple[str, str, str, bool]]] = (
    ("activa", "en_pausa", ADMIN, False),
    ("en_pausa", "activa", ADMIN, False),
    *(
        (desde, hasta, ADMIN, True)
        for desde in ("activa", "en_pausa")
        for hasta in ("finalizada", "implementada", "integrada", "cerrada")
    ),
)

########################################################################################


@register_structural(app_label="rudiestados", name="estados")
def seed_estados() -> None:
    seed_estado(EstadoRudiUser, USUARIO_ESTADOS)
    seed_estado(EstadoConsentimiento, CONSENTIMIENTO_ESTADOS)
    seed_estado(EstadoAsignacionMentor, ASIGNACION_ESTADOS)
    seed_estado(EstadoConstancia, CONSTANCIA_ESTADOS)

    for estado, transicion, estados, pares in (
        (
            EstadoActividad,
            TransicionEstadoActividad,
            ACTIVIDAD_ESTADOS,
            ACTIVIDAD_TRANSICIONES,
        ),
        (
            EstadoInscripcion,
            TransicionEstadoInscripcion,
            INSCRIPCION_ESTADOS,
            INSCRIPCION_TRANSICIONES,
        ),
        (
            EstadoParticipacion,
            TransicionEstadoParticipacion,
            PARTICIPACION_ESTADOS,
            PARTICIPACION_TRANSICIONES,
        ),
        (
            EstadoPropuesta,
            TransicionEstadoPropuesta,
            PROPUESTA_ESTADOS,
            PROPUESTA_TRANSICIONES,
        ),
    ):
        seed_transicion(transicion, seed_estado(estado, estados), pares)
