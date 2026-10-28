from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    TextField,
    UniqueConstraint,
)
from pgtrigger import (
    After,
    Before,
    Insert,
    ReadOnly,
    Trigger,
    UpdateOf,
)

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo
from rudi_estados.enums import InputSourceTypes
from rudi_estados.models import (
    EstadoActividad,
    EstadoInscripcion,
    TransicionEstadoInscripcion,
)
from rudi_estados.triggers import estado_lifecycle_triggers, motivo_ambito_trigger

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

ESTADO_COHERENTE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    estado RECORD;
BEGIN
    SELECT terminal, consume_cupo
    INTO estado
    FROM {EstadoInscripcion._meta.db_table}
    WHERE id = NEW.estado_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'estado_id';
    END IF;
    IF estado.terminal <> (NEW.cerrada_at IS NOT NULL) THEN
        RAISE check_violation
        USING
            COLUMN = 'cerrada_at',
            MESSAGE = 'Una inscripción está cerrada si y solo si su estado es terminal.';
    END IF;
    IF estado.consume_cupo AND NEW.posicion_espera IS NOT NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'posicion_espera',
            MESSAGE = 'Una inscripción en lista de espera no ocupa cupo.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

VENTANA_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    ventana RECORD;
BEGIN
    IF NEW.origen <> '{InputSourceTypes.SELF.value}' THEN
        RETURN NEW;
    END IF;
    SELECT
        actividad.inscripcion_abre_at AS abre,
        actividad.inscripcion_cierra_at AS cierra,
        estado.allow_inscripcion AS admite
    INTO ventana
    FROM {Actividad._meta.db_table}
    AS actividad
    JOIN {EstadoActividad._meta.db_table}
    AS estado
    ON estado.id = actividad.estado_id
    WHERE actividad.id = NEW.actividad_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'actividad_id';
    END IF;
    IF NOT ventana.admite
    OR (ventana.abre IS NOT NULL AND now() < ventana.abre)
    OR (ventana.cierra IS NOT NULL AND now() >= ventana.cierra) THEN
        RAISE check_violation
        USING
            COLUMN = 'actividad_id',
            MESSAGE = 'La actividad no admite inscripciones en este momento.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

CONTADOR_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    nuevo boolean;
    previo boolean := false;
BEGIN
    IF NEW.is_excepcion_cupo THEN
        RETURN NULL;
    END IF;
    SELECT consume_cupo
    INTO nuevo
    FROM {EstadoInscripcion._meta.db_table}
    WHERE id = NEW.estado_id;
    IF TG_OP = 'UPDATE' THEN
        SELECT consume_cupo
        INTO previo
        FROM {EstadoInscripcion._meta.db_table}
        WHERE id = OLD.estado_id;
    END IF;
    IF nuevo AND NOT previo THEN
        UPDATE {Actividad._meta.db_table}
        SET inscritos_activos = inscritos_activos + 1
        WHERE id = NEW.actividad_id;
    ELSIF previo AND NOT nuevo THEN
        UPDATE {Actividad._meta.db_table}
        SET inscritos_activos = inscritos_activos - 1
        WHERE id = NEW.actividad_id;
    END IF;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

PROMOVER_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    nuevo boolean;
    previo boolean;
BEGIN
    SELECT consume_cupo INTO nuevo
    FROM {EstadoInscripcion._meta.db_table}
    WHERE id = NEW.estado_id;
    SELECT consume_cupo INTO previo
    FROM {EstadoInscripcion._meta.db_table}
    WHERE id = OLD.estado_id;
    IF previo AND NOT nuevo AND NOT NEW.is_excepcion_cupo THEN
        PERFORM rudi_promover_espera(NEW.actividad_id);
    END IF;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

########################################################################################


@track_table()
class Inscripcion(ApiProtectedModel):
    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="inscripciones",
        to=RudiUser,
    )

    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="inscripciones",
        to=Actividad,
    )

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="inscripciones",
        to=EstadoInscripcion,
    )

    origen = CharField(max_length=20)

    creada_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="inscripciones_creadas",
        to=settings.AUTH_USER_MODEL,
    )

    posicion_espera = PositiveSmallIntegerField(null=True)

    is_excepcion_cupo = BooleanField(db_default=False, default=False)

    confirmada_at = DateTimeField(null=True)
    cerrada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="inscripciones",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(origen__in=InputSourceTypes.values),
                name="chk_%(class)s_origen",
            ),
            CheckConstraint(
                condition=(
                    Q(origen=InputSourceTypes.MODERN, creada_por__isnull=False)
                    | (~Q(origen=InputSourceTypes.MODERN) & Q(creada_por__isnull=True))
                ),
                name="chk_%(class)s_creador",
            ),
            CheckConstraint(
                condition=(
                    Q(cerrada_at__isnull=True, motivo__isnull=True)
                    | Q(cerrada_at__isnull=False, motivo__isnull=False)
                ),
                name="chk_%(class)s_cierre",
            ),
            CheckConstraint(
                condition=Q(posicion_espera__isnull=True) | Q(posicion_espera__gt=0),
                name="chk_%(class)s_espera_positiva",
            ),
            UniqueConstraint(
                condition=Q(cerrada_at__isnull=True),
                fields=["user", "actividad"],
                name="unq_%(class)s_persona_activa",
            ),
            UniqueConstraint(
                condition=Q(posicion_espera__isnull=False),
                fields=["actividad", "posicion_espera"],
                name="unq_%(class)s_posicion_espera",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(fields=["actividad", "estado"], name="idx_%(class)s_actividad"),
            Index(
                F("user"),
                F("created_at").desc(),
                name="idx_%(class)s_user",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            *estado_lifecycle_triggers(
                entidad="inscripcion",
                model=EstadoInscripcion,
                transicion_model=TransicionEstadoInscripcion,
            ),
            motivo_ambito_trigger(
                ambitos=(
                    MotivoAmbitoTypes.CANCEL_INSCRIPCION,
                    MotivoAmbitoTypes.CANCEL_ACTIVIDAD,
                ),
                descripcion_field="motivo_descripcion",
                entidad="inscripcion",
                motivo_table=Motivo._meta.db_table,  # ruff: ignore[private-member-access]
            ),
            ReadOnly(
                fields=["actividad", "is_excepcion_cupo", "origen", "user"],
                name="trg_readonly_origen",
            ),
            Trigger(
                func=ESTADO_COHERENTE_TRIGGER,
                name="trg_inscripcion_estado_coherente",
                operation=(
                    Insert | UpdateOf("estado_id", "cerrada_at", "posicion_espera")
                ),
                when=Before,
            ),
            Trigger(
                func=VENTANA_TRIGGER,
                name="trg_inscripcion_ventana_abierta",
                operation=Insert,
                when=Before,
            ),
            Trigger(
                func=CONTADOR_TRIGGER,
                name="trg_inscripcion_contador",
                operation=(Insert | UpdateOf("estado_id")),
                when=After,
            ),
            Trigger(
                func=PROMOVER_TRIGGER,
                name="trg_inscripcion_promover_espera",
                operation=UpdateOf("estado_id"),
                when=After,
            ),
        )
