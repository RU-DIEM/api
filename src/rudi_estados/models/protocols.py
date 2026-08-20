from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .base import RudiEstado

########################################################################################


class RudiConcreteTransicionProtocol[Estado: RudiEstado](Protocol):
    from_estado: Estado
    to_estado: Estado


########################################################################################


class RudiTransicionProtocol[Estado: RudiEstado](
    RudiConcreteTransicionProtocol[Estado],
    Protocol,
):
    require_motivo: bool
    require_descripcion: bool
    actor: str
