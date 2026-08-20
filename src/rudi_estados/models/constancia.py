from typing import TYPE_CHECKING

from django.db.models import BooleanField, CheckConstraint, Q

from api_utils.db import track_table

from .base import RudiEstado
from .mixins import RequireMotivoFieldMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################


@track_table()
class EstadoConstancia(RudiEstado, RequireMotivoFieldMixin):
    valid = BooleanField(db_default=False, default=False)

    class Meta(RudiEstado.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiEstado.Meta.constraints,
            CheckConstraint(
                condition=(~Q(valid=True, terminal=True)),
                name="chk_%(class)s_valida_terminal_mutex",
            ),
        )
