from typing import TYPE_CHECKING

from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CharField,
    CheckConstraint,
    DateField,
    F,
    PositiveSmallIntegerField,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
    Value,
)
from pgtrigger import ReadOnly

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pgtrigger import Trigger

########################################################################################


@track_table()
class PlantillaConstancia(ApiProtectedModel):
    codigo = CharField(max_length=50)
    etiqueta = CharField(max_length=120)

    version = PositiveSmallIntegerField(db_default=1, default=1)

    cuerpo = TextField()
    campos_requeridos = ArrayField(
        base_field=CharField(max_length=50),
        db_default=Value(value=[], output_field=ArrayField(CharField(max_length=50))),
        default=list,
    )

    firma_nombre = CharField(db_default="", default="", max_length=150)
    firma_cargo = CharField(db_default="", default="", max_length=150)
    firma_imagen_url = URLField(db_default="", default="", max_length=500)

    vigente_desde = DateField()
    vigente_hasta = DateField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(codigo__regex=r"^[a-z][a-z0-9_]*$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(cuerpo__len__gte=1, cuerpo__len__lte=20_000),
                name="chk_%(class)s_cuerpo",
            ),
            CheckConstraint(
                condition=(
                    Q(vigente_hasta__isnull=True)
                    | Q(vigente_hasta__gt=F("vigente_desde"))
                ),
                name="chk_%(class)s_vigencia",
            ),
            UniqueConstraint(
                fields=["codigo", "version"],
                name="unq_%(class)s_codigo_version",
            ),
            UniqueConstraint(
                condition=Q(vigente_hasta__isnull=True),
                fields=["codigo"],
                name="unq_%(class)s_vigente",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            ReadOnly(fields=["codigo", "version"], name="trg_readonly_codigo_version"),
        )
