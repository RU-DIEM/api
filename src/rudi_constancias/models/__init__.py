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
from rudi_estados.models import EstadoConstancia
from rudi_participacion.models import Participacion

from .constancia import Constancia, ConstanciaParticipacion
from .plantilla import PlantillaConstancia

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Final

########################################################################################

__all__: Sequence[str] = (
    "Constancia",
    "ConstanciaParticipacion",
    "PlantillaConstancia",
)

########################################################################################

VERSION_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    IF NEW.cuerpo IS DISTINCT FROM OLD.cuerpo AND EXISTS (
        SELECT 1
        FROM {Constancia._meta.db_table}
        WHERE plantilla_id = OLD.id
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'cuerpo',
            MESSAGE = 'Esta versión ya se usó; el texto nuevo es una versión nueva.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

# annulling a participation annuls every live certificate that vouches for it, with
# the annulment's own reason, into a terminal state that is no longer `valid`
INVALIDAR_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    destino uuid;
BEGIN
    IF OLD.anulada_at IS NOT NULL OR NEW.anulada_at IS NULL THEN
        RETURN NULL;
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM {ConstanciaParticipacion._meta.db_table}
        AS puente
        JOIN {Constancia._meta.db_table}
        AS constancia
        ON constancia.id = puente.constancia_id
        WHERE puente.participacion_id = NEW.id
        AND constancia.anulada_at IS NULL
    ) THEN
        RETURN NULL;
    END IF;
    SELECT id
    INTO destino
    FROM {EstadoConstancia._meta.db_table}
    WHERE is_active
    AND terminal
    AND NOT valid
    ORDER BY require_motivo DESC, codigo
    LIMIT 1;
    IF NOT FOUND THEN
        RAISE check_violation
        USING
            COLUMN = 'anulada_at',
            MESSAGE = 'No hay un estado de constancia anulada configurado.';
    END IF;
    UPDATE {Constancia._meta.db_table}
    SET
        estado_id = destino,
        anulada_at = NEW.anulada_at,
        motivo_id = NEW.motivo_id,
        motivo_descripcion = NEW.motivo_descripcion
    WHERE anulada_at IS NULL
    AND id IN (
        SELECT constancia_id
        FROM {ConstanciaParticipacion._meta.db_table}
        WHERE participacion_id = NEW.id
    );
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

########################################################################################

register_trigger(
    Trigger(
        func=VERSION_TRIGGER,
        name="trg_plantillaconstancia_version_nueva",
        operation=UpdateOf("cuerpo"),
        when=Before,
    ),
)(PlantillaConstancia)

register_trigger(
    Trigger(
        func=INVALIDAR_TRIGGER,
        name="trg_participacion_invalidar_constancias",
        operation=UpdateOf("anulada_at"),
        when=After,
    ),
)(Participacion)
