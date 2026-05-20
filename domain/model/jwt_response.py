from dataclasses import dataclass


@dataclass
class JwtResponse:
    type:          str
    access_token:  str
    refresh_token: str

    def to_dict(self) -> dict:
        return {
            "type":         self.type,
            "accessToken":  self.access_token,
            "refreshToken": self.refresh_token,
        }
