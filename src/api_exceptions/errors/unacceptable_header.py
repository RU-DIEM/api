from http import HTTPStatus

from .base import ApiError

########################################################################################


class UnacceptableHeaderError(ApiError):
    default_detail: str = "Ha enviado un `Accept` header inválido."

    default_http_status: HTTPStatus = HTTPStatus.NOT_ACCEPTABLE
