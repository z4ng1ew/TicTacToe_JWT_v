from functools import wraps
from typing import Any, Callable, Optional
from flask import g, jsonify, request
from domain.service.auth_service import AuthService


class UserAuthenticator:
    def __init__(self, service: AuthService) -> None:
        self._service: AuthService = service

    def authenticate(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            header: Optional[str] = request.headers.get("Authorization")
            if header is None:
                return jsonify({"error": "Требуется авторизация"}), 401
            else:
                user_id: Optional[str] = self._service.authorize(header)
                if user_id is None:
                    return jsonify({"error": "Неверные учётные данные"}), 401
                else:
                    g.user_id = user_id
                    return func(*args, **kwargs)
        return wrapper
