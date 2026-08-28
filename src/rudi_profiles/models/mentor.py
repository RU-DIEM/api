from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db.models import (
    CASCADE,
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateTimeField,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
)
from django.db.models.functions import Upper
from pgtrigger import Before, Insert, Trigger, Update

from api_utils.db import ImmutableUnaccent, track_table
from api_utils.strings import normalize_trigger
from rudi_catalogos.enums import NivelesAcademicos
from rudi_catalogos.models import AreaExperiencia, Municipio, TipoMentor
from rudi_core.models import RudiProtectedModel

from .base import RudiProfile

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

YEAR_TRIGGER: Final[str] = normalize_trigger("""
BEGIN
    IF NEW.year IS NOT NULL AND (
    NEW.year < 1960
        OR
        NEW.year > EXTRACT(year FROM CURRENT_DATE) + 1
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'year',
            MESSAGE = 'El año de la certificación está fuera del rango admitido.';
    END IF;
    RETURN NEW;
END;
""")

########################################################################################


@track_table()
class MentorProfile(RudiProfile):
    tipo_mentor = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="mentores",
        to=TipoMentor,
    )

    municipio = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="mentores",
        to=Municipio,
    )

    nivel_academico = CharField(db_default="", default="", max_length=20)

    direccion = TextField(db_default="", default="")
    descripcion_profesional = TextField(db_default="", default="")
    necesidades_formacion = TextField(db_default="", default="")

    confirmado_at = DateTimeField(null=True)
    confirmado_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="mentores_confirmados",
        to=settings.AUTH_USER_MODEL,
    )

    class Meta(RudiProfile.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(nivel_academico__in=(*NivelesAcademicos.values, "")),
                name="chk_%(class)s_nivel",
            ),
            CheckConstraint(
                condition=(
                    Q(confirmado_at__isnull=True, confirmado_por__isnull=True)
                    | Q(confirmado_at__isnull=False, confirmado_por__isnull=False)
                ),
                name="chk_%(class)s_confirmacion",
            ),
            CheckConstraint(
                condition=Q(descripcion_profesional__len__lte=4_000),
                name="chk_%(class)s_descripcion",
            ),
            CheckConstraint(
                condition=Q(necesidades_formacion__len__lte=2_000),
                name="chk_%(class)s_necesidades",
            ),
        )

        indexes: Sequence[Index] = (
            *RudiProfile.Meta.indexes,
            Index(
                condition=Q(confirmado_at__isnull=False),
                fields=["confirmado_at"],
                name="idx_%(class)s_confirmadoat",
            ),
            GinIndex(
                OpClass(
                    expression=Upper(ImmutableUnaccent("descripcion_profesional")),
                    name="gin_trgm_ops",
                ),
                condition=Q(descripcion_profesional__len__gt=0),
                name="gin_%(class)s_descripcionprofesional",
            ),
        )


########################################################################################


@track_table()
class MentorAreaExperiencia(RudiProtectedModel):
    profile = ForeignKey(
        on_delete=CASCADE,
        related_name="areas",
        to=MentorProfile,
    )

    area = ForeignKey(
        on_delete=RESTRICT,
        related_name="mentores",
        to=AreaExperiencia,
    )

    is_main = BooleanField(db_default=False, default=False)

    class Meta(RudiProtectedModel.Meta):
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(
                fields=["profile", "area"],
                name="unq_%(class)s_par",
            ),
            UniqueConstraint(
                condition=Q(is_main=True),
                fields=["profile"],
                name="unq_%(class)s_principal",
            ),
        )


########################################################################################


@track_table()
class MentorCertificacion(RudiProtectedModel):
    profile = ForeignKey(
        on_delete=CASCADE,
        related_name="certificaciones",
        to=MentorProfile,
    )

    nombre = CharField(max_length=200)
    institucion = CharField(db_default="", default="", max_length=200)

    year = PositiveSmallIntegerField(null=True)

    enlace_url = URLField(db_default="", default="", max_length=500)

    class Meta(RudiProtectedModel.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(nombre__len__gte=2),
                name="chk_%(class)s_nombre",
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiProtectedModel.Meta.triggers,
            Trigger(
                name="trg_mentorcertificacion_year",
                operation=(Insert | Update),
                when=Before,
                func=YEAR_TRIGGER,
            ),
        )
