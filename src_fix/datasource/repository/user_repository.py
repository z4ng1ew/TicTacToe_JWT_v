from typing import Optional
from sqlalchemy.orm import Session
from datasource.db import get_session
from datasource.model.user_db import UserDB


class UserRepository:
    def save_user(self, user_id: str, login: str, password_hash: str) -> None:
        db_session: Session = get_session()
        try:
            new_user: UserDB = UserDB(user_id=user_id, login=login, password_hash=password_hash)
            db_session.add(new_user)
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise
        finally:
            db_session.close()

    def find_by_login(self, login: str) -> Optional[UserDB]:
        db_session: Session = get_session()
        try:
            record: Optional[UserDB] = db_session.query(UserDB).filter_by(login=login).first()
            return record
        finally:
            db_session.close()

    def find_by_id(self, user_id: str) -> Optional[UserDB]:
        db_session: Session = get_session()
        try:
            record: Optional[UserDB] = db_session.query(UserDB).filter_by(user_id=user_id).first()
            return record
        finally:
            db_session.close()
