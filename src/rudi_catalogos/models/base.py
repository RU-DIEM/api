from typing import TYPE_CHECKING

from django.db.models import CharField, CheckConstraint, Q, TextField, UniqueConstraint
from pgtrigger import ReadOnly, Trigger

from api_core.models.base import ApiSoftDeleteModel

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class RudiCatalogo(ApiSoftDeleteModel):
    codigo = CharField(max_length=50)
    etiqueta = CharField(db_default="", default="", max_length=100)
    descripcion = TextField(db_default="", default="")

    class Meta(ApiSoftDeleteModel.Meta):  # ty: ignore[invalid-attribute-override]
        abstract: bool = True

        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(codigo__regex=r"^[a-z][a-z0-9_]*$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(descripcion__len__lte=300),
                name="chk_%(class)s_descripcion",
            ),
            UniqueConstraint(fields=["codigo"], name="unq_%(class)s_codigo"),
        )

        triggers: Sequence[Trigger] = (
            *ApiSoftDeleteModel.Meta.triggers,
            ReadOnly(fields=["codigo"], name="trg_readonly_codigo"),
        )


########################################################################################


class AreaExperiencia(RudiCatalogo):
    pass


class RolParticipacion(RudiCatalogo):
    pass


class TipoActividad(RudiCatalogo):
    pass


class TipoMentor(RudiCatalogo):
    pass


class TipoReconocimiento(RudiCatalogo):
    pass
