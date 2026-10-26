from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    CheckConstraint,
    DateTimeField,
    ForeignKey,
    Func as DjangoFunc,
    GeneratedField,
    Q,
    UniqueConstraint,
)
from pgtrigger import (
    After,
    Before,
    Func as TriggerFunc,
    Insert,
    Trigger,
    Update,
)

from api_utils.db import track_table
from api_utils.strings import normalize_trigger
from rudi_catalogos.models import TipoIdentificador
from rudi_core.models import RudiProtectedModel

from .user import RudiUser

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

REGEX_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    regex_pat text;
BEGIN
    SELECT regex
    INTO regex_pat
    FROM {TipoIdentificador._meta.db_table}
    WHERE id = NEW.tipo_id;
    IF regex_pat <> '' AND NEW.valor !~ regex_pat THEN
        NEW.verificado_at = NULL;
        NEW.verificado_por_id = NULL;
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

IS_MAIN_TRIGGER: Final[TriggerFunc] = TriggerFunc(
    normalize_trigger("""
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM {meta.db_table}
            WHERE user_id = NEW.user_id
        ) THEN
            NEW.is_main = true;
        END IF;
        RETURN NEW;
    END;
    """)
)

UPDATE_MAIN_TRIGGER: Final[TriggerFunc] = TriggerFunc(
    normalize_trigger(f"""
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM {RudiUser._meta.db_table}
            AS persona
            WHERE persona.id = NEW.user_id
            AND persona.anonimizado_at IS NULL
        ) AND NOT EXISTS (
            SELECT 1
            FROM {{meta.db_table}}
            AS actual
            WHERE actual.user_id = NEW.user_id
            AND actual.is_main
        ) THEN
            RAISE check_violation
            USING
                COLUMN = 'is_main',
                MESSAGE = 'Un usuario activo no puede quedar sin identificador principal.';
        END IF;
        RETURN NULL;
    END;
    """)  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]
)

########################################################################################


class NormalizarIdentificador(DjangoFunc):
    arity: int = 1
    function: str = "regexp_replace"
    template: str = "upper(%(function)s(%(expressions)s, '[^A-Za-z0-9]', '', 'g'))"


########################################################################################


@track_table()
class IdentificadorUser(RudiProtectedModel):
    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="identificadores",
        to=RudiUser,
    )

    tipo = ForeignKey(
        on_delete=RESTRICT,
        related_name="identificadores",
        to=TipoIdentificador,
    )

    valor = CharField(max_length=20)

    valor_normalizado = GeneratedField(
        db_persist=True,
        expression=NormalizarIdentificador("valor"),
        output_field=CharField(max_length=20),
    )

    is_main = BooleanField(db_default=False, default=False)

    verificado_at = DateTimeField(null=True)
    verificado_por = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="identificadores_verificados",
        to=settings.AUTH_USER_MODEL,
    )

    class Meta(RudiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=(
                    Q(verificado_at__isnull=True, verificado_por__isnull=True)
                    | Q(verificado_at__isnull=False, verificado_por__isnull=False)
                ),
                name="chk_%(class)s_verificacion_coherente",
            ),
            CheckConstraint(
                condition=Q(
                    valor_normalizado__len__gte=4,
                    valor_normalizado__len__lte=20,
                ),
                name="chk_%(class)s_valor_longitud",
            ),
            UniqueConstraint(
                fields=["tipo", "valor_normalizado"],
                name="unq_%(class)s_valor",
            ),
            UniqueConstraint(
                fields=["user", "tipo"],
                name="unq_%(class)s_tipo_user",
            ),
            UniqueConstraint(
                condition=Q(is_main=True),
                fields=["user"],
                name="unq_%(class)s_principal",
            ),
        )

        triggers: Sequence[Trigger] = (
            *RudiProtectedModel.Meta.triggers,
            Trigger(
                name="trg_identificadoruser_regex",
                operation=(Insert | Update),
                when=Before,
                func=REGEX_TRIGGER,
            ),
            Trigger(
                name="trg_identificadoruser_first_main",
                operation=Insert,
                when=Before,
                func=IS_MAIN_TRIGGER,
            ),
            Trigger(
                name="trg_identificadoruser_protect_main",
                operation=Update,
                when=After,
                func=UPDATE_MAIN_TRIGGER,
            ),
        )
