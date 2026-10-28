from typing import TYPE_CHECKING

from .base import RudiAuthController
from .consentimiento import (
    ConsentimientoDatosDetailController,
    ConsentimientoRetiroController,
)
from .email import EmailConfirmController, EmailResendController
from .identificador import (
    IdentificadorUserDetailController,
    IdentificadorUserListController,
)
from .me import (
    MeConsentimientoController,
    MeDetailController,
    MeIdentificadoresController,
)
from .password import (
    InviteAcceptController,
    PasswordConfirmController,
    PasswordResetController,
)
from .politica import (
    PoliticaPrivacidadDetailController,
    PoliticaPrivacidadListAllController,
    PoliticaPrivacidadListController,
    PoliticaVigenteController,
)
from .register import (
    RudiInviteController,
    RudiRegisterController,
)
from .user import (
    AccesoDatoPersonalListController,
    RudiUserDetailController,
    RudiUserListAllController,
    RudiUserListController,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################

__all__: Sequence[str] = (
    "AccesoDatoPersonalListController",
    "ConsentimientoDatosDetailController",
    "ConsentimientoRetiroController",
    "EmailConfirmController",
    "EmailResendController",
    "IdentificadorUserDetailController",
    "IdentificadorUserListController",
    "InviteAcceptController",
    "MeConsentimientoController",
    "MeDetailController",
    "MeIdentificadoresController",
    "PasswordConfirmController",
    "PasswordResetController",
    "PoliticaPrivacidadDetailController",
    "PoliticaPrivacidadListAllController",
    "PoliticaPrivacidadListController",
    "PoliticaVigenteController",
    "RudiAuthController",
    "RudiInviteController",
    "RudiRegisterController",
    "RudiUserDetailController",
    "RudiUserListAllController",
    "RudiUserListController",
)
