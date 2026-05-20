from sqlalchemy     import String
from sqlalchemy.orm import Mapped, mapped_column

from datasource.database import db


class UserDS(db.Model):
    __tablename__ = "users"

    id:            Mapped[str] = mapped_column(String(36),  primary_key=True)
    login:         Mapped[str] = mapped_column(String(64),  nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    def __repr__(self) -> str:
        return f"<UserDS id={self.id} login={self.login}>"
