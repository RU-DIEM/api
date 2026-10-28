from typing import TYPE_CHECKING, Final

from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    PositiveSmallIntegerField,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
    Value,
)
from django.db.models.functions import Concat, Upper
from pgtrigger import Before, Func, Insert, ReadOnly, Trigger, Update, UpdateOf

from api_core.models.base import ApiProtectedModel
from api_utils.db import ImmutableUnaccent, track_table
from api_utils.strings import normalize_trigger
from rudi_actividades.models import Actividad
from rudi_catalogos.enums import (
    MRL,
    ODS,
    TRL,
    AmbitosAplicacion,
    EtapasDesarrollo,
    MotivoAmbitoTypes,
    NivelesFormalizacion,
    RudiTaxonomia,
    SectoresAplicacion,
    TiposInnovacion,
    VerticalesInnovacion,
)
from rudi_catalogos.models import Motivo
from rudi_estados.models import EstadoPropuesta, TransicionEstadoPropuesta
from rudi_estados.triggers import estado_lifecycle_triggers, motivo_ambito_trigger

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

CLASIFICACIONES: Final[dict[str, type[RudiTaxonomia]]] = {
    "nivel_formalizacion": NivelesFormalizacion,
    "etapa_desarrollo": EtapasDesarrollo,
    "ambito_aplicacion": AmbitosAplicacion,
    "sector_aplicacion": SectoresAplicacion,
    "vertical": VerticalesInnovacion,
    "tipo_innovacion": TiposInnovacion,
    "trl": TRL,
    "mrl": MRL,
    "ods_principal": ODS,
    "ods_secundario": ODS,
}

# `por_determinar` is the one value that means "not evaluated yet"; the other
# neutral values (`no_aplica`, `sin_alineacion`) are an evaluation's result
PENDIENTE: Final[str] = EtapasDesarrollo.P_D.value

CLASIFICADA_TRIGGER: Final[str] = normalize_trigger(
    "BEGIN IF "
    + " OR ".join(
        f"NEW.{campo} = '{PENDIENTE}'"
        for campo, taxonomia in CLASIFICACIONES.items()
        if PENDIENTE in taxonomia.values
    )
    + """ THEN
        NEW.clasificada_at = NULL;
    ELSIF NEW.clasificada_at IS NULL THEN
        NEW.clasificada_at = clock_timestamp();
    END IF;
    RETURN NEW;
    END;
    """
)

# the advisory lock serializes the numbering of one year, so two proposals filed at
# the same time never read the same last number
CODIGO_TRIGGER: Final[Func] = Func(
    normalize_trigger("""
    DECLARE
        siguiente integer;
    BEGIN
        PERFORM pg_advisory_xact_lock(
            hashtext('{meta.db_table}.codigo'),
            NEW.anio_ingreso
        );
        SELECT coalesce(max(split_part(codigo, '-', 4)::integer), 0) + 1
        INTO siguiente
        FROM {meta.db_table}
        WHERE anio_ingreso = NEW.anio_ingreso;
        NEW.codigo = 'UAM-INN-'
            || NEW.anio_ingreso
            || '-'
            || lpad(siguiente::text, 3, '0');
        RETURN NEW;
    END;
    """)
)

ESTADO_COHERENTE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    terminal boolean;
BEGIN
    SELECT estado.terminal
    INTO terminal
    FROM {EstadoPropuesta._meta.db_table}
    AS estado
    WHERE estado.id = NEW.estado_id;
    IF terminal <> (NEW.cerrada_at IS NOT NULL) THEN
        RAISE check_violation
        USING
            COLUMN = 'cerrada_at',
            MESSAGE = 'Una propuesta está cerrada si y solo si su estado es terminal.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

########################################################################################


@track_table()
class Propuesta(ApiProtectedModel):
    # assigned by `trg_propuesta_codigo_asignar`, whatever the caller sends
    codigo = CharField(db_default="", default="", max_length=20)
    nombre = CharField(max_length=200)

    anio_ingreso = PositiveSmallIntegerField()

    actividad_origen = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="propuestas_originadas",
        to=Actividad,
    )

    problema = TextField(db_default="", default="")
    solucion = TextField(db_default="", default="")
    usuario_beneficiario = TextField(db_default="", default="")
    cliente_adoptante = TextField(db_default="", default="")

    nivel_formalizacion = CharField(max_length=30)
    etapa_desarrollo = CharField(
        db_default=EtapasDesarrollo.P_D,
        default=EtapasDesarrollo.P_D,
        max_length=30,
    )
    ambito_aplicacion = CharField(max_length=30)
    sector_aplicacion = CharField(
        db_default=SectoresAplicacion.P_D,
        default=SectoresAplicacion.P_D,
        max_length=30,
    )
    vertical = CharField(
        db_default=VerticalesInnovacion.P_D,
        default=VerticalesInnovacion.P_D,
        max_length=30,
    )
    tipo_innovacion = CharField(
        db_default=TiposInnovacion.P_D,
        default=TiposInnovacion.P_D,
        max_length=30,
    )
    trl = CharField(db_default=TRL.P_D, default=TRL.P_D, max_length=30)
    mrl = CharField(db_default=MRL.P_D, default=MRL.P_D, max_length=30)
    ods_principal = CharField(db_default=ODS.P_D, default=ODS.P_D, max_length=30)
    ods_secundario = CharField(db_default=ODS.N_A, default=ODS.N_A, max_length=30)

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="propuestas",
        to=EstadoPropuesta,
    )

    enlace_expediente = URLField(db_default="", default="", max_length=500)

    clasificada_at = DateTimeField(null=True)
    cerrada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="propuestas",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *(
                CheckConstraint(
                    condition=Q(**{f"{campo}__in": taxonomia.values}),
                    name=f"chk_%(class)s_{campo.replace('_', '')}",
                )
                for campo, taxonomia in CLASIFICACIONES.items()
            ),
            CheckConstraint(
                condition=Q(codigo__regex=r"^UAM-INN-[0-9]{4}-[0-9]{3,4}$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(anio_ingreso__gte=2015, anio_ingreso__lte=2100),
                name="chk_%(class)s_anio",
            ),
            CheckConstraint(
                condition=~Q(ods_principal=F("ods_secundario")),
                name="chk_%(class)s_ods_distintos",
            ),
            CheckConstraint(
                condition=~Q(ods_principal=ODS.N_A),
                name="chk_%(class)s_ods_principal",
            ),
            CheckConstraint(
                condition=(
                    Q(cerrada_at__isnull=True, motivo__isnull=True)
                    | Q(cerrada_at__isnull=False, motivo__isnull=False)
                ),
                name="chk_%(class)s_cierre",
            ),
            UniqueConstraint(fields=["codigo"], name="unq_%(class)s_codigo"),
            UniqueConstraint(
                Upper(ImmutableUnaccent("nombre")),
                name="unq_%(class)s_nombre",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                fields=["etapa_desarrollo", "estado"],
                name="idx_%(class)s_etapa_estado",
            ),
            Index(F("anio_ingreso").desc(), name="idx_%(class)s_anio"),
            Index(
                condition=Q(cerrada_at__isnull=True),
                fields=["etapa_desarrollo"],
                name="idx_%(class)s_vigente",
            ),
            Index(fields=["ods_principal"], name="idx_%(class)s_ods"),
            GinIndex(
                OpClass(
                    expression=Upper(
                        ImmutableUnaccent(
                            Concat(
                                "nombre",
                                Value(" "),
                                "problema",
                                Value(" "),
                                "solucion",
                                output_field=TextField(),
                            ),
                        ),
                    ),
                    name="gin_trgm_ops",
                ),
                name="gin_%(class)s_texto",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            ReadOnly(
                fields=["anio_ingreso", "codigo"],
                name="trg_readonly_codigo_anioingreso",
            ),
            *estado_lifecycle_triggers(
                entidad="propuesta",
                model=EstadoPropuesta,
                transicion_model=TransicionEstadoPropuesta,
            ),
            motivo_ambito_trigger(
                ambitos=(MotivoAmbitoTypes.CIERRE_PROPUESTA,),
                descripcion_field="motivo_descripcion",
                entidad="propuesta",
                motivo_table=Motivo._meta.db_table,  # ruff: ignore[private-member-access]
            ),
            Trigger(
                func=CLASIFICADA_TRIGGER,
                name="trg_propuesta_clasificada_marca",
                operation=(Insert | Update),
                when=Before,
            ),
            Trigger(
                func=CODIGO_TRIGGER,
                name="trg_propuesta_codigo_asignar",
                operation=Insert,
                when=Before,
            ),
            Trigger(
                func=ESTADO_COHERENTE_TRIGGER,
                name="trg_propuesta_estado_coherente",
                operation=(Insert | UpdateOf("estado_id", "cerrada_at")),
                when=Before,
            ),
        )
