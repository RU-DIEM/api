from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateTimeField,
    EmailField,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    TextField,
)
from django.db.models.functions import Now
from django.utils.timezone import now
from pgtrigger import ReadOnly

from api_core.models.base import ApiProtectedModel
from rudi_catalogos.models import PlantillaMensaje

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pgtrigger import Trigger

########################################################################################


# the queue is its own history: rows are rendered once, then only the delivery
# columns move, so there is no event table on top of it
class Notificacion(ApiProtectedModel):
    plantilla = ForeignKey(
        on_delete=RESTRICT,
        related_name="notificaciones",
        to=PlantillaMensaje,
    )

    cuenta = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="notificaciones",
        to=settings.AUTH_USER_MODEL,
    )

    destinatario = EmailField(max_length=254)
    asunto = CharField(max_length=200)
    cuerpo = TextField()

    programada_para = DateTimeField(db_default=Now(), default=now)

    intentos = PositiveSmallIntegerField(db_default=0, default=0)
    ultimo_error = TextField(db_default="", default="")

    enviada_at = DateTimeField(null=True)
    descartada_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint] = (
            CheckConstraint(
                condition=Q(cuerpo__len__gte=1),
                name="chk_%(class)s_cuerpo",
            ),
            CheckConstraint(
                condition=~Q(enviada_at__isnull=False, descartada_at__isnull=False),
                name="chk_%(class)s_desenlace_unico",
            ),
            CheckConstraint(
                condition=Q(descartada_at__isnull=True) | ~Q(ultimo_error=""),
                name="chk_%(class)s_descarte_error",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                condition=Q(enviada_at__isnull=True, descartada_at__isnull=True),
                fields=["programada_para"],
                name="idx_%(class)s_pendiente",
            ),
            BrinIndex(fields=["created_at"], name="brin_%(class)s_createdat"),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            ReadOnly(
                fields=["asunto", "cuerpo", "cuenta", "destinatario", "plantilla"],
                name="trg_readonly_mensaje",
            ),
        )
