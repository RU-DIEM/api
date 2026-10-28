from typing import TYPE_CHECKING, Final
from uuid import UUID

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.contrib.postgres.indexes import GistIndex
from django.db.models import (
    RESTRICT,
    Case,
    CharField,
    CheckConstraint,
    F,
    ForeignKey,
    GeneratedField,
    Index,
    Q,
    SmallIntegerField,
    UUIDField,
    UniqueConstraint,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from pgtrigger import ReadOnly

from api_core.models.base import (
    ApiSoftDeleteModel,
    remove_default_touch,
    touch_updatedat_trigger,
)
from api_utils.db import track_table
from rudi_actividades.models import Programa
from rudi_catalogos.models import RolParticipacion, TipoActividad, TipoReconocimiento
from rudi_estados.models import EstadoParticipacion

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import BaseConstraint
    from pgtrigger import Trigger

########################################################################################

CRITERIOS: Final[Sequence[str]] = (
    "tipo_actividad",
    "programa",
    "rol",
    "estado_participacion",
    "tipo_reconocimiento",
)

# `NULL` is never equal to `NULL` under `WITH =`, so two identical generic rules
# would never collide without mapping the missing criteria to a shared value
SIN_CRITERIO: Final[Value] = Value(UUID(int=0), output_field=UUIDField())

########################################################################################


@track_table()
class ReglaPuntuacion(ApiSoftDeleteModel):
    codigo = CharField(max_length=50)
    etiqueta = CharField(max_length=150)

    tipo_actividad = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="reglas",
        to=TipoActividad,
    )
    programa = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="reglas",
        to=Programa,
    )
    rol = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="reglas",
        to=RolParticipacion,
    )
    estado_participacion = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="reglas",
        to=EstadoParticipacion,
    )
    tipo_reconocimiento = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="reglas",
        to=TipoReconocimiento,
    )

    puntos = SmallIntegerField()

    especificidad = GeneratedField(
        db_persist=True,
        expression=sum(
            (
                Case(When(**{f"{c}__isnull": False}, then=Value(1)), default=Value(0))
                for c in CRITERIOS
            ),
            start=Value(0),
        ),
        output_field=SmallIntegerField(),
    )

    vigencia = DateRangeField()

    class Meta(ApiSoftDeleteModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[BaseConstraint] = (
            CheckConstraint(
                condition=Q(codigo__regex=r"^[a-z][a-z0-9_]*$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(puntos__gte=-500, puntos__lte=500),
                name="chk_%(class)s_puntos_rango",
            ),
            CheckConstraint(
                condition=~Q(vigencia__isempty=True),
                name="chk_%(class)s_vigencia",
            ),
            CheckConstraint(
                condition=Q(
                    *(Q(**{f"{c}__isnull": False}) for c in CRITERIOS),
                    _connector=Q.OR,
                ),
                name="chk_%(class)s_criterio_minimo",
            ),
            UniqueConstraint(fields=["codigo"], name="unq_%(class)s_codigo"),
            ExclusionConstraint(
                condition=Q(is_active=True),
                expressions=[
                    *(
                        (Coalesce(F(c), SIN_CRITERIO), RangeOperators.EQUAL)
                        for c in CRITERIOS
                    ),
                    ("vigencia", RangeOperators.OVERLAPS),
                ],
                name="excl_%(class)s_vigencia",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiSoftDeleteModel.Meta.indexes,
            Index(
                F("especificidad").desc(),
                condition=Q(is_active=True),
                name="idx_%(class)s_resolucion",
            ),
            GistIndex(fields=["vigencia"], name="gist_%(class)s_vigencia"),
        )

        triggers: Sequence[Trigger] = (
            *remove_default_touch(ApiSoftDeleteModel.Meta.triggers),
            touch_updatedat_trigger(exclude_generated=["especificidad"]),
            ReadOnly(fields=["codigo"], name="trg_readonly_codigo"),
        )
