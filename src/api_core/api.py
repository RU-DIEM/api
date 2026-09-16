from typing import TYPE_CHECKING

from dmr.openapi import build_schema
from dmr.routing import Router

import api_auth.api
import rudi_auth.api
import rudi_catalogos.api
import rudi_estados.api
import rudi_profiles.api

from api_core.controllers.routers import sort_urls

if TYPE_CHECKING:
    from typing import Final

    from dmr.openapi.openapi import OpenAPI

########################################################################################

router: Final[Router] = Router(
    prefix="",
    urls=sort_urls((
        *api_auth.api.router.urls,
        *rudi_auth.api.router.urls,
        *rudi_catalogos.api.router.urls,
        *rudi_estados.api.router.urls,
        *rudi_profiles.api.router.urls,
    )),
)

schema: Final[OpenAPI] = build_schema(router)
