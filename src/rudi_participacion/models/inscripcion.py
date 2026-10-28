from typing import TYPE_CHECKING

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

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_catalogos.models import Motivo
from rudi_estados.enums import InputSourceTypes
from rudi_estados.models import EstadoInscripcion

if TYPE_CHECKING:
    from collections.abc import Sequence

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
