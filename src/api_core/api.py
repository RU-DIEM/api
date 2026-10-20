from typing import TYPE_CHECKING

from dmr.openapi import build_schema
from dmr.routing import Router

import api_auth.api
import api_media.api

from api_core.openapi import OPENAPI_CONFIG, ApiOpenAPIContext

if TYPE_CHECKING:
    from typing import Final

    from dmr.openapi.openapi import OpenAPI

########################################################################################

router: Final[Router] = Router(prefix="")

router.include(api_auth.api.router)
router.include(api_media.api.router)

schema: Final[OpenAPI] = build_schema(
    router,
    context=ApiOpenAPIContext(config=OPENAPI_CONFIG),
)
