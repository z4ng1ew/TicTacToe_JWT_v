from datetime import datetime
from datasource.database import db


class GameDS(db.Model):
    __tablename__ = 'games'

    id:            str      = db.Column(db.String(36),  primary_key=True)
    state:         str      = db.Column(db.String(16),  nullable=False, default='waiting')
    player_x_id:   str      = db.Column(db.String(36),  nullable=True)
    player_o_id:   str      = db.Column(db.String(36),  nullable=True)
    current_turn:  str      = db.Column(db.String(36),  nullable=True)
    opponent_type: str      = db.Column(db.String(8),   nullable=False, default='computer')
    board_json:    str      = db.Column(db.Text,        nullable=False, default='[]')
    created_at:    datetime = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<GameDS id={self.id} state={self.state}>'