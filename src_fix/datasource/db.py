from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/tictactoe_db"
engine: Engine = create_engine(DATABASE_URL, echo=False)
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_session() -> Session:
    return SessionFactory()


def init_db() -> None:
    from datasource.model import game_db, user_db
    _ = (game_db, user_db)
    Base.metadata.create_all(bind=engine)
