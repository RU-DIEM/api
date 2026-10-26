from http import HTTPStatus

from .base import ApiError

########################################################################################


class UnauthorizedError(ApiError):
    default_detail: str = "No se proporcionaron credenciales de autenticación válidas."

    default_http_status: HTTPStatus = HTTPStatus.UNAUTHORIZED
