from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    JSONField,
    PositiveSmallIntegerField,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
)
from django.db.models.functions import Now
from django.utils.timezone import now
from pgtrigger import Before, Func, Insert, ReadOnly, Trigger, UpdateOf

from api_core.models.base import ApiAppendOnlyModel, ApiProtectedModel
from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_auth.models import RudiUser
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo
from rudi_estados.models import EstadoConstancia, EstadoParticipacion
from rudi_estados.triggers import estado_lifecycle_triggers, motivo_ambito_trigger
from rudi_participacion.models import Participacion

from .plantilla import PlantillaConstancia

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

FOLIO_TRIGGER: Final[str] = normalize_trigger("""
BEGIN
    NEW.folio = 'DIEM-'
        || to_char(rudi_hoy(), 'YYYY')
        || '-'
        || lpad(nextval('rudiconstancias_folio_seq')::text, 6, '0');
    RETURN NEW;
END;
""")

ESTADO_COHERENTE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    valida boolean;
BEGIN
    SELECT valid
    INTO valida
    FROM {EstadoConstancia._meta.db_table}
    WHERE id = NEW.estado_id;
    IF valida AND NEW.anulada_at IS NOT NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'estado_id',
            MESSAGE = 'Una constancia anulada no puede estar en un estado válido.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

REEMPLAZO_TRIGGER: Final[str] = normalize_trigger("""
DECLARE
    anulada timestamptz;
BEGIN
    IF NEW.reemplaza_a_id IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT anulada_at
    INTO anulada
    FROM {meta.db_table}
    WHERE id = NEW.reemplaza_a_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'reemplaza_a_id';
    END IF;
    IF anulada IS NULL THEN
        RAISE check_violation
        USING
            COLUMN = 'reemplaza_a_id',
            MESSAGE = 'Solo se reemplaza una constancia anulada.';
    END IF;
    RETURN NEW;
END;
""")

########################################################################################


@track_table()
class Constancia(ApiProtectedModel):
    # assigned by `trg_constancia_folio_asignar`, whatever the caller sends
    folio = CharField(db_default="", default="", max_length=30)

    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=RudiUser,
    )

    plantilla = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=PlantillaConstancia,
    )

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=EstadoConstancia,
    )

    codigo_verificacion = CharField(max_length=12)

    nombre_congelado = CharField(max_length=201)
    identificador_congelado = CharField(db_default="", default="", max_length=20)
    contenido_congelado = JSONField()
    texto_congelado = TextField()

    emitida_at = DateTimeField(db_default=Now(), default=now)
    emitida_por = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias_emitidas",
        to=settings.AUTH_USER_MODEL,
    )
    solicitada_at = DateTimeField(null=True)

    anulada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="constancias",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    reemplaza_a = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="+",
        to="self",
    )

    documento_url = URLField(db_default="", default="", max_length=500)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(folio__regex=r"^DIEM-[0-9]{4}-[0-9]{6}$"),
                name="chk_%(class)s_folio_format",
            ),
            CheckConstraint(
                condition=Q(codigo_verificacion__regex=r"^[A-Z0-9]{8,12}$"),
                name="chk_%(class)s_verificacion_format",
            ),
            CheckConstraint(
                condition=(
                    Q(anulada_at__isnull=True, motivo__isnull=True)
                    | Q(anulada_at__isnull=False, motivo__isnull=False)
                ),
                name="chk_%(class)s_anulacion",
            ),
            CheckConstraint(
                condition=Q(reemplaza_a__isnull=True) | ~Q(reemplaza_a=F("id")),
                name="chk_%(class)s_no_autoreemplazo",
            ),
            CheckConstraint(
                condition=Q(contenido_congelado__typeof="object"),
                name="chk_%(class)s_contenido",
            ),
            UniqueConstraint(fields=["folio"], name="unq_%(class)s_folio"),
            UniqueConstraint(
                fields=["codigo_verificacion"],
                name="unq_%(class)s_verificacion",
            ),
            UniqueConstraint(
                condition=Q(reemplaza_a__isnull=False),
                fields=["reemplaza_a"],
                name="unq_%(class)s_reemplazo",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                F("user"),
                F("emitida_at").desc(),
                name="idx_%(class)s_user",
            ),
        )

        # what a certificate says is frozen the moment it is issued (D-16)
        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            ReadOnly(
                fields=[
                    "codigo_verificacion",
                    "contenido_congelado",
                    "emitida_at",
                    "emitida_por",
                    "folio",
                    "identificador_congelado",
                    "nombre_congelado",
                    "plantilla",
                    "texto_congelado",
                    "user",
                ],
                name="trg_readonly_snapshot",
            ),
            *estado_lifecycle_triggers(entidad="constancia", model=EstadoConstancia),
            motivo_ambito_trigger(
                ambitos=(
                    MotivoAmbitoTypes.NULL_CONSTANCIA,
                    MotivoAmbitoTypes.NULL_PARTICIPACION,
                ),
                descripcion_field="motivo_descripcion",
                entidad="constancia",
                motivo_table=Motivo._meta.db_table,  # ruff: ignore[private-member-access]
            ),
            Trigger(
                func=FOLIO_TRIGGER,
                name="trg_constancia_folio_asignar",
                operation=Insert,
                when=Before,
            ),
            Trigger(
                func=ESTADO_COHERENTE_TRIGGER,
                name="trg_constancia_estado_coherente",
                operation=(Insert | UpdateOf("estado_id", "anulada_at")),
                when=Before,
            ),
            Trigger(
                func=Func(REEMPLAZO_TRIGGER),
                name="trg_constancia_reemplazo_anulado",
                operation=(Insert | UpdateOf("reemplaza_a_id")),
                when=Before,
            ),
        )


########################################################################################


VALIDA_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    participacion RECORD;
    titular uuid;
BEGIN
    SELECT p.user_id, p.validada_at, p.anulada_at, e.allow_constancia
    INTO participacion
    FROM {Participacion._meta.db_table}
    AS p
    JOIN {EstadoParticipacion._meta.db_table}
    AS e
    ON e.id = p.estado_id
    WHERE p.id = NEW.participacion_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'participacion_id';
    END IF;
    SELECT user_id
    INTO titular
    FROM {Constancia._meta.db_table}
    WHERE id = NEW.constancia_id;
    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'constancia_id';
    END IF;
    IF participacion.user_id <> titular THEN
        RAISE check_violation
        USING
            COLUMN = 'participacion_id',
            MESSAGE = 'La participación es de otra persona.';
    END IF;
    IF participacion.validada_at IS NULL
    OR participacion.anulada_at IS NOT NULL
    OR NOT participacion.allow_constancia THEN
        RAISE check_violation
        USING
            COLUMN = 'participacion_id',
            MESSAGE = 'La participación no está validada en un estado que admita constancia.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]


class ConstanciaParticipacion(ApiAppendOnlyModel):
    constancia = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Constancia,
    )

    participacion = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=Participacion,
    )

    orden = PositiveSmallIntegerField()

    class Meta(ApiAppendOnlyModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(
                fields=["constancia", "participacion"],
                name="unq_%(class)s_par",
            ),
            UniqueConstraint(
                fields=["constancia", "orden"],
                name="unq_%(class)s_orden",
            ),
        )

        triggers: Sequence[Trigger] = (
            *ApiAppendOnlyModel.Meta.triggers,
            Trigger(
                func=VALIDA_TRIGGER,
                name="trg_constanciaparticipacion_amparo",
                operation=Insert,
                when=Before,
            ),
        )
