from typing import TYPE_CHECKING

from pgtrigger import (
    Before,
    F as TriggerF,
    Insert,
    Q as TriggerQ,
    Trigger,
    Update,
)

from api_utils.strings import normalize_trigger

if TYPE_CHECKING:
    from collections.abc import Sequence

    from api_utils.types import DatabaseModel

########################################################################################


def estado_lifecycle_triggers(
    *,
    entidad: str,
    field: str = "estado",
    model: type[DatabaseModel],
    transicion_model: type[DatabaseModel] | None = None,
) -> tuple[Trigger, ...]:
    """
    Build the triggers every table with a state machine shares.

    - `trg_<entidad>_estado_activo`: a row may only enter an active state.
    - `trg_<entidad>_estado_terminal`: a row in a terminal state never moves.
    - `trg_<entidad>_transicion_valida` (only with *transicion_model*): a change
      of state must be declared for the acting role (`rudi_actor()`); with no
      actor set, any declared transition is accepted.

    Args:
        entidad: The table's name in trigger names (`trg_<entidad>_...`).
        field: The foreign key that points at the state catalog.
        model: The state catalog.
        transicion_model: The catalog of declared transitions, if there is one.

    Returns:
        The triggers, to be spread into `Meta.triggers`.

    """

    fk: str = f"{field}_id"

    estado_table: str = model._meta.db_table  # ruff: ignore[private-member-access]

    estado_activo = Trigger(
        declare=[("activo", "boolean")],
        func=normalize_trigger(f"""
            IF TG_OP = 'UPDATE' AND OLD.{fk} IS NOT DISTINCT FROM NEW.{fk} THEN
                RETURN NEW;
            END IF;
            SELECT is_active
            INTO activo
            FROM {estado_table}
            WHERE id = NEW.{fk};
            IF NOT FOUND THEN
                RAISE foreign_key_violation USING COLUMN = '{fk}';
            END IF;
            IF NOT activo THEN
                RAISE check_violation
                USING
                    COLUMN = '{fk}',
                    MESSAGE = 'El estado está desactivado.';
            END IF;
            RETURN NEW;
        """),  # ruff: ignore[hardcoded-sql-expression]
        name=f"trg_{entidad}_estado_activo",
        operation=(Insert | Update),
        when=Before,
    )

    cambia_estado: TriggerQ = TriggerQ(**{
        f"old__{field}__df": TriggerF(f"new__{field}")
    })

    estado_terminal = Trigger(
        condition=cambia_estado,
        declare=[("terminal_previo", "boolean")],
        func=normalize_trigger(f"""
            SELECT terminal
            INTO terminal_previo
            FROM {estado_table}
            WHERE id = OLD.{fk};
            IF terminal_previo THEN
                RAISE check_violation
                USING
                    COLUMN = '{fk}',
                    MESSAGE = 'El estado es terminal; no puede cambiar.';
            END IF;
            RETURN NEW;
        """),  # ruff: ignore[hardcoded-sql-expression]
        name=f"trg_{entidad}_estado_terminal",
        operation=Update,
        when=Before,
    )

    triggers: list[Trigger] = [estado_activo, estado_terminal]

    if transicion_model is not None:
        transicion_table: str = transicion_model._meta.db_table  # ruff: ignore[private-member-access]

        triggers.append(
            Trigger(
                condition=cambia_estado,
                func=normalize_trigger(f"""
                    IF NOT EXISTS (
                        SELECT 1
                        FROM {transicion_table}
                        WHERE (
                            from_estado_id = OLD.{fk} AND
                            to_estado_id = NEW.{fk} AND
                            is_active AND
                            (rudi_actor() IS NULL OR actor = rudi_actor())
                        )
                    ) THEN
                        RAISE check_violation
                        USING
                            COLUMN = '{fk}',
                            MESSAGE = 'La transición no está declarada para este actor.';
                    END IF;
                    RETURN NEW;
                """),  # ruff: ignore[hardcoded-sql-expression, line-too-long]
                name=f"trg_{entidad}_transicion_valida",
                operation=Update,
                when=Before,
            ),
        )

    return tuple(triggers)


########################################################################################


def motivo_ambito_trigger(
    *,
    ambitos: Sequence[str],
    descripcion_field: str | None = None,
    entidad: str,
    motivo_field: str = "motivo",
    motivo_table: str,
) -> Trigger:
    """
    Build the trigger that checks a reason picked from the closed `Motivo` list.

    The reason must exist, be active, and belong to one of the action's
    *ambitos*. With *descripcion_field*, a reason that `require_descripcion`
    also needs a free-text description. An update that keeps the same reason
    and description is not re-checked, so retiring a reason never locks the
    rows that already cite it.

    Args:
        ambitos: The `MotivoAmbitoTypes` values the reason may belong to.
        descripcion_field: The free-text column, if the table has one.
        entidad: The table's name in the trigger name (`trg_<entidad>_motivo`).
        motivo_field: The foreign key that points at the reason.
        motivo_table: The reason catalog's table.

    Returns:
        The trigger.

    """

    fk: str = f"{motivo_field}_id"

    sin_cambio: str = f"OLD.{fk} IS NOT DISTINCT FROM NEW.{fk}" + (
        f" AND OLD.{descripcion_field} IS NOT DISTINCT FROM NEW.{descripcion_field}"
        if descripcion_field
        else ""
    )

    lista: str = ", ".join(f"'{a}'" for a in ambitos)

    descripcion_check: str = (
        f"""
            IF motivo.require_descripcion AND length(NEW.{descripcion_field}) = 0 THEN
                RAISE check_violation
                USING
                    COLUMN = '{descripcion_field}',
                    MESSAGE = 'Este motivo exige una descripción.';
            END IF;
        """
        if descripcion_field
        else ""
    )

    return Trigger(
        declare=[("motivo", "RECORD")],
        func=normalize_trigger(f"""
            IF NEW.{fk} IS NULL OR (TG_OP = 'UPDATE' AND {sin_cambio}) THEN
                RETURN NEW;
            END IF;
            SELECT ambito, require_descripcion, is_active
            INTO motivo
            FROM {motivo_table}
            WHERE id = NEW.{fk};
            IF NOT FOUND THEN
                RAISE foreign_key_violation USING COLUMN = '{fk}';
            END IF;
            IF NOT motivo.is_active THEN
                RAISE check_violation
                USING
                    COLUMN = '{fk}',
                    MESSAGE = 'El motivo está desactivado.';
            END IF;
            IF motivo.ambito NOT IN ({lista}) THEN
                RAISE check_violation
                USING
                    COLUMN = '{fk}',
                    MESSAGE = 'El motivo no pertenece al ámbito de esta acción.';
            END IF;
            {descripcion_check}
            RETURN NEW;
        """),  # ruff: ignore[hardcoded-sql-expression]
        name=f"trg_{entidad}_motivo",
        operation=(Insert | Update),
        when=Before,
    )
