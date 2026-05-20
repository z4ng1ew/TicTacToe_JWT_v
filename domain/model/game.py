import uuid

from domain.model.game_board import GameBoard
from domain.model.game_state import GameState


class Game:

    def __init__(self, board: GameBoard | None = None) -> None:
        self.id:            uuid.UUID         = uuid.uuid4()
        self.board:         GameBoard         = board if board is not None else GameBoard()
        self.state:         GameState         = GameState.WAITING
        self.player_x_id:   uuid.UUID | None  = None
        self.player_o_id:   uuid.UUID | None  = None
        self.current_turn:  uuid.UUID | None  = None
        self.opponent_type: str               = "computer"
