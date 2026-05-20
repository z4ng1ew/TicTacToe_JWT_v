import uuid

class User:
    def __init__(self, login: str, password: str):
        self.id       = uuid.uuid4()
        self.login    = login
        self.password = password
        self.password_hash = ''  