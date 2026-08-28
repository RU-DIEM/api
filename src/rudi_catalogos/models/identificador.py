from typing import TYPE_CHECKING

from django.db.models import BooleanField, CharField
from pgtrigger import Before, Insert, Trigger, Update

from api_utils.strings import normalize_trigger

from .base import RudiCatalogo

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import CheckConstraint, UniqueConstraint


########################################################################################


class TipoIdentificador(RudiCatalogo):
    descripcion = None

    regex = CharField(db_default="", default="", max_length=100)

    is_institucional = BooleanField(db_default=False, default=False)

    class Meta(RudiCatalogo.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            *filter(
                lambda c: c.name != "chk_%(class)s_descripcion",
                RudiCatalogo.Meta.constraints,
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiCatalogo.Meta.triggers,
            Trigger(
                name="trg_normalize_tipoidentificador",
                operation=(Insert | Update),
                when=Before,
                func=normalize_trigger(r"""
                    BEGIN
                        NEW.codigo = lower(btrim(NEW.codigo));
                        NEW.etiqueta = btrim(regexp_replace(NEW.etiqueta, '\s+', ' ', 'g'));
                        NEW.regex = btrim(NEW.regex);
                        RETURN NEW;
                    END;
                """),  # ruff: ignore[line-too-long]
            ),
            Trigger(
                name="trg_tipoidentificador_test_posix_validity",
                operation=(Insert | Update),
                when=Before,
                func=normalize_trigger("""
                    BEGIN
                        IF NEW.regex <> '' THEN
                            BEGIN
                                PERFORM '' ~* NEW.regex;
                            EXCEPTION WHEN invalid_regular_expression THEN
                                RAISE check_violation
                                USING
                                    COLUMN = 'regex',
                                    MESSAGE = 'No es una expresión regular válida.';
                            END;
                        END IF;
                        RETURN NEW;
                    END;
                """),
            ),
        )
