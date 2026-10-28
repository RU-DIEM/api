from typing import TYPE_CHECKING

from rudi_auth.enums import AccesoDatoTypes
from rudi_auth.models import AccesoDatoPersonal, RudiUser

if TYPE_CHECKING:
    from uuid import UUID

    from api_auth.models import ApiUser

########################################################################################


def registrar_acceso(
    *,
    accedido_por: ApiUser,
    persona_id: UUID,
    recurso: str,
    tipo: AccesoDatoTypes = AccesoDatoTypes.LECTURA,
) -> None:
    """
    Record that someone read or exported another person's personal data.

    Reading one's own data is not recorded: the record answers "who saw my
    data", and the person is not the one they need to ask about.
    """

    if RudiUser.objects.filter(pk=persona_id, user=accedido_por).exists():
        return

    if not RudiUser.objects.filter(pk=persona_id).exists():
        return

    AccesoDatoPersonal.objects.create(
        accedido_por=accedido_por,
        recurso=recurso[:200],
        tipo=tipo,
        user_id=persona_id,
    )
