import uuid
from typing import Optional
from werkzeug.security import check_password_hash, generate_password_hash
from datasource.model.user_db import UserDB
from datasource.repository.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository: UserRepository = repository

    def create_user(self, login: str, raw_password: str) -> bool:
        existing: Optional[UserDB] = self._repository.find_by_login(login)
        if existing is not None:
            return False
        else:
            new_id: str = str(uuid.uuid4())
            hashed: str = generate_password_hash(raw_password)
            self._repository.save_user(new_id, login, hashed)
            return True

    def verify_credentials(self, login: str, raw_password: str) -> Optional[str]:
        record: Optional[UserDB] = self._repository.find_by_login(login)
        if record is None:
            return None
        elif check_password_hash(record.password_hash, raw_password):
            return record.user_id
        else:
            return None

    def find_by_id(self, user_id: str) -> Optional[UserDB]:
        return self._repository.find_by_id(user_id)
