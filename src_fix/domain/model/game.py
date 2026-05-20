import uuid
from enum import Enum
from typing import Optional
from domain.model.board import GameField


class GameState(Enum):
    WAITING = "waiting"
    PLAYER_X_TURN = "player_x_turn"
    PLAYER_O_TURN = "player_o_turn"
    DRAW = "draw"
    WIN_X = "win_x"
    WIN_O = "win_o"


class MatchSession:
    def __init__(
        self,
        current_field: Optional[GameField] = None,
        player_x_id: Optional[str] = None,
        player_o_id: Optional[str] = None,
        state: GameState = GameState.WAITING,
        mode: str = "pve",
        session_id: Optional[uuid.UUID] = None,
    ) -> None:
        self.session_id: uuid.UUID = session_id if session_id is not None else uuid.uuid4()
        self.field: GameField = current_field if current_field is not None else GameField()
        self.player_x_id: Optional[str] = player_x_id
        self.player_o_id: Optional[str] = player_o_id
        self.state: GameState = state
        self.mode: str = mode

    def get_current_player_id(self) -> Optional[str]:
        if self.state == GameState.PLAYER_X_TURN:
            return self.player_x_id
        elif self.state == GameState.PLAYER_O_TURN:
            return self.player_o_id
        else:
            return None

    def get_symbol_for_player(self, player_id: str) -> Optional[int]:
        if player_id == self.player_x_id:
            return 1
        elif player_id == self.player_o_id:
            return 2
        else:
            return None
