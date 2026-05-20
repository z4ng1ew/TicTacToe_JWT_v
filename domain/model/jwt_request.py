from dataclasses import dataclass


@dataclass
class JwtRequest:
    login:    str
    password: str
