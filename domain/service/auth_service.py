import hashlib
import uuid

from domain.model.signup_request      import SignUpRequest
from domain.model.jwt_request         import JwtRequest
from domain.model.jwt_response        import JwtResponse
from domain.model.user                import User
from domain.service.user_service      import UserService
from domain.service.jwt_provider      import JwtProvider
from datasource.model.user_ds         import UserDS


class AuthService:

    def __init__(
        self,
        user_service: UserService,
        jwt_provider: JwtProvider,
    ) -> None:
        self._user_service = user_service
        self._jwt_provider = jwt_provider

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

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

    def login(self, request: JwtRequest) -> JwtResponse | None:
        user_ds = self._user_service.get_by_login(request.login)

        if user_ds is None:
            return None
        elif user_ds.password_hash != self._hash_password(request.password):
            return None
        else:
            user               = User(login=user_ds.login)
            user.id            = uuid.UUID(user_ds.id)
            user.password_hash = user_ds.password_hash

            access  = self._jwt_provider.generate_access_token(user)
            refresh = self._jwt_provider.generate_refresh_token(user)

            return JwtResponse(type="Bearer", access_token=access, refresh_token=refresh)

    def refresh_access(self, refresh_token: str) -> JwtResponse | None:
        if not self._jwt_provider.validate_refresh_token(refresh_token):
            return None

        user_id_str = self._jwt_provider.get_uuid_from_token(refresh_token)

        if user_id_str is None:
            return None

        user_ds = self._user_service.get_by_id(user_id_str)

        if user_ds is None:
            return None
        else:
            user               = User(login=user_ds.login)
            user.id            = uuid.UUID(user_ds.id)
            user.password_hash = user_ds.password_hash

            new_access = self._jwt_provider.generate_access_token(user)

            return JwtResponse(type="Bearer", access_token=new_access, refresh_token=refresh_token)

    def refresh_refresh(self, refresh_token: str) -> JwtResponse | None:
        if not self._jwt_provider.validate_refresh_token(refresh_token):
            return None

        user_id_str = self._jwt_provider.get_uuid_from_token(refresh_token)

        if user_id_str is None:
            return None

        user_ds = self._user_service.get_by_id(user_id_str)

        if user_ds is None:
            return None
        else:
            user               = User(login=user_ds.login)
            user.id            = uuid.UUID(user_ds.id)
            user.password_hash = user_ds.password_hash

            new_access  = self._jwt_provider.generate_access_token(user)
            new_refresh = self._jwt_provider.generate_refresh_token(user)

            return JwtResponse(type="Bearer", access_token=new_access, refresh_token=new_refresh)

    def get_user_id_from_access(self, access_token: str) -> uuid.UUID | None:
        if not self._jwt_provider.validate_access_token(access_token):
            return None

        user_id_str = self._jwt_provider.get_uuid_from_token(access_token)

        if user_id_str is None:
            return None
        else:
            return uuid.UUID(user_id_str)
