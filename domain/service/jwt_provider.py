from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token

from domain.model.user import User


class JwtProvider:

    def __init__(
        self,
        access_ttl_minutes: int = 60,
        refresh_ttl_days:   int = 7,
    ) -> None:
        self._access_ttl  = timedelta(minutes=access_ttl_minutes)
        self._refresh_ttl = timedelta(days=refresh_ttl_days)

    def generate_access_token(self, user: User) -> str:
        return create_access_token(
            identity      = str(user.id),
            expires_delta = self._access_ttl,
        )

    def generate_refresh_token(self, user: User) -> str:
        return create_refresh_token(
            identity      = str(user.id),
            expires_delta = self._refresh_ttl,
        )

    def validate_access_token(self, token: str) -> bool:
        try:
            payload = decode_token(token)
        except Exception:
            return False

        if payload.get("type") != "access":
            return False
        else:
            return True

    def validate_refresh_token(self, token: str) -> bool:
        try:
            payload = decode_token(token)
        except Exception:
            return False

        if payload.get("type") != "refresh":
            return False
        else:
            return True

    def get_uuid_from_token(self, token: str) -> str | None:
        try:
            payload = decode_token(token)
        except Exception:
            return None

        return payload.get("sub")
