import base64
import hashlib
import uuid
from typing import Optional

from domain.model.signup_request import SignUpRequest
from domain.service.user_service import UserService
from datasource.model.user_ds import UserDS


class AuthService:

    def __init__(self, user_service: UserService):
        self._user_service = user_service

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, request: SignUpRequest) -> bool:
        existing = self._user_service.get_by_login(request.login)

        if existing is not None:
            return False
        else:
            user_ds               = UserDS()
            user_ds.id            = str(uuid.uuid4())
            user_ds.login         = request.login
            user_ds.password_hash = self._hash_password(request.password)

            self._user_service.save(user_ds)

            return True

    def login(self, auth_header: str) -> Optional[uuid.UUID]:
        try:
            encoded         = auth_header.split(' ')[1]
            decoded         = base64.b64decode(encoded).decode('utf-8')
            login, password = decoded.split(':', maxsplit=1)
        except Exception:
            return None

        user_ds = self._user_service.get_by_login(login)

        if user_ds is None:
            return None
        elif user_ds.password_hash != self._hash_password(password):
            return None
        else:
            return uuid.UUID(user_ds.id)