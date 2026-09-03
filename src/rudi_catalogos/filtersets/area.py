from typing import TYPE_CHECKING

from rudi_catalogos.models import AreaExperiencia

from .base import RudiCatalogoFilterSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import Model

########################################################################################


class AreaExperienciaFilterSet(RudiCatalogoFilterSet):
    class Meta(RudiCatalogoFilterSet.Meta):
        fields: Sequence[str] = ()
        model: type[Model] = AreaExperiencia
