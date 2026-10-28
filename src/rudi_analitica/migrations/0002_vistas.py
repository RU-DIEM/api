from typing import TYPE_CHECKING

from django.db import migrations

if TYPE_CHECKING:
    from typing import Final

########################################################################################

# a participation counts once it is validated, not annulled, and in a state that
# declares `efectiva` (RN-13); the same predicate feeds every view below
EFECTIVA: Final[str] = """
    p.validada_at IS NOT NULL
    AND p.anulada_at IS NULL
    AND EXISTS (
        SELECT 1
        FROM rudiestados_estadoparticipacion AS e
        WHERE e.id = p.estado_id
        AND e.efectiva
    )
"""

FORWARD: Final[str] = f"""
CREATE MATERIALIZED VIEW mv_participante_unico_anio AS
SELECT
    p.anio,
    count(DISTINCT p.user_id)::integer AS valor
FROM rudiparticipacion_participacion AS p
WHERE {EFECTIVA}
GROUP BY p.anio;

CREATE UNIQUE INDEX unq_mvparticipanteunicoanio_anio
ON mv_participante_unico_anio (anio);

CREATE MATERIALIZED VIEW mv_participacion_actividad AS
SELECT
    a.id AS actividad_id,
    a.anio,
    (
        SELECT count(*)
        FROM rudiparticipacion_inscripcion AS i
        WHERE i.actividad_id = a.id
    )::integer AS inscripciones,
    (
        SELECT count(*)
        FROM rudiparticipacion_participacion AS p
        WHERE p.actividad_id = a.id
        AND p.anulada_at IS NULL
    )::integer AS participaciones,
    (
        SELECT count(*)
        FROM rudiparticipacion_participacion AS p
        WHERE p.actividad_id = a.id
        AND {EFECTIVA}
    )::integer AS validadas
FROM rudiactividades_actividad AS a;

CREATE UNIQUE INDEX unq_mvparticipacionactividad_actividad
ON mv_participacion_actividad (actividad_id);

CREATE MATERIALIZED VIEW mv_saldo_puntos_user AS
SELECT
    m.user_id,
    coalesce(sum(m.puntos), 0)::integer AS saldo,
    coalesce(sum(m.puntos) FILTER (WHERE m.origen = 'automatico'), 0)::integer
        AS automatico,
    coalesce(sum(m.puntos) FILTER (WHERE m.origen <> 'automatico'), 0)::integer
        AS manual
FROM rudipuntos_movimientopunto AS m
WHERE m.revertido_at IS NULL
AND m.origen <> 'reverso'
GROUP BY m.user_id;

CREATE UNIQUE INDEX unq_mvsaldopuntosuser_user
ON mv_saldo_puntos_user (user_id);

CREATE MATERIALIZED VIEW mv_cobertura_carrera AS
WITH base AS (
    SELECT DISTINCT
        p.anio,
        ec.carrera_id,
        p.user_id
    FROM rudiparticipacion_participacion AS p
    JOIN rudiprofiles_estudianteprofile AS ep
    ON ep.user_id = p.user_id
    JOIN rudiprofiles_estudiantecarrera AS ec
    ON ec.profile_id = ep.id
    AND (ec.cerrada_at IS NULL OR extract(year FROM ec.cerrada_at) >= p.anio)
    WHERE {EFECTIVA}
)
SELECT
    base.anio || ':' || base.carrera_id AS clave,
    base.anio,
    base.carrera_id,
    count(*)::integer AS estudiantes,
    0 AS doble_titulacion
FROM base
GROUP BY base.anio, base.carrera_id
UNION ALL
SELECT
    totales.anio || ':total' AS clave,
    totales.anio,
    NULL AS carrera_id,
    count(*)::integer AS estudiantes,
    (count(*) FILTER (WHERE totales.carreras > 1))::integer AS doble_titulacion
FROM (
    SELECT anio, user_id, count(*) AS carreras
    FROM base
    GROUP BY anio, user_id
) AS totales
GROUP BY totales.anio;

CREATE UNIQUE INDEX unq_mvcoberturacarrera_clave
ON mv_cobertura_carrera (clave);
"""  # ruff: ignore[hardcoded-sql-expression]

REVERSE: Final[str] = """
DROP MATERIALIZED VIEW IF EXISTS mv_cobertura_carrera;
DROP MATERIALIZED VIEW IF EXISTS mv_saldo_puntos_user;
DROP MATERIALIZED VIEW IF EXISTS mv_participacion_actividad;
DROP MATERIALIZED VIEW IF EXISTS mv_participante_unico_anio;
"""

########################################################################################


class Migration(migrations.Migration):
    dependencies = [
        ("rudianalitica", "0001_initial"),
        ("rudiparticipacion", "0001_initial"),
        ("rudiprofiles", "0003_track_academia"),
        ("rudipuntos", "0001_initial"),
    ]

    operations = [migrations.RunSQL(reverse_sql=REVERSE, sql=FORWARD)]
