from typing import TYPE_CHECKING

from django.db.models import BooleanField, CheckConstraint, Q

from api_utils.db import track_table

from .base import RudiEstado, build_concrete_transicion
from .mixins import AllowInscripcionFieldMixin, PublicFieldMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################


@track_table()
class EstadoActividad(RudiEstado, PublicFieldMixin, AllowInscripcionFieldMixin):
    allow_validacion = BooleanField(db_default=False, default=False)

    class Meta(RudiEstado.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiEstado.Meta.constraints,
            CheckConstraint(
                condition=(~Q(allow_inscripcion=True) | Q(public=True)),
                name="chk_%(class)s_inscripcion_public",
            ),
            CheckConstraint(
                condition=(~Q(allow_validacion=True) | Q(public=True)),
                name="chk_%(class)s_validacion_public",
            ),
        )


########################################################################################


@track_table()
class TransicionEstadoActividad(
    build_concrete_transicion(EstadoActividad),  # ty: ignore[unsupported-base]
):
    pass
