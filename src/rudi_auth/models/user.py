from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateField,
    DateTimeField,
    ForeignKey,
    Index,
    OneToOneField,
    Q,
)
from pgtrigger import After, Before, Insert, ReadOnly, Trigger, Update

from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_catalogos.enums import Etnias, Generos, TallasCamisa
from rudi_core.models import RudiProtectedModel
from rudi_estados.enums import InputSourceTypes
from rudi_estados.models import EstadoRudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################

ANON_TRIGGER: Final[str] = normalize_trigger("""
BEGIN
    IF OLD.anonimizado_at IS NOT NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'anonimizado_at',
            MESSAGE = 'Una cuenta anonimizada no admite modificaciones.';
    END IF;
    RETURN NEW;
END;
""")

ESTADO_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    is_terminal boolean;
BEGIN
    SELECT terminal
    INTO is_terminal
    FROM {EstadoRudiUser._meta.db_table}
    WHERE id = NEW.estado_id;
    IF is_terminal AND NEW.anonimizado_at IS NULL THEN
        NEW.anonimizado_at = NOW();
    ELSIF NOT is_terminal AND NEW.anonimizado_at IS NOT NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'estado_id',
            MESSAGE = 'Una cuenta con marca de anonimización no admite un estado no terminal.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

INGRESO_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    active boolean;
BEGIN
    SELECT allow_ingreso
    INTO active
    FROM {EstadoRudiUser._meta.db_table}
    WHERE id = NEW.estado_id;
    UPDATE {settings.AUTH_USER_MODEL.replace(".", "_").lower()}
    SET is_active = active
    WHERE id = NEW.user_id
    AND is_active IS DISTINCT FROM active;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

FECHA_NACIMIENTO_TRIGGER: Final[str] = normalize_trigger("""
BEGIN
    IF NEW.fecha_nacimiento IS NOT NULL AND (
        NEW.fecha_nacimiento < DATE '1930-01-01'
        OR
        NEW.fecha_nacimiento > CURRENT_DATE - INTERVAL '14 years'
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'fecha_nacimiento',
            MESSAGE = 'La fecha de nacimiento está fuera del rango admitido.';
    END IF;
    RETURN NEW;
END;
""")

########################################################################################


@track_table()
class RudiUser(RudiProtectedModel):
    user = OneToOneField(
        on_delete=RESTRICT,
        related_name="rudi",
        to=settings.AUTH_USER_MODEL,
    )

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="users",
        to=EstadoRudiUser,
    )

    origen = CharField(max_length=20)

    fecha_nacimiento = DateField(null=True)

    telefono = CharField(db_default="", default="", max_length=20)

    genero = CharField(db_default="", default="", max_length=20)
    etnia = CharField(db_default="", default="", max_length=20)
    talla = CharField(db_default="", default="", max_length=10)

    email_verified_at = DateTimeField(null=True)
    anonimizado_at = DateTimeField(null=True)

    class Meta(RudiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(origen__in=InputSourceTypes.values),
                name="chk_%(class)s_origen",
            ),
            CheckConstraint(
                condition=Q(genero__in=(*Generos.values, "")),
                name="chk_%(class)s_genero",
            ),
            CheckConstraint(
                condition=Q(etnia__in=(*Etnias.values, "")),
                name="chk_%(class)s_etnia",
            ),
            CheckConstraint(
                condition=Q(talla__in=(*TallasCamisa.values, "")),
                name="chk_%(class)s_talla",
            ),
        )

        indexes: Sequence[Index] = (
            *RudiProtectedModel.Meta.indexes,
            Index(fields=["estado"], name="idx_%(class)s_estado"),
            Index(
                condition=Q(fecha_nacimiento__isnull=False),
                fields=["fecha_nacimiento"],
                name="idx_%(class)s_nacimiento",
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiProtectedModel.Meta.triggers,
            ReadOnly(fields=["origen", "user"], name="trg_readonly_origen_user"),
            Trigger(
                name="trg_rudiuser_anonimizacion",
                operation=Update,
                when=Before,
                func=ANON_TRIGGER,
            ),
            Trigger(
                name="trg_rudiuser_estado",
                operation=(Insert | Update),
                when=Before,
                func=ESTADO_TRIGGER,
            ),
            Trigger(
                name="trg_rudiuser_fechanacimiento",
                operation=(Insert | Update),
                when=Before,
                func=FECHA_NACIMIENTO_TRIGGER,
            ),
            Trigger(
                name="trg_rudiuser_sync_active",
                operation=(Insert | Update),
                when=After,
                func=INGRESO_TRIGGER,
            ),
        )
