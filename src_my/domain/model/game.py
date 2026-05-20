import uuid
from domain.model.game_board import GameBoard
from domain.model.game_state import GameState

class Game:
    def __init__(self, board: GameBoard | None = None):
        self.id            = uuid.uuid4()
        self.board         = board or GameBoard()
        self.state         = GameState.WAITING  
        self.player_x_id   = None   
        self.player_o_id   = None   
        self.current_turn  = None   
        self.opponent_type = "computer"  