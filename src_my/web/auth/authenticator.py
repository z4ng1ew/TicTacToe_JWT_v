import uuid
from typing import Optional, Callable
from functools import wraps

from flask import request, jsonify

from domain.service.auth_service import AuthService


class UserAuthenticator:

    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    def get_current_user_id(self) -> Optional[uuid.UUID]:
        auth_header: Optional[str] = request.headers.get('Authorization')

        if auth_header is None:
            return None

        return self._auth_service.login(auth_header)

    def required(self, f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            user_id = self.get_current_user_id()

            if user_id is None:
                response             = jsonify({'error': 'Unauthorized'})
                response.status_code = 401
                response.headers['WWW-Authenticate'] = 'Basic realm="Login required"'
                return response
            else:
                return f(*args, user_id=user_id, **kwargs)

        return decorated