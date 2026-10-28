from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    ForeignKey,
    Index,
    Q,
    TextField,
)

from api_core.models.base import ApiAppendOnlyModel
from rudi_auth.enums import AccesoDatoTypes

from .user import RudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class AccesoDatoPersonal(ApiAppendOnlyModel):
    tipo = CharField(max_length=20)

    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="accesos",
        to=RudiUser,
    )

    accedido_por = ForeignKey(
        on_delete=RESTRICT,
        related_name="accesos_datos",
        to=settings.AUTH_USER_MODEL,
    )

    recurso = CharField(max_length=200)
    detalle = TextField(db_default="", default="")

    class Meta(ApiAppendOnlyModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint] = (
            CheckConstraint(
                condition=Q(tipo__in=AccesoDatoTypes.values),
                name="chk_%(class)s_tipo",
            ),
        )

        indexes: Sequence[Index] = (
            Index(fields=["user", "created_at"], name="idx_%(class)s_user"),
            BrinIndex(fields=["created_at"], name="brin_%(class)s_createdat"),
        )
