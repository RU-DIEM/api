from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    ForeignKey,
    JSONField,
    Q,
    UniqueConstraint,
)
from django.db.models.expressions import RawSQL
from django.db.models.functions import JSONObject
from pgtrigger import Before, Insert, Trigger, Update

from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_catalogos.enums import ParametroGrupoTypes, ParametroTypes

from .base import RudiCatalogo

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

TYPE_TRIGGER: Final[str] = normalize_trigger(rf"""
DECLARE
    forma text := jsonb_typeof(NEW.valor);
    texto text;
BEGIN
    IF NEW.tipo = '{ParametroTypes.BOOL.value}' THEN
        IF forma <> 'boolean' THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'Un parámetro binario exige un valor booleano.';
        END IF;
    ELSIF NEW.tipo = '{ParametroTypes.INT.value}' THEN
        IF forma <> 'number' THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'Un parámetro entero exige un valor numérico.';
        END IF;
        texto := NEW.valor #>> '{{}}';
        IF texto::numeric <> trunc(texto::numeric) THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'Un parámetro entero no admite decimales.';
        END IF;
    ELSIF NEW.tipo = '{ParametroTypes.LIST.value}' THEN
        IF forma <> 'array' THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'Un parámetro de lista exige un arreglo.';
        END IF;
        IF EXISTS (
            SELECT 1
            FROM jsonb_array_elements(NEW.valor)
            AS elemento
            WHERE jsonb_typeof(elemento) <> 'string'
        ) THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'Un parámetro de lista solo admite elementos de texto.';
        END IF;
    ELSIF NEW.tipo = '{ParametroTypes.STR.value}' THEN
        IF forma <> 'string' THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'Un parámetro de texto exige una cadena.';
        END IF;
    ELSIF NEW.tipo = '{ParametroTypes.TIME.value}' THEN
        IF forma <> 'string' THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'Una duración se expresa como cadena ISO 8601.';
        END IF;
        texto := NEW.valor #>> '{{}}';
        IF  (
            texto !~ '^P(\d+Y)?(\d+M)?(\d+D)?(T(\d+H)?(\d+M)?(\d+(\.\d+)?S)?)?$'
            OR
            texto = 'P'
            OR
            right(texto, 1) = 'T'
        ) THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'La duración debe seguir el formato ISO 8601, como PT30M o P365D.';
        END IF;
        BEGIN
            PERFORM texto::interval;
        EXCEPTION WHEN invalid_datetime_format OR datetime_field_overflow THEN
            RAISE check_violation
            USING
                COLUMN = 'valor',
                MESSAGE = 'La duración no representa un intervalo válido.';
        END;
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long]

########################################################################################


@track_table()
class Parametro(RudiCatalogo):
    etiqueta = None

    grupo = CharField(max_length=20)
    tipo = CharField(max_length=10)
    valor = JSONField()
    restricciones = JSONField(db_default=JSONObject(), default=dict)

    updated_by = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="parametros",
        to=settings.AUTH_USER_MODEL,
    )

    class Meta(RudiCatalogo.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *filter(
                lambda c: c.name != "chk_%(class)s_codigo_format",
                RudiCatalogo.Meta.constraints,
            ),
            CheckConstraint(
                condition=Q(codigo__regex=r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$"),
                name="chk_%(class)s_codigo_format",
            ),
            CheckConstraint(
                condition=Q(grupo__in=ParametroGrupoTypes.values),
                name="chk_%(class)s_grupo",
            ),
            CheckConstraint(
                condition=Q(tipo__in=ParametroTypes.values),
                name="chk_%(class)s_tipo",
            ),
            CheckConstraint(
                condition=RawSQL(
                    params=(),
                    output_field=BooleanField(),
                    sql="jsonb_typeof(restricciones) = 'object'",
                ),
                name="chk_%(class)s_restricciones",
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiCatalogo.Meta.triggers,
            Trigger(
                name="trg_parametro_valor_tipo",
                operation=(Insert | Update),
                when=Before,
                func=TYPE_TRIGGER,
            ),
        )
