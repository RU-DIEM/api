from typing import TYPE_CHECKING

from django.db.models import CheckConstraint, Q

from api_utils.db import track_table

from .base import RudiEstado
from .mixins import PublicFieldMixin, RequireMotivoFieldMixin, VigenteFieldMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################


@track_table()
class EstadoAsignacionMentor(
    RudiEstado,
    RequireMotivoFieldMixin,
    PublicFieldMixin,
    VigenteFieldMixin,
):
    class Meta(RudiEstado.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiEstado.Meta.constraints,
            CheckConstraint(
                condition=(~Q(vigente=True) | Q(public=True)),
                name="chk_%(class)s_vigente_public",
            ),
        )
