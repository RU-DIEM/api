from typing import TYPE_CHECKING

from django.db.models import (
    CASCADE,
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Q,
    UniqueConstraint,
)
from django.db.models.functions import Lower

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@track_table()
class Equipo(ApiProtectedModel):
    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="equipos",
        to=Actividad,
    )

    nombre = CharField(max_length=120)
    codigo_union = CharField(max_length=10)

    creado_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="equipos_creados",
        to=RudiUser,
    )

    congelado_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(codigo_union__regex=r"^[A-Z0-9]{6,10}$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(nombre__len__gte=2),
                name="chk_%(class)s_nombre",
            ),
            UniqueConstraint(fields=["codigo_union"], name="unq_%(class)s_codigo"),
            UniqueConstraint(
                F("actividad"),
                Lower("nombre"),
                name="unq_%(class)s_nombre",
            ),
        )


########################################################################################


@track_table()
class EquipoMiembro(ApiProtectedModel):
    equipo = ForeignKey(
        on_delete=CASCADE,
        related_name="miembros",
        to=Equipo,
    )

    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="equipos",
        to=RudiUser,
    )

    is_lider = BooleanField(db_default=False, default=False)

    retirado_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(
                condition=Q(retirado_at__isnull=True),
                fields=["equipo", "user"],
                name="unq_%(class)s_vigente",
            ),
            UniqueConstraint(
                condition=Q(is_lider=True, retirado_at__isnull=True),
                fields=["equipo"],
                name="unq_%(class)s_lider",
            ),
        )
