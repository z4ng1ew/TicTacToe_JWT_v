from datasource.model.user_ds          import UserDS
from datasource.repository.user_repository import UserRepository


class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def get_by_login(self, login: str) -> UserDS | None:
        return self._user_repository.get_by_login(login)

    def get_by_id(self, user_id: str) -> UserDS | None:
        return self._user_repository.get_by_id(user_id)

    def save(self, user_ds: UserDS) -> None:
        self._user_repository.save(user_ds)
