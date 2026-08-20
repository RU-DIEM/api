from typing import TYPE_CHECKING, Final

from django.db.models import (
    BooleanField,
    CharField,
    CheckConstraint,
    JSONField,
    Q,
    TextField,
)
from django.db.models.expressions import RawSQL
from django.db.models.functions import JSONArray
from pgtrigger import AnyChange, Before, Insert, Row, Trigger, Update

from api_utils.strings import normalize_trigger
from rudi_catalogos.models.base import RudiCatalogo

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import UniqueConstraint

########################################################################################

INTEGRITY_TRIGGER: Final[str] = normalize_trigger(r"""
DECLARE
    campo text;
    texto text;
BEGIN
    IF EXISTS (
        SELECT 1
        FROM jsonb_array_elements_text(NEW.variables)
        AS elem
        WHERE NEW.asunto NOT LIKE '%{' || elem || '}%'
        AND
        NEW.cuerpo NOT LIKE '%{' || elem || '}%'
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'variables',
            MESSAGE = 'Una de las variables especificadas no está presente en el asunto o el cuerpo de la plantilla.';
    END IF;
    FOR campo, texto IN
        VALUES ('asunto', NEW.asunto), ('cuerpo', NEW.cuerpo)
    LOOP
        IF EXISTS (
            SELECT 1
            FROM regexp_matches(texto, '\{([^}]+)\}', 'g')
            AS match(m)
            WHERE NOT (NEW.variables ? match.m[1])
        ) THEN
            RAISE check_violation
            USING
                COLUMN = campo,
                MESSAGE = format('Uno de los parámetros especificados en el %s no tiene una variable correspondiente.', campo);
        END IF;
    END LOOP;
    RETURN NEW;
END;
""")  # ruff: ignore[line-too-long]

########################################################################################


class PlantillaMensaje(RudiCatalogo):
    descripcion = None

    asunto = CharField(max_length=200)
    cuerpo = TextField()
    variables = JSONField(db_default=JSONArray(), default=list)

    class Meta(RudiCatalogo.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *filter(
                lambda c: "descripcion" not in c.name,
                RudiCatalogo.Meta.constraints,
            ),
            CheckConstraint(
                condition=RawSQL(
                    params=(),
                    output_field=BooleanField(),
                    sql="jsonb_typeof(variables) = 'array'",
                ),
                name="chk_%(class)s_variables",
            ),
            CheckConstraint(
                condition=Q(cuerpo__len__gte=1, cuerpo__len__lte=8_000),
                name="chk_%(class)s_cuerpo",
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiCatalogo.Meta.triggers,
            Trigger(
                level=Row,
                name="trg_plantillamensaje_variables_insert_integrity",
                operation=Insert,
                when=Before,
                func=INTEGRITY_TRIGGER,
            ),
            Trigger(
                condition=AnyChange("asunto", "cuerpo", "variables"),
                level=Row,
                name="trg_plantillamensaje_variables_update_integrity",
                operation=Update,
                when=Before,
                func=INTEGRITY_TRIGGER,
            ),
        )
