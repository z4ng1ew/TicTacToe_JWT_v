import uuid
from typing import Optional

from datasource.repository.user_repo import UserRepository
from datasource.model.user_ds import UserDS


class UserService:

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def get_by_login(self, login: str) -> Optional[UserDS]:
        return self._user_repo.get_by_login(login)

    def get_by_id(self, user_id: str) -> Optional[UserDS]:
        return self._user_repo.get_by_id(user_id)

    def save(self, user_ds: UserDS) -> None:
        self._user_repo.save(user_ds)