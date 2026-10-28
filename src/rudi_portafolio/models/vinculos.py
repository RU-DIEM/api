from typing import TYPE_CHECKING

from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateField,
    F,
    ForeignKey,
    Q,
    URLField,
    UniqueConstraint,
)

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_portafolio.enums import IntegranteRolTypes, PropuestaActividadRolTypes

from .propuesta import Propuesta

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@track_table()
class PropuestaIntegrante(ApiProtectedModel):
    propuesta = ForeignKey(
        on_delete=RESTRICT,
        related_name="integrantes",
        to=Propuesta,
    )

    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="propuestas",
        to=RudiUser,
    )

    rol = CharField(max_length=30)

    desde = DateField()
    hasta = DateField(null=True)

    is_contacto = BooleanField(db_default=False, default=False)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(rol__in=IntegranteRolTypes.values),
                name="chk_%(class)s_rol",
            ),
            CheckConstraint(
                condition=Q(hasta__isnull=True) | Q(hasta__gte=F("desde")),
                name="chk_%(class)s_periodo",
            ),
            UniqueConstraint(
                condition=Q(hasta__isnull=True),
                fields=["propuesta", "user"],
                name="unq_%(class)s_vigente",
            ),
            UniqueConstraint(
                condition=Q(is_contacto=True, hasta__isnull=True),
                fields=["propuesta"],
                name="unq_%(class)s_contacto",
            ),
            UniqueConstraint(
                condition=Q(rol=IntegranteRolTypes.RESPONSABLE, hasta__isnull=True),
                fields=["propuesta"],
                name="unq_%(class)s_responsable",
            ),
        )


########################################################################################


@track_table()
class PropuestaActividad(ApiProtectedModel):
    propuesta = ForeignKey(
        on_delete=RESTRICT,
        related_name="actividades",
        to=Propuesta,
    )

    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="propuestas",
        to=Actividad,
    )

    rol = CharField(
        db_default=PropuestaActividadRolTypes.PARTICIPA,
        default=PropuestaActividadRolTypes.PARTICIPA,
        max_length=30,
    )

    resultado = CharField(db_default="", default="", max_length=200)
    enlace_evidencia = URLField(db_default="", default="", max_length=500)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(rol__in=PropuestaActividadRolTypes.values),
                name="chk_%(class)s_rol",
            ),
            UniqueConstraint(
                fields=["propuesta", "actividad"],
                name="unq_%(class)s_par",
            ),
            UniqueConstraint(
                condition=Q(rol=PropuestaActividadRolTypes.ORIGINA),
                fields=["propuesta"],
                name="unq_%(class)s_origen",
            ),
        )
