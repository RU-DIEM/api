from typing import TYPE_CHECKING

from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    ForeignKey,
    Q,
    TextField,
    UniqueConstraint,
)

from api_utils.db import track_table
from rudi_profiles.enums import OcupacionTypes

from .academia import Institucion
from .base import RudiProfile

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@track_table()
class ExternoProfile(RudiProfile):
    institucion = ForeignKey(
        on_delete=RESTRICT,
        related_name="externos",
        to=Institucion,
    )

    ocupacion = CharField(max_length=30)
    ocupacion_detalle = TextField(db_default="", default="")

    carrera_externa = CharField(db_default="", default="", max_length=150)

    class Meta(RudiProfile.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(ocupacion__in=OcupacionTypes.values),
                name="chk_%(class)s_ocupacion",
            ),
            CheckConstraint(
                condition=(
                    Q(ocupacion=OcupacionTypes.ESTUDIANTE) | Q(carrera_externa="")
                ),
                name="chk_%(class)s_carrera_externa",
            ),
            CheckConstraint(
                condition=Q(ocupacion_detalle__len__lte=500),
                name="chk_%(class)s_detalle",
            ),
        )
