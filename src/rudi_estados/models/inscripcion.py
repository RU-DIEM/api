from typing import TYPE_CHECKING

from django.db.models import BooleanField, CheckConstraint, Q

from api_utils.db import track_table

from .base import RudiSourceAwareEstado, build_concrete_transicion

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################


@track_table()
class EstadoInscripcion(RudiSourceAwareEstado):
    consume_cupo = BooleanField(db_default=False, default=False)

    allow_participacion = BooleanField(db_default=False, default=False)

    class Meta(RudiSourceAwareEstado.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiSourceAwareEstado.Meta.constraints,
            CheckConstraint(
                condition=(~Q(consume_cupo=True, terminal=True)),
                name="chk_%(class)s_cupo_terminal_mutex",
            ),
            CheckConstraint(
                condition=(~Q(allow_participacion=True) | Q(consume_cupo=True)),
                name="chk_%(class)s_participacion_cupo",
            ),
        )


########################################################################################


@track_table()
class TransicionEstadoInscripcion(
    build_concrete_transicion(EstadoInscripcion),  # ty: ignore[unsupported-base]
):
    pass
