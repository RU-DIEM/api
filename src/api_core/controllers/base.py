from dmr import Controller
from dmr.plugins.msgspec import MsgspecJsonParser, MsgspecJsonRenderer
from dmr.serializer import BaseSerializer

from api_auth.enums import TokenTypes
from api_auth.security import JwtCookieAsyncAuth, JwtHeaderAsyncAuth
from api_auth.services.jwt import REQUIRED_CLAIMS
from api_core.config import CONFIG
from api_exceptions.schemas import ApiErrorResponse
from api_utils.types import UsableHttpRequest

from .endpoints import PathOperationIdEndpoint
from .mixins import HandleNotAllowedMixin
from .throttles import DEFAULT_THROTTLES

########################################################################################


class BaseController[Serializer: BaseSerializer](
    HandleNotAllowedMixin,
    Controller[Serializer],
):
    auth = (
        JwtCookieAsyncAuth(
            algorithm=CONFIG.JWT_ALGORITHM,
            cookie_name=TokenTypes.ACCESS,
            require_claims=REQUIRED_CLAIMS,
            secret=CONFIG.JWT_SECRET_KEY.get_secret_value(),
            security_scheme_name="jwtCookie",
        ),
        JwtHeaderAsyncAuth(
            algorithm=CONFIG.JWT_ALGORITHM,
            require_claims=REQUIRED_CLAIMS,
            secret=CONFIG.JWT_SECRET_KEY.get_secret_value(),
            security_scheme_name="jwtHeader",
        ),
    )

    endpoint_cls = PathOperationIdEndpoint

    error_model = ApiErrorResponse

    namespace = ""
    variant = ""

    parsers = (MsgspecJsonParser(),)
    renderers = (MsgspecJsonRenderer(),)

    request: UsableHttpRequest

    summary = None
    description = None

    throttling = DEFAULT_THROTTLES
