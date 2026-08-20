from typing import TYPE_CHECKING

from django.db.models import RESTRICT, CharField, F, ForeignKey, UniqueConstraint
from django.db.models.functions import Lower

from rudi_core.models import RudiAppendOnlyModel

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class Departamento(RudiAppendOnlyModel):
    nombre = CharField(max_length=30)

    class Meta(RudiAppendOnlyModel.Meta):
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(Lower("nombre"), name="unq_%(class)s_nombre"),
        )


class Municipio(RudiAppendOnlyModel):
    departamento = ForeignKey(
        on_delete=RESTRICT,
        related_name="municipios",
        to=Departamento,
    )

    nombre = CharField(max_length=30)

    class Meta(RudiAppendOnlyModel.Meta):
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(Lower("nombre"), name="unq_%(class)s_nombre"),
            UniqueConstraint(
                F("departamento"),
                Lower("nombre"),
                name="unq_%(class)s_nombre_departamento",
            ),
        )
