import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from datasource.db import Base


class UserDB(Base):
    __tablename__: str = "users"
    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
