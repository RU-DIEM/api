from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateField,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
)
from pgtrigger import Before, Insert, ReadOnly, Trigger, Update, UpdateOf

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo, RolParticipacion, TipoReconocimiento
from rudi_core.triggers import catalogo_activo_trigger
from rudi_estados.models import (
    EstadoActividad,
    EstadoParticipacion,
    TransicionEstadoParticipacion,
)
from rudi_estados.triggers import estado_lifecycle_triggers, motivo_ambito_trigger
from rudi_participacion.enums import ParticipacionOrigenTypes

from .equipo import Equipo
from .inscripcion import Inscripcion

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

SNAPSHOT_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    SELECT anio
    INTO NEW.anio
    FROM {Actividad._meta.db_table}
    WHERE id = NEW.actividad_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'actividad_id';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

ESTADO_COHERENTE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    efectiva boolean;
BEGIN
    SELECT estado.efectiva
    INTO efectiva
    FROM {EstadoParticipacion._meta.db_table}
    AS estado
    WHERE estado.id = NEW.estado_id;
    IF efectiva AND NEW.validada_at IS NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'validada_at',
            MESSAGE = 'Un estado efectivo exige una participación validada.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

COHERENCIA_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    inscripcion RECORD;
    actividad_equipo uuid;
BEGIN
    IF NEW.inscripcion_id IS NOT NULL THEN
        SELECT actividad_id, user_id
        INTO inscripcion
        FROM {Inscripcion._meta.db_table}
        WHERE id = NEW.inscripcion_id;
        IF NOT FOUND THEN
            RAISE foreign_key_violation USING COLUMN = 'inscripcion_id';
        END IF;
        IF inscripcion.actividad_id <> NEW.actividad_id
        OR inscripcion.user_id <> NEW.user_id THEN
            RAISE check_violation
            USING
                COLUMN = 'inscripcion_id',
                MESSAGE = 'La inscripción es de otra persona o de otra actividad.';
        END IF;
    END IF;
    IF NEW.equipo_id IS NOT NULL THEN
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
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

VALIDABLE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    admite boolean;
BEGIN
    IF NEW.validada_at IS NULL
    OR (TG_OP = 'UPDATE' AND OLD.validada_at IS NOT NULL) THEN
        RETURN NEW;
    END IF;
    SELECT estado.allow_validacion
    INTO admite
    FROM {Actividad._meta.db_table}
    AS actividad
    JOIN {EstadoActividad._meta.db_table}
    AS estado
    ON estado.id = actividad.estado_id
    WHERE actividad.id = NEW.actividad_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'actividad_id';
    END IF;
    IF NOT admite THEN
        RAISE check_violation
        USING
            COLUMN = 'validada_at',
            MESSAGE = 'La actividad no admite validar participaciones en su estado.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

########################################################################################


@track_table()
class Participacion(ApiProtectedModel):
    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=RudiUser,
    )

    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Actividad,
    )

    inscripcion = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Inscripcion,
    )

    anio = PositiveSmallIntegerField()

    rol = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=RolParticipacion,
    )

    equipo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Equipo,
    )

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=EstadoParticipacion,
    )

    origen = CharField(
        db_default=ParticipacionOrigenTypes.ADMIN,
        default=ParticipacionOrigenTypes.ADMIN,
        max_length=20,
    )

    fecha_inicio = DateField(null=True)
    fecha_fin = DateField(null=True)

    validada_at = DateTimeField(null=True)
    validada_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones_validadas",
        to=settings.AUTH_USER_MODEL,
    )

    enlace_evidencia = URLField(db_default="", default="", max_length=500)
    observaciones = TextField(db_default="", default="")

    anulada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(origen__in=ParticipacionOrigenTypes.values),
                name="chk_%(class)s_origen",
            ),
            CheckConstraint(
                condition=Q(anio__gte=2000, anio__lte=2100),
                name="chk_%(class)s_anio",
            ),
            CheckConstraint(
                condition=(
                    Q(validada_at__isnull=True, validada_por__isnull=True)
                    | Q(validada_at__isnull=False, validada_por__isnull=False)
                ),
                name="chk_%(class)s_validacion_coherente",
            ),
            CheckConstraint(
                condition=(
                    Q(anulada_at__isnull=True, motivo__isnull=True)
                    | Q(anulada_at__isnull=False, motivo__isnull=False)
                ),
                name="chk_%(class)s_anulacion",
            ),
            CheckConstraint(
                condition=Q(anulada_at__isnull=True) | Q(validada_at__isnull=False),
                name="chk_%(class)s_anulacion_validada",
            ),
            CheckConstraint(
                condition=(
                    Q(fecha_fin__isnull=True)
                    | Q(fecha_inicio__isnull=True)
                    | Q(fecha_fin__gte=F("fecha_inicio"))
                ),
                name="chk_%(class)s_fechas",
            ),
            UniqueConstraint(
                condition=Q(anulada_at__isnull=True),
                fields=["user", "actividad"],
                name="unq_%(class)s_persona_activa",
            ),
            UniqueConstraint(
                condition=Q(inscripcion__isnull=False, anulada_at__isnull=True),
                fields=["inscripcion"],
                name="unq_%(class)s_inscripcion",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(F("user"), F("anio").desc(), name="idx_%(class)s_user_anio"),
            Index(
                fields=["actividad", "estado"],
                name="idx_%(class)s_actividad_estado",
            ),
            Index(
                condition=Q(validada_at__isnull=False, anulada_at__isnull=True),
                fields=["anio", "actividad"],
                name="idx_%(class)s_efectiva_anio",
            ),
            Index(
                condition=Q(validada_at__isnull=True, anulada_at__isnull=True),
                fields=["actividad"],
                name="idx_%(class)s_sin_validar",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            *estado_lifecycle_triggers(
                entidad="participacion",
                model=EstadoParticipacion,
                transicion_model=TransicionEstadoParticipacion,
            ),
            catalogo_activo_trigger(
                catalogos={"rol_id": RolParticipacion},
                entidad="participacion",
            ),
            motivo_ambito_trigger(
                ambitos=(MotivoAmbitoTypes.NULL_PARTICIPACION,),
                descripcion_field="motivo_descripcion",
                entidad="participacion",
                motivo_table=Motivo._meta.db_table,  # ruff: ignore[private-member-access]
            ),
            ReadOnly(
                fields=["actividad", "anio", "user"],
                name="trg_readonly_snapshot",
            ),
            Trigger(
                func=SNAPSHOT_TRIGGER,
                name="trg_participacion_snapshot",
                operation=Insert,
                when=Before,
            ),
            Trigger(
                func=ESTADO_COHERENTE_TRIGGER,
                name="trg_participacion_estado_coherente",
                operation=(Insert | UpdateOf("estado_id", "validada_at")),
                when=Before,
            ),
            Trigger(
                func=COHERENCIA_TRIGGER,
                name="trg_participacion_actividad_coherente",
                operation=(Insert | Update),
                when=Before,
            ),
            Trigger(
                func=VALIDABLE_TRIGGER,
                name="trg_participacion_actividad_validable",
                operation=(Insert | UpdateOf("validada_at")),
                when=Before,
            ),
        )


########################################################################################


@track_table()
class Reconocimiento(ApiProtectedModel):
    participacion = ForeignKey(
        on_delete=RESTRICT,
        related_name="reconocimientos",
        to=Participacion,
    )

    tipo = ForeignKey(
        on_delete=RESTRICT,
        related_name="reconocimientos",
        to=TipoReconocimiento,
    )

    descripcion = CharField(max_length=300)
    posicion = PositiveSmallIntegerField(null=True)
    otorgado_en = DateField(null=True)

    enlace_evidencia = URLField(db_default="", default="", max_length=500)

    anulado_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint] = (
            CheckConstraint(
                condition=Q(posicion__isnull=True) | Q(posicion__gt=0),
                name="chk_%(class)s_posicion",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                F("tipo"),
                F("otorgado_en").desc(),
                condition=Q(anulado_at__isnull=True),
                name="idx_%(class)s_tipo",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            catalogo_activo_trigger(
                catalogos={"tipo_id": TipoReconocimiento},
                entidad="reconocimiento",
            ),
        )
