from typing import TYPE_CHECKING

from django.db.models import BooleanField, CheckConstraint, Q

from api_utils.db import track_table

from .base import RudiEstado, build_concrete_transicion

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################


@track_table()
class EstadoParticipacion(RudiEstado):
    efectiva = BooleanField(db_default=False, default=False)

    allow_constancia = BooleanField(db_default=False, default=False)
    allow_puntos = BooleanField(db_default=False, default=False)

    class Meta(RudiEstado.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiEstado.Meta.constraints,
            CheckConstraint(
                condition=(~Q(allow_puntos=True) | Q(efectiva=True)),
                name="chk_%(class)s_puntos_efectiva",
            ),
            CheckConstraint(
                condition=(~Q(allow_constancia=True) | Q(efectiva=True)),
                name="chk_%(class)s_constancia_efectiva",
            ),
        )


########################################################################################


@track_table()
class TransicionEstadoParticipacion(
    build_concrete_transicion(EstadoParticipacion),  # ty: ignore[unsupported-base]
):
    pass
