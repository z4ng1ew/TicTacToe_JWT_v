from typing import Optional
from datasource.database import db
from datasource.model.user_ds import UserDS


class UserRepository:

    def save(self, user: UserDS) -> None:
        db.session.add(user)
        db.session.commit()

    def get_by_id(self, user_id: str) -> Optional[UserDS]:
        return db.session.get(UserDS, user_id)

    def get_by_login(self, login: str) -> Optional[UserDS]:
        return UserDS.query.filter_by(login=login).first()