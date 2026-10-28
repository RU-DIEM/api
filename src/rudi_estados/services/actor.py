from django.db import connection

from rudi_estados.enums import ActorTypes

########################################################################################


def set_actor(actor: ActorTypes | str) -> None:
    """
    Declare who is acting for the rest of the current transaction.

    `trg_<tabla>_transicion_valida` reads it back through `rudi_actor()` and only
    accepts transitions declared for that actor. `SET LOCAL` ends with the
    transaction, so call it inside the `atomic` block that does the write.
    """

    value: str = actor.value if isinstance(actor, ActorTypes) else actor

    with connection.cursor() as cursor:
        cursor.execute("SELECT set_config('rudi.actor', %s, true)", [value])
