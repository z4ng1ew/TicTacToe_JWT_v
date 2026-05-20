from dataclasses import dataclass


@dataclass
class RefreshJwtRequest:
    refresh_token: str
