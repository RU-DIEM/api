from typing import TYPE_CHECKING

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DecimalField,
    F,
    ForeignKey,
    Index,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    Q,
    TextField,
    UniqueConstraint,
)

from api_core.models.base import ApiAppendOnlyModel
from rudi_analitica.enums import IndicadorUnidadTypes

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


class IndicadorPeriodo(ApiAppendOnlyModel):
    indicador = CharField(max_length=60)
    anio = PositiveSmallIntegerField()

    dimension = CharField(db_default="", default="", max_length=40)
    dimension_valor = CharField(db_default="", default="", max_length=150)

    valor = DecimalField(decimal_places=2, max_digits=12)
    unidad = CharField(
        db_default=IndicadorUnidadTypes.PERSONAS,
        default=IndicadorUnidadTypes.PERSONAS,
        max_length=20,
    )

    cerrado_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="indicadores_cerrados",
        to=settings.AUTH_USER_MODEL,
    )

    metodo = TextField(db_default="", default="")
    filas_origen = PositiveIntegerField(db_default=0, default=0)

    class Meta(ApiAppendOnlyModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(indicador__regex=r"^[a-z][a-z0-9_]*$"),
                name="chk_%(class)s_indicador_format",
            ),
            CheckConstraint(
                condition=Q(anio__gte=2000, anio__lte=2100),
                name="chk_%(class)s_anio",
            ),
            CheckConstraint(
                condition=Q(unidad__in=IndicadorUnidadTypes.values),
                name="chk_%(class)s_unidad",
            ),
            CheckConstraint(
                condition=Q(valor__gte=0),
                name="chk_%(class)s_valor",
            ),
            CheckConstraint(
                condition=(
                    Q(dimension="", dimension_valor="")
                    | (~Q(dimension="") & ~Q(dimension_valor=""))
                ),
                name="chk_%(class)s_dimension_coherente",
            ),
            UniqueConstraint(
                fields=["indicador", "anio", "dimension", "dimension_valor"],
                name="unq_%(class)s_corte",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiAppendOnlyModel.Meta.indexes,
            Index(F("anio").desc(), F("indicador"), name="idx_%(class)s_anio"),
            Index(F("indicador"), F("anio").desc(), name="idx_%(class)s_indicador"),
        )
