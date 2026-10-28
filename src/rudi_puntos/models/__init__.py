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
from rudi_actividades.models import Actividad
from rudi_estados.models import EstadoParticipacion
from rudi_participacion.enums import ParticipacionOrigenTypes
from rudi_participacion.models import Participacion, Reconocimiento
from rudi_puntos.enums import MovimientoOrigenTypes

from .movimiento import MovimientoPunto
from .regla import ReglaPuntuacion

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Final

########################################################################################

__all__: Sequence[str] = (
    "MovimientoPunto",
    "ReglaPuntuacion",
)

########################################################################################

ASIENTO: Final[str] = (
    f"INSERT INTO {MovimientoPunto._meta.db_table} "  # ruff: ignore[private-member-access]
    "(user_id, participacion_id, regla_id, puntos, origen, anio)"
)

# validating a participation grants its points in the same transaction (RN-08):
# the activity's `puntos_base` wins, else the most specific live rule whose
# criteria match on the validation date; no match means no entry, and the
# participation shows up in the review list of RF-A-31
OTORGAR_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    admite boolean;
    actividad RECORD;
    regla RECORD;
    fecha date;
BEGIN
    IF NEW.validada_at IS NULL
    OR NEW.anulada_at IS NOT NULL
    OR (TG_OP = 'UPDATE' AND OLD.validada_at IS NOT NULL)
    OR (TG_OP = 'INSERT' AND NEW.origen = '{ParticipacionOrigenTypes.LEGACY.value}') THEN
        RETURN NULL;
    END IF;
    SELECT allow_puntos
    INTO admite
    FROM {EstadoParticipacion._meta.db_table}
    WHERE id = NEW.estado_id;
    IF NOT admite THEN
        RETURN NULL;
    END IF;
    SELECT puntos_base, tipo_actividad_id, programa_id
    INTO actividad
    FROM {Actividad._meta.db_table}
    WHERE id = NEW.actividad_id;
    IF actividad.puntos_base IS NOT NULL THEN
        IF actividad.puntos_base <> 0 THEN
            {ASIENTO}
            VALUES (
                NEW.user_id, NEW.id, NULL, actividad.puntos_base,
                '{MovimientoOrigenTypes.AUTO.value}', NEW.anio
            )
            ON CONFLICT DO NOTHING;
        END IF;
        RETURN NULL;
    END IF;
    fecha := (NEW.validada_at AT TIME ZONE 'America/Managua')::date;
    SELECT id, puntos
    INTO regla
    FROM {ReglaPuntuacion._meta.db_table}
    AS r
    WHERE r.is_active
    AND r.vigencia @> fecha
    AND (r.tipo_actividad_id IS NULL OR r.tipo_actividad_id = actividad.tipo_actividad_id)
    AND (r.programa_id IS NULL OR r.programa_id = actividad.programa_id)
    AND (r.rol_id IS NULL OR r.rol_id = NEW.rol_id)
    AND (r.estado_participacion_id IS NULL OR r.estado_participacion_id = NEW.estado_id)
    AND (
        r.tipo_reconocimiento_id IS NULL
        OR EXISTS (
            SELECT 1
            FROM {Reconocimiento._meta.db_table}
            AS reconocimiento
            WHERE reconocimiento.participacion_id = NEW.id
            AND reconocimiento.tipo_id = r.tipo_reconocimiento_id
            AND reconocimiento.anulado_at IS NULL
        )
    )
    ORDER BY r.especificidad DESC
    LIMIT 1;
    IF FOUND AND regla.puntos <> 0 THEN
        {ASIENTO}
        VALUES (
            NEW.user_id, NEW.id, regla.id, regla.puntos,
            '{MovimientoOrigenTypes.AUTO.value}', NEW.anio
        )
        ON CONFLICT DO NOTHING;
    END IF;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

# annulling a participation reverts every live entry it produced, citing the
# annulment's own reason; `trg_movimientopunto_reverso_exacto` checks each one
REVERTIR_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    IF OLD.anulada_at IS NOT NULL OR NEW.anulada_at IS NULL THEN
        RETURN NULL;
    END IF;
    INSERT INTO {MovimientoPunto._meta.db_table}
    (user_id, participacion_id, puntos, origen, motivo_id, descripcion, revierte_id, anio)
    SELECT
        movimiento.user_id,
        movimiento.participacion_id,
        -movimiento.puntos,
        '{MovimientoOrigenTypes.REVERSO.value}',
        NEW.motivo_id,
        'Anulación de la participación.',
        movimiento.id,
        movimiento.anio
    FROM {MovimientoPunto._meta.db_table}
    AS movimiento
    WHERE movimiento.participacion_id = NEW.id
    AND movimiento.revertido_at IS NULL
    AND movimiento.origen <> '{MovimientoOrigenTypes.REVERSO.value}'
    ON CONFLICT DO NOTHING;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

########################################################################################

register_trigger(
    Trigger(
        func=OTORGAR_TRIGGER,
        name="trg_participacion_otorgar_puntos",
        operation=(Insert | UpdateOf("validada_at")),
        when=After,
    ),
    Trigger(
        func=REVERTIR_TRIGGER,
        name="trg_participacion_revertir_puntos",
        operation=UpdateOf("anulada_at"),
        when=After,
    ),
)(Participacion)
