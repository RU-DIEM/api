from typing import TYPE_CHECKING, Final

from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CharField,
    CheckConstraint,
    Q,
    TextField,
)
from django.db.models.expressions import Value
from pgtrigger import AnyChange, Before, Insert, Trigger, Update

from api_utils.strings import normalize_trigger

from .base import RudiCatalogo

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
        FROM unnest(NEW.variables)
        AS elemento
        WHERE NEW.asunto NOT LIKE '%{' || elemento || '}%'
        AND
        NEW.cuerpo NOT LIKE '%{' || elemento || '}%'
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'variables',
            MESSAGE = 'Una de las variables especificadas no está presente en el asunto o el cuerpo de la plantilla.';
    END IF;
    FOR
        campo,
        texto
    IN VALUES
        ('asunto', NEW.asunto),
        ('cuerpo', NEW.cuerpo)
    LOOP
        IF EXISTS (
            SELECT 1
            FROM regexp_matches(texto, '\{([^}]+)\}', 'g')
            AS match(m)
            WHERE NOT (match.m[1] = ANY(NEW.variables))
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
    variables = ArrayField(
        base_field=CharField(max_length=50),
        db_default=Value(value=[], output_field=ArrayField(CharField(max_length=50))),
        default=list,
    )

    class Meta(RudiCatalogo.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *filter(
                lambda c: c.name != "chk_%(class)s_descripcion",
                RudiCatalogo.Meta.constraints,
            ),
            CheckConstraint(
                condition=Q(cuerpo__len__gte=1, cuerpo__len__lte=8_000),
                name="chk_%(class)s_cuerpo",
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiCatalogo.Meta.triggers,
            Trigger(
                name="trg_plantillamensaje_variables_insert_integrity",
                operation=Insert,
                when=Before,
                func=INTEGRITY_TRIGGER,
            ),
            Trigger(
                condition=AnyChange("asunto", "cuerpo", "variables"),
                name="trg_plantillamensaje_variables_update_integrity",
                operation=Update,
                when=Before,
                func=INTEGRITY_TRIGGER,
            ),
        )
