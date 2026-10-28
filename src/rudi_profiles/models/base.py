from typing import TYPE_CHECKING

from django.db.models import RESTRICT, DateTimeField, Index, OneToOneField
from django.db.models.functions import Now
from django.utils.timezone import now

from api_core.models.base import ApiProtectedModel
from rudi_auth.models import RudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class RudiProfile(ApiProtectedModel):
    user = OneToOneField(
        on_delete=RESTRICT,
        related_name="%(class)s",
        to=RudiUser,
    )

    verificado_at = DateTimeField(db_default=Now(), default=now)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        abstract: bool = True

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(fields=["verificado_at"], name="idx_%(class)s_verificadoat"),
        )
