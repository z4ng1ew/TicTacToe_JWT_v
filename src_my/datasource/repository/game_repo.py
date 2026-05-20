from datetime import datetime, timedelta
from typing import Optional

from datasource.database import db
from datasource.model.game_ds import GameDS


class GameRepository:

    def save(self, game: GameDS) -> None:
        db.session.merge(game)
        db.session.commit()

    def get_by_id(self, game_id: str) -> Optional[GameDS]:
        return db.session.get(GameDS, game_id)

    def get_all_waiting(self) -> list[GameDS]:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        return GameDS.query.filter(
            GameDS.state      == 'waiting',
            GameDS.created_at >= one_hour_ago,
        ).all()