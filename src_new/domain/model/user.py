import uuid


class User:

    def __init__(self, login: str, password_hash: str = "") -> None:
        self.id:            uuid.UUID = uuid.uuid4()
        self.login:         str       = login
        self.password_hash: str       = password_hash
