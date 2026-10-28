from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    CASCADE,
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateTimeField,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    UniqueConstraint,
)
from pgtrigger import (
    After,
    Before,
    Deferred,
    Func,
    Insert,
    Trigger,
    Update,
)

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import NivelesCarrera

from .academia import Carrera
from .base import RudiProfile

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

ORDINALES: Final[str] = ", ".join(
    f"'{n.value}'" for n in NivelesCarrera if any(c.isdigit() for c in n.label)
)

DOMINIO_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    dominio text;
    correo text;
BEGIN
    dominio := rudi_parametro('registro.dominio_institucional') #>> '{{}}';
    IF dominio IS NULL OR dominio = '' THEN
        RETURN NEW;
    END IF;
    SELECT cuenta.email
    INTO correo
    FROM {RudiUser._meta.db_table}
    AS persona
    JOIN {settings.AUTH_USER_MODEL.replace(".", "_").lower()}
    AS cuenta
    ON cuenta.id = persona.user_id
    WHERE persona.id = NEW.user_id;
    IF lower(correo) NOT LIKE '%@' || lower(dominio) THEN
        RAISE check_violation
        USING
            COLUMN = 'user_id',
            MESSAGE = 'Un perfil de estudiante UAM exige un correo del dominio institucional.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

NIVEL_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    duracion smallint;
    ordinal integer;
BEGIN
    ordinal := array_position(ARRAY[{ORDINALES}]::text[], NEW.nivel);
    IF ordinal IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT carrera.duracion
    INTO duracion
    FROM {Carrera._meta.db_table}
    AS carrera
    WHERE carrera.id = NEW.carrera_id;
    IF duracion IS NOT NULL AND ordinal > duracion THEN
        RAISE check_violation
        USING
            COLUMN = 'nivel',
            MESSAGE = 'El nivel declarado excede la duración de la carrera.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

MIN_MAIN_TRIGGER: Final[Func] = Func(
    normalize_trigger("""
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM {meta.db_table}
            AS actual
            WHERE actual.profile_id = NEW.profile_id
            AND actual.is_main
            AND actual.cerrada_at IS NULL
        ) THEN
            RAISE check_violation
            USING
                COLUMN = 'is_main',
                MESSAGE = 'Un perfil de estudiante no puede quedar sin carrera principal vigente.';
        END IF;
        RETURN NULL;
    END;
    """)  # ruff: ignore[line-too-long]
)

########################################################################################


@track_table()
class EstudianteProfile(RudiProfile):
    class Meta(RudiProfile.Meta):  # ty: ignore[invalid-attribute-override]
        triggers: Sequence[Trigger] = (
            *RudiProfile.Meta.triggers,
            Trigger(
                name="trg_estudianteprofile_dominio",
                operation=(Insert | Update),
                when=Before,
                func=DOMINIO_TRIGGER,
            ),
        )


########################################################################################


@track_table()
class EstudianteCarrera(ApiProtectedModel):
    profile = ForeignKey(
        on_delete=CASCADE,
        related_name="carreras",
        to=EstudianteProfile,
    )

    carrera = ForeignKey(
        on_delete=RESTRICT,
        related_name="estudiantes",
        to=Carrera,
    )

    nivel = CharField(db_default="", default="", max_length=20)

    is_main = BooleanField(db_default=False, default=False)

    iniciada_en = PositiveSmallIntegerField(null=True)
    cerrada_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(nivel__in=(*NivelesCarrera.values, "")),
                name="chk_%(class)s_nivel",
            ),
            CheckConstraint(
                condition=(
                    Q(iniciada_en__isnull=True)
                    | Q(iniciada_en__gte=2000, iniciada_en__lte=3000)
                ),
                name="chk_%(class)s_iniciada",
            ),
            UniqueConstraint(
                fields=["profile", "carrera"],
                name="unq_%(class)s_par",
            ),
            UniqueConstraint(
                condition=Q(cerrada_at__isnull=True, is_main=True),
                fields=["profile"],
                name="unq_%(class)s_principal",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                condition=Q(cerrada_at__isnull=True),
                fields=["carrera"],
                name="idx_%(class)s_carrera",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            Trigger(
                name="trg_estudiantecarrera_nivel",
                operation=(Insert | Update),
                when=Before,
                func=NIVEL_TRIGGER,
            ),
            Trigger(
                name="trg_estudiantecarrera_carrera",
                operation=(Insert | Update),
                timing=Deferred,
                when=After,
                func=MIN_MAIN_TRIGGER,
            ),
        )
