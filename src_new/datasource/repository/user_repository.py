from datasource.database      import db
from datasource.model.user_ds import UserDS


class UserRepository:

    def save(self, user_ds: UserDS) -> None:
        db.session.add(user_ds)
        db.session.commit()

    def get_by_id(self, user_id: str) -> UserDS | None:
        return db.session.get(UserDS, user_id)

    def get_by_login(self, login: str) -> UserDS | None:
        return UserDS.query.filter_by(login=login).first()
