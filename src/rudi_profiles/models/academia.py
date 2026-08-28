from typing import TYPE_CHECKING

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
    UniqueConstraint,
)
from django.db.models.functions import Upper

from api_utils.db import ImmutableUnaccent, track_table
from rudi_catalogos.models.base import RudiCatalogo
from rudi_core.models import RudiSoftDeleteModel
from rudi_profiles.enums import InstitucionTypes

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class Facultad(RudiCatalogo):
    abreviacion = CharField(db_default="", default="", max_length=30)


########################################################################################


class Carrera(RudiCatalogo):
    facultad = ForeignKey(
        on_delete=RESTRICT,
        related_name="carreras",
        to=Facultad,
    )

    duracion = PositiveSmallIntegerField(null=True)

    class Meta(RudiCatalogo.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiCatalogo.Meta.constraints,
            CheckConstraint(
                condition=(
                    Q(duracion__isnull=True) | Q(duracion__gte=1, duracion__lte=8)
                ),
                name="chk_%(class)s_duracion",
            ),
            UniqueConstraint(
                F("facultad"),
                Upper(ImmutableUnaccent("etiqueta")),
                name="unq_%(class)s_nombre_facultad",
            ),
        )


########################################################################################


@track_table()
class Institucion(RudiSoftDeleteModel):
    nombre = CharField(max_length=200)
    tipo = CharField(max_length=30)

    normalizada_at = DateTimeField(null=True)

    class Meta(RudiSoftDeleteModel.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(tipo__in=InstitucionTypes.values),
                name="chk_%(class)s_tipo",
            ),
            CheckConstraint(
                condition=Q(nombre__len__gte=2),
                name="chk_%(class)s_nombre",
            ),
            UniqueConstraint(
                Upper(ImmutableUnaccent("nombre")),
                name="unq_%(class)s_nombre",
            ),
        )

        indexes: Sequence[Index] = (
            *RudiSoftDeleteModel.Meta.indexes,
            Index(
                condition=Q(normalizada_at__isnull=True),
                fields=["created_at"],
                name="idx_%(class)s_pendiente",
            ),
        )
