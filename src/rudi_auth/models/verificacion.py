from typing import TYPE_CHECKING

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateTimeField,
    EmailField,
    F,
    ForeignKey,
    Index,
    Q,
    UniqueConstraint,
)
from django.db.models.functions import Lower

from api_utils.db import track_table
from rudi_auth.enums import VerificacionPropositoTypes
from rudi_core.models import RudiProtectedModel

from .user import RudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@track_table()
class CodigoVerificacion(RudiProtectedModel):
    user = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="codigos",
        to=RudiUser,
    )

    email = EmailField()
    proposito = CharField(max_length=30)
    token_hash = CharField(max_length=128)

    expira_at = DateTimeField()
    consumido_at = DateTimeField(null=True)
    invalidado_at = DateTimeField(null=True)

    emitido_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="codigos_emitidos",
        to=settings.AUTH_USER_MODEL,
    )

    class Meta(RudiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(proposito__in=VerificacionPropositoTypes.values),
                name="chk_%(class)s_proposito",
            ),
            CheckConstraint(
                condition=Q(expira_at__gt=F("created_at")),
                name="chk_%(class)s_vigencia",
            ),
            CheckConstraint(
                condition=(
                    Q(consumido_at__isnull=True) | Q(invalidado_at__isnull=True)
                ),
                name="chk_%(class)s_desenlace_unico",
            ),
            CheckConstraint(
                condition=(
                    ~Q(proposito=VerificacionPropositoTypes.INVITE)
                    | Q(emitido_por__isnull=False)
                ),
                name="chk_%(class)s_invitacion_actor",
            ),
            UniqueConstraint(fields=["token_hash"], name="unq_%(class)s_token"),
            UniqueConstraint(
                F("proposito"),
                Lower("email"),
                condition=Q(consumido_at__isnull=True, invalidado_at__isnull=True),
                name="unq_%(class)s_vivo",
            ),
        )

        indexes: Sequence[Index] = (
            *RudiProtectedModel.Meta.indexes,
            Index(
                condition=Q(consumido_at__isnull=True, invalidado_at__isnull=True),
                fields=["expira_at"],
                name="idx_%(class)s_expiracion",
            ),
        )
