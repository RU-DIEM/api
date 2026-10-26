from typing import TYPE_CHECKING

from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    ForeignKey,
    Q,
    UniqueConstraint,
)

from api_utils.db import track_table
from rudi_catalogos.enums import NivelesAcademicos
from rudi_profiles.models.academia import Facultad
from rudi_profiles.models.base import RudiProfile

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@track_table()
class DocenteProfile(RudiProfile):
    facultad = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="docentes",
        to=Facultad,
    )

    nivel_academico = CharField(db_default="", default="", max_length=20)
    cargo = CharField(db_default="", default="", max_length=120)

    class Meta(RudiProfile.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(nivel_academico__in=(*NivelesAcademicos.values, "")),
                name="chk_%(class)s_nivel",
            ),
        )
