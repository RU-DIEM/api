from typing import TYPE_CHECKING, Final

from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
)
from django.db.models.functions import Now
from django.utils.timezone import now
from pgtrigger import Before, Insert, Trigger, Update, UpdateOf

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_actividades.models import Actividad
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo
from rudi_estados.models import EstadoAsignacionMentor
from rudi_estados.triggers import estado_lifecycle_triggers, motivo_ambito_trigger
from rudi_participacion.enums import AcompanamientoTypes
from rudi_profiles.models import MentorProfile

from .equipo import Equipo

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

ESTADO_COHERENTE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    estado RECORD;
BEGIN
    SELECT initial, terminal, require_motivo
    INTO estado
    FROM {EstadoAsignacionMentor._meta.db_table}
    WHERE id = NEW.estado_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'estado_id';
    END IF;
    IF estado.require_motivo AND NEW.motivo_id IS NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'motivo_id',
            MESSAGE = 'Este estado exige un motivo.';
    END IF;
    IF NOT estado.initial AND NEW.respondida_at IS NULL THEN
        NEW.respondida_at = clock_timestamp();
    END IF;
    IF estado.terminal AND NEW.finalizada_at IS NULL THEN
        NEW.finalizada_at = clock_timestamp();
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

MENTOR_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    confirmado timestamptz;
BEGIN
    SELECT confirmado_at
    INTO confirmado
    FROM {MentorProfile._meta.db_table}
    WHERE id = NEW.mentor_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'mentor_id';
    END IF;
    IF confirmado IS NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'mentor_id',
            MESSAGE = 'El perfil de mentor todavía no ha sido confirmado.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

EQUIPO_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    actividad_equipo uuid;
BEGIN
    IF NEW.equipo_id IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT actividad_id
    INTO actividad_equipo
    FROM {Equipo._meta.db_table}
    WHERE id = NEW.equipo_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'equipo_id';
    END IF;
    IF actividad_equipo <> NEW.actividad_id THEN
        RAISE check_violation
        USING
            COLUMN = 'equipo_id',
            MESSAGE = 'El equipo es de otra actividad.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

########################################################################################


@track_table()
class AsignacionMentor(ApiProtectedModel):
    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="mentores",
        to=Actividad,
    )

    mentor = ForeignKey(
        on_delete=RESTRICT,
        related_name="asignaciones",
        to=MentorProfile,
    )

    equipo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="mentores",
        to=Equipo,
    )

    tipo_acompanamiento = CharField(max_length=30)

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="asignaciones",
        to=EstadoAsignacionMentor,
    )

    propuesta_at = DateTimeField(db_default=Now(), default=now)
    respondida_at = DateTimeField(null=True)
    finalizada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="asignaciones",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    observaciones = TextField(db_default="", default="")
    enlace_evidencia = URLField(db_default="", default="", max_length=500)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(tipo_acompanamiento__in=AcompanamientoTypes.values),
                name="chk_%(class)s_tipo",
            ),
            CheckConstraint(
                condition=(
                    Q(respondida_at__isnull=True)
                    | Q(respondida_at__gte=F("propuesta_at"))
                ),
                name="chk_%(class)s_respuesta",
            ),
            UniqueConstraint(
                condition=Q(finalizada_at__isnull=True),
                fields=["actividad", "mentor", "equipo"],
                name="unq_%(class)s_vigente",
                nulls_distinct=False,
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                F("mentor"),
                F("propuesta_at").desc(),
                name="idx_%(class)s_mentor",
            ),
            Index(
                condition=Q(respondida_at__isnull=True, finalizada_at__isnull=True),
                fields=["propuesta_at"],
                name="idx_%(class)s_pendiente",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            *estado_lifecycle_triggers(
                entidad="asignacionmentor",
                model=EstadoAsignacionMentor,
            ),
            motivo_ambito_trigger(
                ambitos=(MotivoAmbitoTypes.REJECT_MENTORIA,),
                descripcion_field="motivo_descripcion",
                entidad="asignacionmentor",
                motivo_table=Motivo._meta.db_table,  # ruff: ignore[private-member-access]
            ),
            Trigger(
                func=ESTADO_COHERENTE_TRIGGER,
                name="trg_asignacionmentor_estado_coherente",
                operation=(Insert | UpdateOf("estado_id")),
                when=Before,
            ),
            Trigger(
                func=MENTOR_TRIGGER,
                name="trg_asignacionmentor_mentor_confirmado",
                operation=Insert,
                when=Before,
            ),
            Trigger(
                func=EQUIPO_TRIGGER,
                name="trg_asignacionmentor_equipo_coherente",
                operation=(Insert | Update),
                when=Before,
            ),
        )
