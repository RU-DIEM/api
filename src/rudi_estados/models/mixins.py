from typing import TYPE_CHECKING

from django.db.models import (
    BooleanField,
    CharField,
    CheckConstraint,
    Model,
    Q,
    UniqueConstraint,
)

from rudi_estados.enums import InputSourceTypes

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class AllowInscripcionFieldMixin(Model):
    allow_inscripcion = BooleanField(db_default=False, default=False)

    class Meta:
        abstract: bool = True


########################################################################################


class PublicFieldMixin(Model):
    public = BooleanField(db_default=False, default=False)

    class Meta:
        abstract: bool = True


########################################################################################


class RequireMotivoFieldMixin(Model):
    require_motivo = BooleanField(db_default=False, default=False)

    class Meta:
        abstract: bool = True


########################################################################################


class SourceFieldMixin(Model):
    source = CharField(db_default="", default="", max_length=30)

    class Meta:
        abstract: bool = True

        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=(
                    Q(initial=True, source__regex=r"^[a-z][a-z0-9_]*$")
                    | Q(initial=False, source="")
                ),
                name="chk_%(class)s_source_initial",
            ),
            CheckConstraint(
                condition=Q(source__in=(*InputSourceTypes.values, "")),
                name="chk_%(class)s_source",
            ),
            UniqueConstraint(
                condition=(~Q(source="")),
                fields=["source"],
                name="unq_%(class)s_source",
            ),
        )


########################################################################################


class VigenteFieldMixin(Model):
    vigente = BooleanField(db_default=False, default=False)

    class Meta:
        abstract: bool = True
