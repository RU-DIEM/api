from typing import TYPE_CHECKING, Final

from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateField,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    SmallIntegerField,
    TextField,
    URLField,
    UniqueConstraint,
)
from django.db.models.functions import Lower
from pgtrigger import (
    Before,
    Insert,
    Trigger,
    UpdateOf,
    register as register_trigger,
)

from api_core.models.base import ApiProtectedModel
from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_actividades.enums import ModalidadTypes, ResponsableRolTypes
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo, TipoActividad
from rudi_core.triggers import catalogo_activo_trigger
from rudi_estados.models import EstadoActividad, TransicionEstadoActividad
from rudi_estados.triggers import estado_lifecycle_triggers, motivo_ambito_trigger

from .programa import Programa

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

ESTADO_COHERENTE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    publico boolean;
BEGIN
    SELECT public
    INTO publico
    FROM {EstadoActividad._meta.db_table}
    WHERE id = NEW.estado_id;
    IF publico AND NEW.publicada_at IS NULL THEN
        NEW.publicada_at = clock_timestamp();
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

########################################################################################


@track_table()
class Actividad(ApiProtectedModel):
    programa = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="actividades",
        to=Programa,
    )

    nombre = CharField(max_length=200)
    etiqueta_edicion = CharField(db_default="", default="", max_length=60)
    descripcion = TextField(db_default="", default="")

    tipo_actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="actividades",
        to=TipoActividad,
    )

    modalidad = CharField(
        db_default=ModalidadTypes.PRESENCIAL,
        default=ModalidadTypes.PRESENCIAL,
        max_length=20,
    )
    lugar = CharField(db_default="", default="", max_length=200)

    anio = PositiveSmallIntegerField()

    fecha_inicio = DateField()
    fecha_fin = DateField(null=True)

    inscripcion_abre_at = DateTimeField(null=True)
    inscripcion_cierra_at = DateTimeField(null=True)

    cupo = PositiveSmallIntegerField(null=True)
    inscritos_activos = PositiveSmallIntegerField(db_default=0, default=0)

    admite_lista_espera = BooleanField(db_default=True, default=True)
    admite_equipos = BooleanField(db_default=False, default=False)

    equipo_min = PositiveSmallIntegerField(null=True)
    equipo_max = PositiveSmallIntegerField(null=True)

    puntos_base = SmallIntegerField(null=True)

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="actividades",
        to=EstadoActividad,
    )

    publicada_at = DateTimeField(null=True)
    cancelada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="actividades",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    enlace_evidencia = URLField(db_default="", default="", max_length=500)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(modalidad__in=ModalidadTypes.values),
                name="chk_%(class)s_modalidad",
            ),
            CheckConstraint(
                condition=Q(anio__gte=2000, anio__lte=2100),
                name="chk_%(class)s_anio",
            ),
            CheckConstraint(
                condition=(
                    Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=F("fecha_inicio"))
                ),
                name="chk_%(class)s_fechas",
            ),
            CheckConstraint(
                condition=(
                    Q(inscripcion_abre_at__isnull=True)
                    | Q(inscripcion_cierra_at__isnull=True)
                    | Q(inscripcion_cierra_at__gt=F("inscripcion_abre_at"))
                ),
                name="chk_%(class)s_ventana",
            ),
            CheckConstraint(
                condition=Q(cupo__isnull=True) | Q(cupo__gt=0),
                name="chk_%(class)s_cupo_positivo",
            ),
            CheckConstraint(
                condition=(Q(cupo__isnull=True) | Q(inscritos_activos__lte=F("cupo"))),
                name="chk_%(class)s_cupo_coherente",
            ),
            CheckConstraint(
                condition=(
                    Q(admite_equipos=True)
                    | Q(equipo_min__isnull=True, equipo_max__isnull=True)
                ),
                name="chk_%(class)s_equipos_coherente",
            ),
            CheckConstraint(
                condition=(
                    Q(equipo_min__isnull=True)
                    | Q(equipo_max__isnull=True)
                    | Q(equipo_min__lte=F("equipo_max"))
                ),
                name="chk_%(class)s_equipo_rango",
            ),
            CheckConstraint(
                condition=(
                    Q(cancelada_at__isnull=True, motivo__isnull=True)
                    | Q(cancelada_at__isnull=False, motivo__isnull=False)
                ),
                name="chk_%(class)s_cancelacion",
            ),
            CheckConstraint(
                condition=(
                    Q(modalidad=ModalidadTypes.VIRTUAL, lugar="")
                    | ~Q(modalidad=ModalidadTypes.VIRTUAL)
                ),
                name="chk_%(class)s_lugar_virtual",
            ),
            UniqueConstraint(
                F("programa"),
                Lower("etiqueta_edicion"),
                condition=Q(programa__isnull=False),
                name="unq_%(class)s_programa_edicion",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                F("fecha_inicio").desc(),
                condition=Q(cancelada_at__isnull=True),
                name="idx_%(class)s_catalogo",
            ),
            Index(fields=["programa", "anio"], name="idx_%(class)s_programa_anio"),
            Index(
                condition=Q(cancelada_at__isnull=True),
                fields=["inscripcion_cierra_at"],
                name="idx_%(class)s_ventana_cierre",
            ),
            Index(fields=["anio", "tipo_actividad"], name="idx_%(class)s_anio_tipo"),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            *estado_lifecycle_triggers(
                entidad="actividad",
                model=EstadoActividad,
                transicion_model=TransicionEstadoActividad,
            ),
            catalogo_activo_trigger(
                catalogos={"programa_id": Programa, "tipo_actividad_id": TipoActividad},
                entidad="actividad",
            ),
            motivo_ambito_trigger(
                ambitos=(MotivoAmbitoTypes.CANCEL_ACTIVIDAD,),
                descripcion_field="motivo_descripcion",
                entidad="actividad",
                motivo_table=Motivo._meta.db_table,  # ruff: ignore[private-member-access]
            ),
            Trigger(
                func=ESTADO_COHERENTE_TRIGGER,
                name="trg_actividad_estado_coherente",
                operation=(Insert | UpdateOf("estado_id")),
                when=Before,
            ),
        )


########################################################################################


@track_table()
class ActividadResponsable(ApiProtectedModel):
    actividad = ForeignKey(
        on_delete=RESTRICT,
        related_name="responsables",
        to=Actividad,
    )

    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="responsabilidades",
        to=RudiUser,
    )

    rol = CharField(max_length=30)

    is_public = BooleanField(db_default=True, default=True)

    retirado_at = DateTimeField(null=True)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(rol__in=ResponsableRolTypes.values),
                name="chk_%(class)s_rol",
            ),
            UniqueConstraint(
                condition=Q(retirado_at__isnull=True),
                fields=["actividad", "user"],
                name="unq_%(class)s_vigente",
            ),
        )


########################################################################################

PUBLICACION_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    publico_nuevo boolean;
    publico_previo boolean;
BEGIN
    SELECT public INTO publico_nuevo
    FROM {EstadoActividad._meta.db_table}
    WHERE id = NEW.estado_id;
    SELECT public INTO publico_previo
    FROM {EstadoActividad._meta.db_table}
    WHERE id = OLD.estado_id;
    IF publico_nuevo AND NOT coalesce(publico_previo, false) AND NOT EXISTS (
        SELECT 1
        FROM {ActividadResponsable._meta.db_table}
        WHERE actividad_id = NEW.id
        AND retirado_at IS NULL
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'estado_id',
            MESSAGE = 'Una actividad no se publica sin al menos un responsable.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

register_trigger(
    Trigger(
        func=PUBLICACION_TRIGGER,
        name="trg_actividad_publicacion_completa",
        operation=UpdateOf("estado_id"),
        when=Before,
    ),
)(Actividad)
