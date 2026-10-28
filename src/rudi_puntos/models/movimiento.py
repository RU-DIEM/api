from typing import TYPE_CHECKING

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
from pgtrigger import ReadOnly

from api_core.models.base import ApiProtectedModel
from rudi_auth.models import RudiUser
from rudi_catalogos.models import Motivo
from rudi_participacion.models import Participacion
from rudi_puntos.enums import MovimientoOrigenTypes

from .regla import ReglaPuntuacion

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pgtrigger import Trigger

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
        )
