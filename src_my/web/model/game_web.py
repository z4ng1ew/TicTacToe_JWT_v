from dataclasses import dataclass
from typing import Optional
from web.model.game_board_web import GameBoardWeb


@dataclass
class GameWeb:
    id:            str
    board:         GameBoardWeb
    state:         str
    opponent_type: str
    player_x_id:   Optional[str]
    player_o_id:   Optional[str]
    current_turn:  Optional[str]

    def to_dict(self) -> dict:
        return {
            'id':            self.id,
            'state':         self.state,
            'opponent_type': self.opponent_type,
            'player_x_id':   self.player_x_id,
            'player_o_id':   self.player_o_id,
            'current_turn':  self.current_turn,
            'board': {
                'matrix': self.board.matrix,
                'size':   self.board.size,
            },
        }