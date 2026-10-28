from typing import TYPE_CHECKING

from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateField,
    DateTimeField,
    F,
    ForeignKey,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
    Value,
)

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from rudi_auth.enums import ConsentimientoCanalTypes
from rudi_estados.models import EstadoConsentimiento
from rudi_estados.triggers import estado_lifecycle_triggers

from .user import RudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pgtrigger import Trigger

########################################################################################


@track_table()
class PoliticaPrivacidad(ApiProtectedModel):
    version = CharField(max_length=20)
    titulo = CharField(max_length=200)
    texto = TextField()

    vigente_desde = DateField()
    vigente_hasta = DateField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(version__regex=r"^\d+\.\d+$"),
                name="chk_%(class)s_version_format",
            ),
            CheckConstraint(
                condition=(
                    Q(vigente_hasta__isnull=True)
                    | Q(vigente_hasta__gt=F("vigente_desde"))
                ),
                name="chk_%(class)s_vigencia",
            ),
            CheckConstraint(
                condition=Q(texto__len__gte=1),
                name="chk_%(class)s_texto",
            ),
            UniqueConstraint(fields=["version"], name="unq_%(class)s_version"),
            UniqueConstraint(
                Value(value=True),
                condition=Q(vigente_hasta__isnull=True),
                name="unq_%(class)s_vigente",
            ),
        )


########################################################################################


@track_table()
class ConsentimientoDatos(ApiProtectedModel):
    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="consentimientos",
        to=RudiUser,
    )

    politica = ForeignKey(
        on_delete=RESTRICT,
        related_name="consentimientos",
        to=PoliticaPrivacidad,
    )

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="consentimientos",
        to=EstadoConsentimiento,
    )

    canal = CharField(max_length=20)

    otorgado_at = DateTimeField(null=True)
    retirado_at = DateTimeField(null=True)

    evidencia_url = URLField(db_default="", default="", max_length=500)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(canal__in=ConsentimientoCanalTypes.values),
                name="chk_%(class)s_canal",
            ),
            CheckConstraint(
                condition=(Q(retirado_at__isnull=True) | Q(otorgado_at__isnull=False)),
                name="chk_%(class)s_retiro",
            ),
            UniqueConstraint(fields=["user"], name="unq_%(class)s_user"),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            *estado_lifecycle_triggers(
                entidad="consentimientodatos",
                model=EstadoConsentimiento,
            ),
        )
