from typing import TYPE_CHECKING

from .academia import (
    CarreraDetailController,
    CarreraListAllController,
    CarreraListController,
    FacultadDetailController,
    FacultadListAllController,
    FacultadListController,
    InstitucionDetailController,
    InstitucionListAllController,
    InstitucionListController,
    InstitucionNormalizarController,
)
from .docente import (
    DocenteProfileDetailController,
    DocenteProfileListAllController,
    DocenteProfileListController,
)
from .estudiante import (
    EstudianteCarreraDetailController,
    EstudianteCarreraListController,
    EstudianteProfileDetailController,
    EstudianteProfileListAllController,
    EstudianteProfileListController,
)
from .externo import (
    ExternoProfileDetailController,
    ExternoProfileListAllController,
    ExternoProfileListController,
)
from .mentor import (
    MentorAreaExperienciaDetailController,
    MentorAreaExperienciaListController,
    MentorCertificacionDetailController,
    MentorCertificacionListController,
    MentorConfirmarController,
    MentorProfileDetailController,
    MentorProfileListAllController,
    MentorProfileListController,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "CarreraDetailController",
    "CarreraListAllController",
    "CarreraListController",
    "DocenteProfileDetailController",
    "DocenteProfileListAllController",
    "DocenteProfileListController",
    "EstudianteCarreraDetailController",
    "EstudianteCarreraListController",
    "EstudianteProfileDetailController",
    "EstudianteProfileListAllController",
    "EstudianteProfileListController",
    "ExternoProfileDetailController",
    "ExternoProfileListAllController",
    "ExternoProfileListController",
    "FacultadDetailController",
    "FacultadListAllController",
    "FacultadListController",
    "InstitucionDetailController",
    "InstitucionListAllController",
    "InstitucionListController",
    "InstitucionNormalizarController",
    "MentorAreaExperienciaDetailController",
    "MentorAreaExperienciaListController",
    "MentorCertificacionDetailController",
    "MentorCertificacionListController",
    "MentorConfirmarController",
    "MentorProfileDetailController",
    "MentorProfileListAllController",
    "MentorProfileListController",
)
