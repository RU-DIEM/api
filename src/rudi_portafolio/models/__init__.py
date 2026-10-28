# ruff: file-ignore[non-empty-init-module]

from typing import TYPE_CHECKING

from pgtrigger import (
    After,
    Insert,
    Trigger,
    UpdateOf,
    register as register_trigger,
)

from api_utils.strings import normalize_trigger
from rudi_portafolio.enums import PropuestaActividadRolTypes

from .propuesta import Propuesta
from .vinculos import PropuestaActividad, PropuestaIntegrante

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Final

########################################################################################

__all__: Sequence[str] = (
    "Propuesta",
    "PropuestaActividad",
    "PropuestaIntegrante",
)

########################################################################################

# the origin activity also starts the proposal's trail, so the trail never needs a
# second source to say where it began
ORIGEN_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    IF NEW.actividad_origen_id IS NULL
    OR (TG_OP = 'UPDATE' AND OLD.actividad_origen_id IS NOT DISTINCT FROM NEW.actividad_origen_id) THEN
        RETURN NULL;
    END IF;
    INSERT INTO {PropuestaActividad._meta.db_table}
    (propuesta_id, actividad_id, rol)
    VALUES (NEW.id, NEW.actividad_origen_id, '{PropuestaActividadRolTypes.ORIGINA.value}')
    ON CONFLICT DO NOTHING;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

########################################################################################

register_trigger(
    Trigger(
        func=ORIGEN_TRIGGER,
        name="trg_propuesta_actividad_origen",
        operation=(Insert | UpdateOf("actividad_origen_id")),
        when=After,
    ),
)(Propuesta)
