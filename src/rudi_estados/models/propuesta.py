from typing import TYPE_CHECKING

from django.db.models import BooleanField, CheckConstraint, Q

from api_utils.db import track_table

from .base import RudiEstado, build_concrete_transicion
from .mixins import VigenteFieldMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################


@track_table()
class EstadoPropuesta(RudiEstado, VigenteFieldMixin):
    allow_portafolio = BooleanField(db_default=False, default=False)

    class Meta(RudiEstado.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiEstado.Meta.constraints,
            CheckConstraint(
                condition=(~Q(vigente=True) | Q(allow_portafolio=True)),
                name="chk_%(class)s_vigente_allowportafolio",
            ),
        )


########################################################################################


@track_table()
class TransicionEstadoPropuesta(
    build_concrete_transicion(EstadoPropuesta),  # ty: ignore[unsupported-base]
):
    pass
