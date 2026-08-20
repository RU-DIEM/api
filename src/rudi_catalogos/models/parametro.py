from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    ForeignKey,
    JSONField,
    Q,
    UniqueConstraint,
)
from django.db.models.expressions import RawSQL
from django.db.models.functions import JSONObject

from rudi_catalogos.enums import ParametroGrupoTypes, ParametroTypes

from .base import RudiCatalogo

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class Parametro(RudiCatalogo):
    etiqueta = None

    grupo = CharField(max_length=20)
    tipo = CharField(max_length=10)
    valor = JSONField()
    restricciones = JSONField(db_default=JSONObject(), default=dict)

    updated_by = ForeignKey(
        on_delete=RESTRICT,
        related_name="parametros",
        to=get_user_model(),
    )

    class Meta(RudiCatalogo.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *filter(lambda c: "etiqueta" not in c.name, RudiCatalogo.Meta.constraints),
            CheckConstraint(
                condition=Q(grupo__in=ParametroGrupoTypes.values),
                name="chk_%(class)s_grupo",
            ),
            CheckConstraint(
                condition=Q(tipo__in=ParametroTypes.values),
                name="chk_%(class)s_tipo",
            ),
            CheckConstraint(
                condition=RawSQL(
                    params=(),
                    output_field=BooleanField(),
                    sql="jsonb_typeof(restricciones) = 'object'",
                ),
                name="chk_%(class)s_restricciones",
            ),
        )
