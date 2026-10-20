from http import HTTPStatus

from .base import ApiError

########################################################################################


class ForbiddenError(ApiError):
    default_detail: str = "No tiene permiso para realizar esta acción."

    default_http_status: HTTPStatus = HTTPStatus.FORBIDDEN
