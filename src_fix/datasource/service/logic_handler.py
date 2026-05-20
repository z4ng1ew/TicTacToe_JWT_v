from typing import Any, Dict, Optional
from datasource.repository.game_repository import GameRepository
from domain.model.board import GameField
from domain.model.game import MatchSession
from domain.service.ai_engine import AiEngine


class LogicWithArchive(AiEngine):
    def __init__(self, repository: GameRepository) -> None:
        super().__init__()
        self._repository: GameRepository = repository

    def save_match_state(self, session: MatchSession) -> None:
        self._repository.save_match(
            session_id=str(session.session_id),
            grid=session.field.grid,
            side_length=session.field.side_length,
            state=session.state.value,
            player_x_id=session.player_x_id,
            player_o_id=session.player_o_id,
            mode=session.mode,
        )

    def load_previous_field(self, session_id: Any) -> Optional[GameField]:
        data_record: Optional[Dict[str, Any]] = self._repository.load_match(str(session_id))
        if data_record is not None:
            return GameField(
                grid=data_record["grid"],
                side_length=data_record["side_length"],
            )
        else:
            return None
