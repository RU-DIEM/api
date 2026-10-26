from typing import TYPE_CHECKING

from django.db.models import RESTRICT, DateTimeField, Index, OneToOneField
from django.db.models.functions import Now
from django.utils.timezone import now

from rudi_auth.models import RudiUser
from rudi_core.models import RudiProtectedModel

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class RudiProfile(RudiProtectedModel):
    user = OneToOneField(
        on_delete=RESTRICT,
        related_name="%(class)s",
        to=RudiUser,
    )

    verificado_at = DateTimeField(db_default=Now(), default=now)

    class Meta(RudiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        abstract: bool = True

        indexes: Sequence[Index] = (
            *RudiProtectedModel.Meta.indexes,
            Index(fields=["verificado_at"], name="idx_%(class)s_verificadoat"),
        )
