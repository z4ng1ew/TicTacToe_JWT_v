import uuid
from functools import wraps
from typing    import Callable

from flask import request, jsonify, Response, g

from domain.service.jwt_provider import JwtProvider


class UserAuthenticator:

    def __init__(self, jwt_provider: JwtProvider) -> None:
        self._jwt_provider = jwt_provider

    def _extract_token(self) -> str | None:
        auth_header: str | None = request.headers.get("Authorization")

        if auth_header is None:
            return None
        elif not auth_header.startswith("Bearer "):
            return None
        else:
            return auth_header.split(" ", maxsplit=1)[1].strip()

    def _get_current_user_id(self) -> uuid.UUID | None:
        token = self._extract_token()

        if token is None:
            return None
        elif not self._jwt_provider.validate_access_token(token):
            return None

        user_id_str = self._jwt_provider.get_uuid_from_token(token)

        if user_id_str is None:
            return None
        else:
            return uuid.UUID(user_id_str)

    def authenticate(self, handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(*args, **kwargs) -> Response:
            user_id = self._get_current_user_id()

            if user_id is None:
                response                            = jsonify({"error": "Unauthorized"})
                response.status_code                = 401
                response.headers["WWW-Authenticate"] = 'Bearer realm="Access token required"'
                return response
            else:
                g.current_user_id = user_id
                return handler(*args, user_id=user_id, **kwargs)

        return wrapper
