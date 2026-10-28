from typing import TYPE_CHECKING

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateField,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
)

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_catalogos.models import Motivo, RolParticipacion, TipoReconocimiento
from rudi_estados.models import EstadoParticipacion
from rudi_participacion.enums import ParticipacionOrigenTypes

from .equipo import Equipo
from .inscripcion import Inscripcion

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@track_table()
class Participacion(ApiProtectedModel):
    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=RudiUser,
    )

    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Actividad,
    )

    inscripcion = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Inscripcion,
    )

    anio = PositiveSmallIntegerField()

    rol = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=RolParticipacion,
    )

    equipo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Equipo,
    )

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=EstadoParticipacion,
    )

    origen = CharField(
        db_default=ParticipacionOrigenTypes.ADMIN,
        default=ParticipacionOrigenTypes.ADMIN,
        max_length=20,
    )

    fecha_inicio = DateField(null=True)
    fecha_fin = DateField(null=True)

    validada_at = DateTimeField(null=True)
    validada_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones_validadas",
        to=settings.AUTH_USER_MODEL,
    )

    enlace_evidencia = URLField(db_default="", default="", max_length=500)
    observaciones = TextField(db_default="", default="")

    anulada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(origen__in=ParticipacionOrigenTypes.values),
                name="chk_%(class)s_origen",
            ),
            CheckConstraint(
                condition=Q(anio__gte=2000, anio__lte=2100),
                name="chk_%(class)s_anio",
            ),
            CheckConstraint(
                condition=(
                    Q(validada_at__isnull=True, validada_por__isnull=True)
                    | Q(validada_at__isnull=False, validada_por__isnull=False)
                ),
                name="chk_%(class)s_validacion_coherente",
            ),
            CheckConstraint(
                condition=(
                    Q(anulada_at__isnull=True, motivo__isnull=True)
                    | Q(anulada_at__isnull=False, motivo__isnull=False)
                ),
                name="chk_%(class)s_anulacion",
            ),
            CheckConstraint(
                condition=Q(anulada_at__isnull=True) | Q(validada_at__isnull=False),
                name="chk_%(class)s_anulacion_validada",
            ),
            CheckConstraint(
                condition=(
                    Q(fecha_fin__isnull=True)
                    | Q(fecha_inicio__isnull=True)
                    | Q(fecha_fin__gte=F("fecha_inicio"))
                ),
                name="chk_%(class)s_fechas",
            ),
            UniqueConstraint(
                condition=Q(anulada_at__isnull=True),
                fields=["user", "actividad"],
                name="unq_%(class)s_persona_activa",
            ),
            UniqueConstraint(
                condition=Q(inscripcion__isnull=False, anulada_at__isnull=True),
                fields=["inscripcion"],
                name="unq_%(class)s_inscripcion",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(F("user"), F("anio").desc(), name="idx_%(class)s_user_anio"),
            Index(
                fields=["actividad", "estado"],
                name="idx_%(class)s_actividad_estado",
            ),
            Index(
                condition=Q(validada_at__isnull=False, anulada_at__isnull=True),
                fields=["anio", "actividad"],
                name="idx_%(class)s_efectiva_anio",
            ),
            Index(
                condition=Q(validada_at__isnull=True, anulada_at__isnull=True),
                fields=["actividad"],
                name="idx_%(class)s_sin_validar",
            ),
        )


########################################################################################


@track_table()
class Reconocimiento(ApiProtectedModel):
    participacion = ForeignKey(
        on_delete=RESTRICT,
        related_name="reconocimientos",
        to=Participacion,
    )

    tipo = ForeignKey(
        on_delete=RESTRICT,
        related_name="reconocimientos",
        to=TipoReconocimiento,
    )

    descripcion = CharField(max_length=300)
    posicion = PositiveSmallIntegerField(null=True)
    otorgado_en = DateField(null=True)

    enlace_evidencia = URLField(db_default="", default="", max_length=500)

    anulado_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint] = (
            CheckConstraint(
                condition=Q(posicion__isnull=True) | Q(posicion__gt=0),
                name="chk_%(class)s_posicion",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                F("tipo"),
                F("otorgado_en").desc(),
                condition=Q(anulado_at__isnull=True),
                name="idx_%(class)s_tipo",
            ),
        )
