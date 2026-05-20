import base64
from typing import Optional
from domain.service.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService) -> None:
        self._user_service: UserService = user_service

    def register(self, login: str, password: str) -> bool:
        if not login or not password:
            return False
        else:
            return self._user_service.create_user(login, password)

    def authorize(self, auth_header: Optional[str]) -> Optional[str]:
        if not auth_header:
            return None
        elif not auth_header.startswith("Basic "):
            return None
        else:
            try:
                encoded: str = auth_header.split(" ", 1)[1]
                decoded_str: str = base64.b64decode(encoded).decode("utf-8")
                parts: list[str] = decoded_str.split(":", 1)
                if len(parts) != 2:
                    return None
                else:
                    login: str = parts[0]
                    password: str = parts[1]
                    return self._user_service.verify_credentials(login, password)
            except Exception:
                return None
