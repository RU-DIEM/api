from typing import TYPE_CHECKING

from dmr.openapi import build_schema
from dmr.routing import Router

import api_auth.api
import rudi_actividades.api
import rudi_analitica.api
import rudi_auth.api
import rudi_catalogos.api
import rudi_constancias.api
import rudi_estados.api
import rudi_notificaciones.api
import rudi_participacion.api
import rudi_portafolio.api
import rudi_profiles.api
import rudi_puntos.api

from api_core.openapi import OPENAPI_CONFIG, ApiOpenAPIContext

if TYPE_CHECKING:
    from typing import Final

    from dmr.openapi.openapi import OpenAPI

########################################################################################

router: Final[Router] = Router(prefix="")

router.include(api_auth.api.router)
router.include(rudi_auth.api.router)
router.include(rudi_catalogos.api.router)
router.include(rudi_estados.api.router)
router.include(rudi_profiles.api.router)
router.include(rudi_actividades.api.router)
router.include(rudi_participacion.api.router)
router.include(rudi_puntos.api.router)
router.include(rudi_constancias.api.router)
router.include(rudi_portafolio.api.router)
router.include(rudi_notificaciones.api.router)
router.include(rudi_analitica.api.router)

schema: Final[OpenAPI] = build_schema(
    router,
    context=ApiOpenAPIContext(config=OPENAPI_CONFIG),
)
