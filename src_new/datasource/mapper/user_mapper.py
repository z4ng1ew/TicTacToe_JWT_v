import uuid

from domain.model.user        import User
from datasource.model.user_ds import UserDS


class UserMapper:

    @staticmethod
    def domain_to_ds(user: User) -> UserDS:
        return UserDS(
            id            = str(user.id),
            login         = user.login,
            password_hash = user.password_hash,
        )

    @staticmethod
    def ds_to_domain(user_ds: UserDS) -> User:
        user               = User(login=user_ds.login)
        user.id            = uuid.UUID(user_ds.id)
        user.password_hash = user_ds.password_hash

        return user
