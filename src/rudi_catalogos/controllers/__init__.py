from typing import TYPE_CHECKING

from .actividad import (
    TipoActividadDetailController,
    TipoActividadListAllController,
    TipoActividadListController,
)
from .area import (
    AreaExperienciaDetailController,
    AreaExperienciaListAllController,
    AreaExperienciaListController,
)
from .identificador import (
    TipoIdentificadorDetailController,
    TipoIdentificadorListAllController,
    TipoIdentificadorListController,
)
from .mentor import (
    TipoMentorDetailController,
    TipoMentorListAllController,
    TipoMentorListController,
)
from .motivo import (
    MotivoDetailController,
    MotivoListAllController,
    MotivoListController,
)
from .parametro import (
    ParametroDetailController,
    ParametroListAllController,
)
from .plantilla import (
    PlantillaMensajeDetailController,
    PlantillaMensajeListAllController,
    PlantillaMensajeListController,
)
from .reconocimiento import (
    TipoReconocimientoDetailController,
    TipoReconocimientoListAllController,
    TipoReconocimientoListController,
)
from .rol import (
    RolParticipacionDetailController,
    RolParticipacionListAllController,
    RolParticipacionListController,
)
from .ubicaciones import (
    DepartamentoListAllController,
    MunicipioListAllController,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "AreaExperienciaDetailController",
    "AreaExperienciaListAllController",
    "AreaExperienciaListController",
    "DepartamentoListAllController",
    "MotivoDetailController",
    "MotivoListAllController",
    "MotivoListController",
    "MunicipioListAllController",
    "ParametroDetailController",
    "ParametroListAllController",
    "PlantillaMensajeDetailController",
    "PlantillaMensajeListAllController",
    "PlantillaMensajeListController",
    "RolParticipacionDetailController",
    "RolParticipacionListAllController",
    "RolParticipacionListController",
    "TipoActividadDetailController",
    "TipoActividadListAllController",
    "TipoActividadListController",
    "TipoIdentificadorDetailController",
    "TipoIdentificadorListAllController",
    "TipoIdentificadorListController",
    "TipoMentorDetailController",
    "TipoMentorListAllController",
    "TipoMentorListController",
    "TipoReconocimientoDetailController",
    "TipoReconocimientoListAllController",
    "TipoReconocimientoListController",
)
