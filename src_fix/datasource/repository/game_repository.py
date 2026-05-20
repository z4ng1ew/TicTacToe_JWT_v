import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datasource.db import get_session
from datasource.model.game_db import GameSessionDB


class GameRepository:
    def save_match(
        self,
        session_id: str,
        grid: List[List[int]],
        side_length: int,
        state: str = "waiting",
        player_x_id: Optional[str] = None,
        player_o_id: Optional[str] = None,
        mode: str = "pve",
    ) -> None:
        db_session: Session = get_session()
        try:
            existing: Optional[GameSessionDB] = (
                db_session.query(GameSessionDB).filter_by(session_id=session_id).first()
            )
            if existing is not None:
                existing.side_length = side_length
                existing.grid_json = json.dumps(grid)
                existing.state = state
                existing.player_x_id = player_x_id
                existing.player_o_id = player_o_id
                existing.mode = mode
            else:
                new_record: GameSessionDB = GameSessionDB(
                    session_id=session_id,
                    side_length=side_length,
                    grid_json=json.dumps(grid),
                    state=state,
                    player_x_id=player_x_id,
                    player_o_id=player_o_id,
                    mode=mode,
                )
                db_session.add(new_record)
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise
        finally:
            db_session.close()

    def load_match(self, session_id: str) -> Optional[Dict[str, Any]]:
        db_session: Session = get_session()
        try:
            record: Optional[GameSessionDB] = (
                db_session.query(GameSessionDB).filter_by(session_id=session_id).first()
            )
            if record is not None:
                return {
                    "session_id": record.session_id,
                    "side_length": record.side_length,
                    "grid": record.to_grid(),
                    "state": record.state,
                    "player_x_id": record.player_x_id,
                    "player_o_id": record.player_o_id,
                    "mode": record.mode,
                }
            else:
                return None
        finally:
            db_session.close()

    def find_waiting_games(self) -> List[Dict[str, Any]]:
        db_session: Session = get_session()
        try:
            records: List[GameSessionDB] = (
                db_session.query(GameSessionDB).filter_by(state="waiting", mode="pvp").all()
            )
            return [
                {
                    "id": r.session_id,
                    "session_id": r.session_id,
                    "player_x_id": r.player_x_id,
                }
                for r in records
            ]
        finally:
            db_session.close()

    def join_game(self, session_id: str, player_id: str) -> bool:
        db_session: Session = get_session()
        try:
            record: Optional[GameSessionDB] = (
                db_session.query(GameSessionDB).filter_by(session_id=session_id).first()
            )
            if record is None:
                return False
            elif record.state != "waiting":
                return False
            elif record.mode != "pvp":
                return False
            elif record.player_x_id is None:
                record.player_x_id = player_id
                record.state = "player_x_turn"
                db_session.commit()
                return True
            elif record.player_o_id is None and record.player_x_id != player_id:
                record.player_o_id = player_id
                record.state = "player_x_turn"
                db_session.commit()
                return True
            else:
                return False
        except Exception:
            db_session.rollback()
            raise
        finally:
            db_session.close()
