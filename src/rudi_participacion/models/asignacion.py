from typing import TYPE_CHECKING

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

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from rudi_actividades.models import Actividad
from rudi_catalogos.models import Motivo
from rudi_estados.models import EstadoAsignacionMentor
from rudi_participacion.enums import AcompanamientoTypes
from rudi_profiles.models import MentorProfile

from .equipo import Equipo

if TYPE_CHECKING:
    from collections.abc import Sequence

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
