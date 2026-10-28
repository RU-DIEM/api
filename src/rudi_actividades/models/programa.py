from typing import TYPE_CHECKING

from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    ForeignKey,
    Q,
    TextField,
    UniqueConstraint,
)
from django.db.models.functions import Upper
from pgtrigger import ReadOnly

from api_core.models.base import ApiSoftDeleteModel
from api_utils.db import ImmutableUnaccent, track_table
from rudi_catalogos.models import TipoActividad
from rudi_core.triggers import catalogo_activo_trigger

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pgtrigger import Trigger

########################################################################################


@track_table()
class Programa(ApiSoftDeleteModel):
    codigo = CharField(max_length=50)
    nombre = CharField(max_length=200)
    nombre_corto = CharField(db_default="", default="", max_length=60)
    descripcion = TextField(db_default="", default="")

    tipo_actividad = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="programas",
        to=TipoActividad,
    )

    is_institucional = BooleanField(db_default=True, default=True)

    class Meta(ApiSoftDeleteModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(codigo__regex=r"^[a-z][a-z0-9_]*$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(nombre__len__gte=2),
                name="chk_%(class)s_nombre",
            ),
            UniqueConstraint(fields=["codigo"], name="unq_%(class)s_codigo"),
            UniqueConstraint(
                Upper(ImmutableUnaccent("nombre")),
                name="unq_%(class)s_nombre",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiSoftDeleteModel.Meta.triggers,
            ReadOnly(fields=["codigo"], name="trg_readonly_codigo"),
            catalogo_activo_trigger(
                catalogos={"tipo_actividad_id": TipoActividad},
                entidad="programa",
            ),
        )
