from datetime import datetime

from sqlalchemy     import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datasource.database import db


class GameDS(db.Model):
    __tablename__ = "games"

    id:            Mapped[str]              = mapped_column(String(36),  primary_key=True)
    state:         Mapped[str]              = mapped_column(String(16),  nullable=False, default="waiting")
    player_x_id:   Mapped[str | None]       = mapped_column(String(36),  nullable=True)
    player_o_id:   Mapped[str | None]       = mapped_column(String(36),  nullable=True)
    current_turn:  Mapped[str | None]       = mapped_column(String(36),  nullable=True)
    opponent_type: Mapped[str]              = mapped_column(String(8),   nullable=False, default="computer")
    board_json:    Mapped[str]              = mapped_column(Text,        nullable=False, default="[]")
    created_at:    Mapped[datetime]         = mapped_column(DateTime,    nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<GameDS id={self.id} state={self.state}>"
