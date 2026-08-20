from typing import TYPE_CHECKING

from django.db.models import (
    BooleanField,
    CharField,
    CheckConstraint,
    Q,
    UniqueConstraint,
)
from django.db.models.functions import Lower

from rudi_catalogos.enums import MotivoAmbitoTypes, MotivoVisibilidadTypes
from rudi_catalogos.models.base import RudiCatalogo

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class Motivo(RudiCatalogo):
    descripcion = None

    ambito = CharField(max_length=30)
    visibilidad = CharField(
        db_default=MotivoVisibilidadTypes.ADMIN,
        default=MotivoVisibilidadTypes.ADMIN,
        max_length=20,
    )

    require_descripcion = BooleanField(db_default=False, default=False)

    class Meta(RudiCatalogo.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *filter(
                lambda c: "descripcion" not in c.name,
                RudiCatalogo.Meta.constraints,
            ),
            CheckConstraint(
                condition=Q(ambito__in=MotivoAmbitoTypes.values),
                name="chk_%(class)s_ambito",
            ),
            CheckConstraint(
                condition=Q(visibilidad__in=MotivoVisibilidadTypes.values),
                name="chk_%(class)s_visibilidad",
            ),
            UniqueConstraint(
                Lower("codigo"),
                Lower("ambito"),
                name="unq_%(class)s_ambito",
            ),
        )
