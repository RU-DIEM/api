from typing import TYPE_CHECKING, Final

from django.db.models import (
    CASCADE,
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Q,
    UniqueConstraint,
)
from django.db.models.functions import Lower
from pgtrigger import Before, Func, Insert, Trigger, Update, UpdateOf

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_estados.enums import ActorTypes

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

ADMITE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    admite boolean;
BEGIN
    SELECT admite_equipos
    INTO admite
    FROM {Actividad._meta.db_table}
    WHERE id = NEW.actividad_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'actividad_id';
    END IF;
    IF NOT admite THEN
        RAISE check_violation
        USING
            COLUMN = 'actividad_id',
            MESSAGE = 'La actividad no admite equipos.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

########################################################################################


@track_table()
class Equipo(ApiProtectedModel):
    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="equipos",
        to=Actividad,
    )

    nombre = CharField(max_length=120)
    codigo_union = CharField(max_length=10)

    creado_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="equipos_creados",
        to=RudiUser,
    )

    congelado_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(codigo_union__regex=r"^[A-Z0-9]{6,10}$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(nombre__len__gte=2),
                name="chk_%(class)s_nombre",
            ),
            UniqueConstraint(fields=["codigo_union"], name="unq_%(class)s_codigo"),
            UniqueConstraint(
                F("actividad"),
                Lower("nombre"),
                name="unq_%(class)s_nombre",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            Trigger(
                func=ADMITE_TRIGGER,
                name="trg_equipo_actividad_admite",
                operation=Insert,
                when=Before,
            ),
        )


########################################################################################

# a member is "live" while `retirado_at` is null; every rule below is checked when a
# membership becomes live, on insert or when `retirado_at` is cleared
VIVO: Final[str] = (
    "NEW.retirado_at IS NULL AND (TG_OP = 'INSERT' OR OLD.retirado_at IS NOT NULL)"
)

UN_EQUIPO_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    IF {VIVO} AND EXISTS (
        SELECT 1
        FROM {{meta.db_table}}
        AS otro
        JOIN {Equipo._meta.db_table}
        AS equipo_otro
        ON equipo_otro.id = otro.equipo_id
        WHERE otro.user_id = NEW.user_id
        AND otro.retirado_at IS NULL
        AND otro.equipo_id <> NEW.equipo_id
        AND equipo_otro.actividad_id = (
            SELECT actividad_id
            FROM {Equipo._meta.db_table}
            WHERE id = NEW.equipo_id
        )
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'user_id',
            MESSAGE = 'La persona ya pertenece a otro equipo de esta actividad.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

TAMANO_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    maximo smallint;
BEGIN
    IF NOT ({VIVO}) THEN
        RETURN NEW;
    END IF;
    SELECT actividad.equipo_max
    INTO maximo
    FROM {Equipo._meta.db_table}
    AS equipo
    JOIN {Actividad._meta.db_table}
    AS actividad
    ON actividad.id = equipo.actividad_id
    WHERE equipo.id = NEW.equipo_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'equipo_id';
    END IF;
    IF maximo IS NOT NULL AND (
        SELECT count(*)
        FROM {{meta.db_table}}
        WHERE equipo_id = NEW.equipo_id
        AND retirado_at IS NULL
        AND id <> NEW.id
    ) >= maximo THEN
        RAISE check_violation
        USING
            COLUMN = 'equipo_id',
            MESSAGE = 'El equipo ya tiene el máximo de miembros de la actividad.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

CONGELADO_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    congelado timestamptz;
BEGIN
    SELECT congelado_at
    INTO congelado
    FROM {Equipo._meta.db_table}
    WHERE id = NEW.equipo_id;
    IF congelado IS NOT NULL
    AND rudi_actor() IS DISTINCT FROM '{ActorTypes.ADMIN.value}' THEN
        RAISE check_violation
        USING
            COLUMN = 'equipo_id',
            MESSAGE = 'La composición del equipo está congelada.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]


########################################################################################


@track_table()
class EquipoMiembro(ApiProtectedModel):
    equipo = ForeignKey(
        on_delete=CASCADE,
        related_name="miembros",
        to=Equipo,
    )

    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="equipos",
        to=RudiUser,
    )

    is_lider = BooleanField(db_default=False, default=False)

    retirado_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(
                condition=Q(retirado_at__isnull=True),
                fields=["equipo", "user"],
                name="unq_%(class)s_vigente",
            ),
            UniqueConstraint(
                condition=Q(is_lider=True, retirado_at__isnull=True),
                fields=["equipo"],
                name="unq_%(class)s_lider",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            Trigger(
                func=Func(CONGELADO_TRIGGER),
                name="trg_equipomiembro_congelado",
                operation=(Insert | Update),
                when=Before,
            ),
            Trigger(
                func=Func(TAMANO_TRIGGER),
                name="trg_equipomiembro_tamano_max",
                operation=(Insert | UpdateOf("retirado_at")),
                when=Before,
            ),
            Trigger(
                func=Func(UN_EQUIPO_TRIGGER),
                name="trg_equipomiembro_un_equipo_actividad",
                operation=(Insert | UpdateOf("retirado_at")),
                when=Before,
            ),
        )
