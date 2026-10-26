from typing import TYPE_CHECKING

from django.db.models import RESTRICT, CharField, F, ForeignKey, UniqueConstraint
from django.db.models.functions import Upper

from api_utils.db import ImmutableUnaccent
from rudi_core.models import RudiSoftDeleteModel

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class Departamento(RudiSoftDeleteModel):
    nombre = CharField(max_length=30)

    class Meta(RudiSoftDeleteModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(
                Upper(ImmutableUnaccent("nombre")),
                name="unq_%(class)s_nombre",
            ),
        )


class Municipio(RudiSoftDeleteModel):
    departamento = ForeignKey(
        on_delete=RESTRICT,
        related_name="municipios",
        to=Departamento,
    )

    nombre = CharField(max_length=30)

    class Meta(RudiSoftDeleteModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(
                F("departamento"),
                Upper(ImmutableUnaccent("nombre")),
                name="unq_%(class)s_nombre_departamento",
            ),
        )
