# ruff: file-ignore[non-empty-init-module]

from typing import TYPE_CHECKING

from pgtrigger import (
    After,
    Before,
    Trigger,
    UpdateOf,
    register as register_trigger,
)

from api_utils.strings import normalize_trigger
from rudi_actividades.models import Actividad
from rudi_core.triggers import como_actor
from rudi_estados.enums import ActorTypes
from rudi_estados.models import EstadoInscripcion, TransicionEstadoInscripcion

from .asignacion import AsignacionMentor
from .equipo import Equipo, EquipoMiembro
from .inscripcion import Inscripcion
from .participacion import Participacion, Reconocimiento

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Final

########################################################################################

__all__: Sequence[str] = (
    "AsignacionMentor",
    "Equipo",
    "EquipoMiembro",
    "Inscripcion",
    "Participacion",
    "Reconocimiento",
)

########################################################################################

CIERRE_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    IF OLD.cerrada_at IS NULL AND NEW.cerrada_at IS NOT NULL AND EXISTS (
        SELECT 1
        FROM {Participacion._meta.db_table}
        WHERE inscripcion_id = NEW.id
        AND validada_at IS NOT NULL
        AND anulada_at IS NULL
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'cerrada_at',
            MESSAGE = 'No se cierra una inscripción con una participación validada.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

PROMOVER_TRIGGER: Final[str] = normalize_trigger("""
BEGIN
    IF (NEW.cupo IS NULL AND OLD.cupo IS NOT NULL) OR NEW.cupo > OLD.cupo THEN
        PERFORM rudi_promover_espera(NEW.id);
    END IF;
    RETURN NULL;
END;
""")

CERRAR_INSCRIPCION: Final[str] = como_actor(
    ActorTypes.SYS.value,
    f"""
        UPDATE {Inscripcion._meta.db_table}
        SET
            estado_id = destino,
            cerrada_at = NEW.cancelada_at,
            motivo_id = NEW.motivo_id,
            motivo_descripcion = NEW.motivo_descripcion,
            posicion_espera = NULL
        WHERE id = inscripcion.id;
    """,  # ruff: ignore[hardcoded-sql-expression, private-member-access]
)

# a cancelled activity closes every live inscription through the transition the
# catalog declares for `sistema` into a terminal state that frees the seat; with
# none declared, the cancellation fails instead of leaving inscriptions alive
CANCELAR_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    inscripcion RECORD;
    destino uuid;
    actor_previo text;
BEGIN
    IF OLD.cancelada_at IS NOT NULL OR NEW.cancelada_at IS NULL THEN
        RETURN NULL;
    END IF;
    FOR inscripcion IN
        SELECT id, estado_id
        FROM {Inscripcion._meta.db_table}
        WHERE actividad_id = NEW.id
        AND cerrada_at IS NULL
        ORDER BY posicion_espera NULLS FIRST
    LOOP
        SELECT transicion.to_estado_id
        INTO destino
        FROM {TransicionEstadoInscripcion._meta.db_table}
        AS transicion
        JOIN {EstadoInscripcion._meta.db_table}
        AS estado
        ON estado.id = transicion.to_estado_id
        WHERE transicion.from_estado_id = inscripcion.estado_id
        AND transicion.actor = '{ActorTypes.SYS.value}'
        AND transicion.is_active
        AND estado.is_active
        AND estado.terminal
        AND NOT estado.consume_cupo
        ORDER BY estado.codigo
        LIMIT 1;
        IF NOT FOUND THEN
            RAISE check_violation
            USING
                COLUMN = 'cancelada_at',
                MESSAGE = 'No hay una transición de sistema que cierre las inscripciones.';
        END IF;
        {CERRAR_INSCRIPCION}
    END LOOP;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

########################################################################################

register_trigger(
    Trigger(
        func=CIERRE_TRIGGER,
        name="trg_inscripcion_cierre_bloqueado",
        operation=UpdateOf("cerrada_at"),
        when=Before,
    ),
)(Inscripcion)

register_trigger(
    Trigger(
        func=CANCELAR_TRIGGER,
        name="trg_actividad_cancelar_inscripciones",
        operation=UpdateOf("cancelada_at"),
        when=After,
    ),
    Trigger(
        func=PROMOVER_TRIGGER,
        name="trg_actividad_promover_espera",
        operation=UpdateOf("cupo"),
        when=After,
    ),
)(Actividad)
