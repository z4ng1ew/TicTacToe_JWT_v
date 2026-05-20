import uuid
from functools import wraps
from typing    import Callable

from flask import request, jsonify, Response

from domain.service.auth_service import AuthService


class UserAuthenticator:

    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service

    def _get_current_user_id(self) -> uuid.UUID | None:
        auth_header: str | None = request.headers.get("Authorization")

        if auth_header is None:
            return None
        else:
            return self._auth_service.login(auth_header)

    def authenticate(self, handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(*args, **kwargs) -> Response:
            user_id = self._get_current_user_id()

            if user_id is None:
                response                            = jsonify({"error": "Unauthorized"})
                response.status_code                = 401
                response.headers["WWW-Authenticate"] = 'Basic realm="Login required"'
                return response
            else:
                return handler(*args, user_id=user_id, **kwargs)

        return wrapper
