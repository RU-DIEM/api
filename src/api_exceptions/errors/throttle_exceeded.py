from http import HTTPStatus

from .base import ApiError

########################################################################################


class ThrottleExceededError(ApiError):
    default_detail: str = "Ha superado el límite de uso establecido para este recurso."

    default_http_status: HTTPStatus = HTTPStatus.TOO_MANY_REQUESTS
