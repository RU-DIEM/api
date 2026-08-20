from typing import TYPE_CHECKING

from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    F,
    ForeignKey,
    Index,
    Q,
    TextField,
    UniqueConstraint,
    Value,
)
from pgtrigger import ReadOnly

from rudi_core.models import RudiSoftDeleteModel
from rudi_estados.enums import ActorTypes

from .mixins import RequireMotivoFieldMixin, SourceFieldMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pgtrigger import Trigger

########################################################################################


class RudiEstado(RudiSoftDeleteModel):
    initial = BooleanField(db_default=False, default=False)
    terminal = BooleanField(db_default=False, default=False)

    codigo = CharField(max_length=50)
    etiqueta = CharField(max_length=50)
    descripcion = TextField(db_default="", default="")

    class Meta(RudiSoftDeleteModel.Meta):
        abstract: bool = True

        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(codigo__regex=r"^[a-z][a-z0-9_]*$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=(~Q(initial=True) | Q(is_active=True)),
                name="chk_%(class)s_initial_isactive",
            ),
            CheckConstraint(
                condition=(~Q(initial=True, terminal=True)),
                name="chk_%(class)s_initial_terminal",
            ),
            UniqueConstraint(fields=["codigo"], name="unq_%(class)s_codigo"),
            UniqueConstraint(
                Value(value=True),
                condition=Q(initial=True),
                name="unq_%(class)s_initial",
            ),
        )

        indexes: Sequence[Index] = (
            *RudiSoftDeleteModel.Meta.indexes,
            Index(
                condition=Q(is_active=True),
                fields=["codigo"],
                name="idx_%(class)s_codigo",
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiSoftDeleteModel.Meta.triggers,
            ReadOnly(fields=["codigo"], name="trg_readonly_codigo"),
        )


########################################################################################


class RudiSourceAwareEstado(RudiEstado, SourceFieldMixin):
    class Meta(RudiEstado.Meta):
        abstract: bool = True

        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *filter(lambda c: "initial" not in c.name, RudiEstado.Meta.constraints),
            *SourceFieldMixin.Meta.constraints,
        )


########################################################################################


class RudiTransicion(RudiSoftDeleteModel, RequireMotivoFieldMixin):
    require_descripcion = BooleanField(db_default=False, default=False)

    actor = CharField(max_length=20)

    class Meta(RudiSoftDeleteModel.Meta):
        abstract: bool = True

        constraints: Sequence[CheckConstraint] = (
            CheckConstraint(
                condition=Q(actor__in=ActorTypes.values),
                name="chk_%(class)s_actor",
            ),
            CheckConstraint(
                condition=(~Q(require_descripcion=True) | Q(require_motivo=True)),
                name="chk_%(class)s_descripcion_motivo_mutex",
            ),
        )


########################################################################################


def build_concrete_transicion(ref: type[RudiEstado]) -> type[RudiTransicion]:
    class RudiConcreteTransicion(RudiTransicion):
        from_estado = ForeignKey(on_delete=RESTRICT, related_name="+", to=ref)
        to_estado = ForeignKey(on_delete=RESTRICT, related_name="+", to=ref)

        class Meta(RudiTransicion.Meta):
            abstract: bool = True

            constraints: Sequence[CheckConstraint] = (
                *RudiTransicion.Meta.constraints,
                CheckConstraint(
                    condition=(~Q(from_estado=F(name="to_estado"))),
                    name="chk_%(class)s_noreflex",
                ),
            )

    return RudiConcreteTransicion
