from typing import TYPE_CHECKING

from pgtrigger import Before, Insert, Trigger

from api_utils.strings import normalize_trigger

if TYPE_CHECKING:
    from collections.abc import Mapping

    from api_utils.types import DatabaseModel

########################################################################################


def catalogo_activo_trigger(
    *,
    catalogos: Mapping[str, type[DatabaseModel]],
    entidad: str,
) -> Trigger:
    """
    Build the trigger that keeps new rows off deactivated catalog entries.

    Only inserts are checked: a historical row keeps the classification it was
    born with, even after the catalog entry is retired (D-18).

    Args:
        catalogos: Foreign key column (`tipo_actividad_id`) => catalog model.
        entidad: The table's name in the trigger name.

    Returns:
        The trigger, `trg_<entidad>_catalogo_activo`.

    """

    checks: str = "".join(
        f"""
            IF NEW.{columna} IS NOT NULL THEN
                SELECT is_active
                INTO activo
                FROM {modelo._meta.db_table}
                WHERE id = NEW.{columna};
                IF NOT FOUND THEN
                    RAISE foreign_key_violation USING COLUMN = '{columna}';
                END IF;
                IF NOT activo THEN
                    RAISE check_violation
                    USING
                        COLUMN = '{columna}',
                        MESSAGE = 'La entrada de catálogo está desactivada.';
                END IF;
            END IF;
        """  # ruff: ignore[hardcoded-sql-expression, private-member-access]
        for columna, modelo in catalogos.items()
    )

    return Trigger(
        declare=[("activo", "boolean")],
        func=normalize_trigger(f"{checks} RETURN NEW;"),
        name=f"trg_{entidad}_catalogo_activo",
        operation=Insert,
        when=Before,
    )


########################################################################################


def como_actor(actor: str, sql: str) -> str:
    """
    Run *sql* inside a trigger as *actor*, then restore the caller's actor.

    A trigger that moves another table's state (closing inscriptions of a
    cancelled activity, promoting the waiting list) acts as `sistema`, not as
    whoever wrote the row that fired it; `trg_<tabla>_transicion_valida` must
    see the transition the catalog declares for that actor.

    The enclosing function must `DECLARE actor_previo text`.

    Returns:
        The wrapped SQL.

    """

    return f"""
        actor_previo := current_setting('rudi.actor', true);
        PERFORM set_config('rudi.actor', '{actor}', true);
        {sql}
        PERFORM set_config('rudi.actor', coalesce(actor_previo, ''), true);
    """
