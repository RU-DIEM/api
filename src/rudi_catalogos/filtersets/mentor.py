from typing import TYPE_CHECKING

from rudi_catalogos.models import TipoMentor

from .base import RudiCatalogoFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class TipoMentorFilterSet(RudiCatalogoFilterSet):
    class Meta(RudiCatalogoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = TipoMentor
