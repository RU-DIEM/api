from typing import TYPE_CHECKING

from django.db.models import BooleanField, CheckConstraint, Q

from api_utils.db import track_table

from .base import RudiEstado
from .mixins import AllowInscripcionFieldMixin, RequireMotivoFieldMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################


@track_table()
class EstadoRudiUser(RudiEstado, RequireMotivoFieldMixin, AllowInscripcionFieldMixin):
    allow_ingreso = BooleanField(db_default=False, default=False)

    visible_reportes = BooleanField(db_default=True, default=True)

    class Meta(RudiEstado.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *RudiEstado.Meta.constraints,
            CheckConstraint(
                condition=(~Q(allow_inscripcion=True) | Q(allow_ingreso=True)),
                name="chk_%(class)s_inscripcion_ingreso",
            ),
        )
