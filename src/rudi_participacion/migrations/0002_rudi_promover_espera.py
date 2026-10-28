from typing import TYPE_CHECKING

from django.db import migrations

if TYPE_CHECKING:
    from typing import Final

########################################################################################

# shared by `trg_inscripcion_promover_espera` (a seat was freed) and
# `trg_actividad_promover_espera` (the quota grew); promotes in `posicion_espera`
# order while there is room, through the transition the catalog declares for the
# `sistema` actor into a state that `consume_cupo`, and stops quietly if none is
# declared: promoting is the DIEM's call, made by declaring that transition
FORWARD: Final[str] = """
CREATE OR REPLACE FUNCTION public.rudi_promover_espera(p_actividad uuid)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    actividad RECORD;
    candidata RECORD;
    destino uuid;
    actor_previo text;
BEGIN
    LOOP
        SELECT cupo, inscritos_activos, cancelada_at
        INTO actividad
        FROM rudiactividades_actividad
        WHERE id = p_actividad
        FOR UPDATE;

        EXIT WHEN NOT FOUND
            OR actividad.cancelada_at IS NOT NULL
            OR (actividad.cupo IS NOT NULL AND actividad.inscritos_activos >= actividad.cupo);

        SELECT id, estado_id
        INTO candidata
        FROM rudiparticipacion_inscripcion
        WHERE actividad_id = p_actividad
        AND cerrada_at IS NULL
        AND posicion_espera IS NOT NULL
        ORDER BY posicion_espera
        LIMIT 1
        FOR UPDATE;

        EXIT WHEN NOT FOUND;

        SELECT t.to_estado_id
        INTO destino
        FROM rudiestados_transicionestadoinscripcion AS t
        JOIN rudiestados_estadoinscripcion AS e
        ON e.id = t.to_estado_id
        WHERE t.from_estado_id = candidata.estado_id
        AND t.actor = 'sistema'
        AND t.is_active
        AND e.is_active
        AND e.consume_cupo
        ORDER BY e.codigo
        LIMIT 1;

        EXIT WHEN NOT FOUND;

        actor_previo := current_setting('rudi.actor', true);
        PERFORM set_config('rudi.actor', 'sistema', true);

        UPDATE rudiparticipacion_inscripcion
        SET estado_id = destino, posicion_espera = NULL
        WHERE id = candidata.id;

        PERFORM set_config('rudi.actor', coalesce(actor_previo, ''), true);
    END LOOP;
END;
$$;
"""

REVERSE: Final[str] = """
DROP FUNCTION IF EXISTS public.rudi_promover_espera(uuid);
"""

########################################################################################


class Migration(migrations.Migration):
    dependencies = [("rudiparticipacion", "0001_initial")]

    operations = [migrations.RunSQL(reverse_sql=REVERSE, sql=FORWARD)]
