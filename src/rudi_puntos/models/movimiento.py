from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    SmallIntegerField,
    UniqueConstraint,
)
from pgtrigger import After, Before, Func, Insert, ReadOnly, Trigger

from api_core.models.base import ApiProtectedModel
from api_utils.strings import normalize_trigger
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo
from rudi_estados.triggers import motivo_ambito_trigger
from rudi_participacion.models import Participacion
from rudi_puntos.enums import MovimientoOrigenTypes

from .regla import ReglaPuntuacion

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

SNAPSHOT_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    IF NEW.participacion_id IS NOT NULL THEN
        SELECT user_id, anio
        INTO NEW.user_id, NEW.anio
        FROM {Participacion._meta.db_table}
        WHERE id = NEW.participacion_id;
        IF NOT FOUND THEN
            RAISE foreign_key_violation USING COLUMN = 'participacion_id';
        END IF;
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

REVERSO_TRIGGER: Final[Func] = Func(
    normalize_trigger(f"""
    DECLARE
        original RECORD;
    BEGIN
        IF NEW.revierte_id IS NULL THEN
            RETURN NEW;
        END IF;
        SELECT user_id, puntos, origen, revertido_at
        INTO original
        FROM {{meta.db_table}}
        WHERE id = NEW.revierte_id;
        IF NOT FOUND THEN
            RAISE foreign_key_violation USING COLUMN = 'revierte_id';
        END IF;
        IF original.origen = '{MovimientoOrigenTypes.REVERSO.value}' THEN
            RAISE check_violation
            USING
                COLUMN = 'revierte_id',
                MESSAGE = 'Un reverso no se revierte.';
        END IF;
        IF original.revertido_at IS NOT NULL THEN
            RAISE check_violation
            USING
                COLUMN = 'revierte_id',
                MESSAGE = 'El asiento ya fue revertido.';
        END IF;
        IF original.user_id <> NEW.user_id THEN
            RAISE check_violation
            USING
                COLUMN = 'user_id',
                MESSAGE = 'Un reverso es de la misma persona que el asiento.';
        END IF;
        IF original.puntos <> -NEW.puntos THEN
            RAISE check_violation
            USING
                COLUMN = 'puntos',
                MESSAGE = 'Un reverso anula el asiento completo, con el signo contrario.';
        END IF;
        RETURN NEW;
    END;
    """)  # ruff: ignore[hardcoded-sql-expression, line-too-long]
)

MARCAR_TRIGGER: Final[Func] = Func(
    normalize_trigger("""
    BEGIN
        IF NEW.revierte_id IS NOT NULL THEN
            UPDATE {meta.db_table}
            SET revertido_at = NEW.created_at
            WHERE id = NEW.revierte_id
            AND revertido_at IS NULL;
        END IF;
        RETURN NULL;
    END;
    """)
)

########################################################################################


# a ledger entry is never edited: the only write after the insert is the reversal
# stamping `revertido_at`, which `trg_readonly_asiento` leaves through
class MovimientoPunto(ApiProtectedModel):
    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="movimientos",
        to=RudiUser,
    )

    participacion = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="movimientos",
        to=Participacion,
    )

    regla = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="movimientos",
        to=ReglaPuntuacion,
    )

    puntos = SmallIntegerField()

    origen = CharField(max_length=20)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="movimientos",
        to=Motivo,
    )
    descripcion = CharField(db_default="", default="", max_length=300)

    revierte = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="+",
        to="self",
    )
    revertido_at = DateTimeField(null=True)

    registrado_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="movimientos_registrados",
        to=settings.AUTH_USER_MODEL,
    )

    anio = PositiveSmallIntegerField()

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(origen__in=MovimientoOrigenTypes.values),
                name="chk_%(class)s_origen",
            ),
            CheckConstraint(
                condition=~Q(puntos=0),
                name="chk_%(class)s_puntos_no_cero",
            ),
            CheckConstraint(
                condition=Q(anio__gte=2000, anio__lte=2100),
                name="chk_%(class)s_anio",
            ),
            CheckConstraint(
                condition=Q(regla__isnull=True) | Q(origen=MovimientoOrigenTypes.AUTO),
                name="chk_%(class)s_regla_automatica",
            ),
            CheckConstraint(
                condition=(
                    Q(origen=MovimientoOrigenTypes.REVERSO, revierte__isnull=False)
                    | (
                        ~Q(origen=MovimientoOrigenTypes.REVERSO)
                        & Q(revierte__isnull=True)
                    )
                ),
                name="chk_%(class)s_reverso_coherente",
            ),
            CheckConstraint(
                condition=(
                    ~Q(
                        origen__in=(
                            MovimientoOrigenTypes.MANUAL,
                            MovimientoOrigenTypes.REVERSO,
                        ),
                    )
                    | Q(motivo__isnull=False)
                ),
                name="chk_%(class)s_motivo_requerido",
            ),
            CheckConstraint(
                condition=Q(revierte__isnull=True) | ~Q(revierte=F("id")),
                name="chk_%(class)s_no_autorreverso",
            ),
            UniqueConstraint(
                condition=Q(revierte__isnull=False),
                fields=["revierte"],
                name="unq_%(class)s_reverso",
            ),
            UniqueConstraint(
                condition=Q(origen=MovimientoOrigenTypes.AUTO),
                fields=["participacion"],
                name="unq_%(class)s_automatico",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                condition=(
                    Q(revertido_at__isnull=True)
                    & ~Q(origen=MovimientoOrigenTypes.REVERSO)
                ),
                fields=["user"],
                name="idx_%(class)s_user_vivo",
            ),
            Index(
                F("user"),
                F("created_at").desc(),
                name="idx_%(class)s_user_detalle",
            ),
            Index(fields=["anio", "origen"], name="idx_%(class)s_anio_origen"),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            ReadOnly(
                exclude=["revertido_at", "updated_at"],
                name="trg_readonly_asiento",
            ),
            motivo_ambito_trigger(
                ambitos=(
                    MotivoAmbitoTypes.AJUSTE_PUNTOS,
                    MotivoAmbitoTypes.NULL_PARTICIPACION,
                ),
                descripcion_field="descripcion",
                entidad="movimientopunto",
                motivo_table=Motivo._meta.db_table,  # ruff: ignore[private-member-access]
            ),
            Trigger(
                func=SNAPSHOT_TRIGGER,
                name="trg_movimientopunto_snapshot",
                operation=Insert,
                when=Before,
            ),
            Trigger(
                func=REVERSO_TRIGGER,
                name="trg_movimientopunto_reverso_exacto",
                operation=Insert,
                when=Before,
            ),
            Trigger(
                func=MARCAR_TRIGGER,
                name="trg_movimientopunto_marcar_revertido",
                operation=Insert,
                when=After,
            ),
        )
