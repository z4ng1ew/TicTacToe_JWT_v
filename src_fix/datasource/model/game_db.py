import json
from typing import List, Optional
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from datasource.db import Base


class GameSessionDB(Base):
    __tablename__: str = "game_sessions"
    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    side_length: Mapped[int] = mapped_column(Integer, default=3)
    grid_json: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String, default="waiting")
    player_x_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    player_o_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    mode: Mapped[str] = mapped_column(String, default="pve")

    def to_grid(self) -> List[List[int]]:
        return json.loads(self.grid_json)
