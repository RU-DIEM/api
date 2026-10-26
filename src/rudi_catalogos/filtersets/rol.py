from typing import TYPE_CHECKING

from rudi_catalogos.models import RolParticipacion

from .base import RudiCatalogoFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class RolParticipacionFilterSet(RudiCatalogoFilterSet):
    class Meta(RudiCatalogoFilterSet.Meta):  # ty: ignore[invalid-attribute-override]
        fields: Sequence[str] = ()
        model: type[Model] = RolParticipacion
