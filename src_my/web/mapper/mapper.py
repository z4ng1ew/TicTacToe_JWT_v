from domain.model.game import Game
from domain.model.game_board import GameBoard
from web.model.game_web import GameWeb
from web.model.game_board_web import GameBoardWeb


class GameWebMapper:

    @staticmethod
    def domain_to_web(game: Game) -> GameWeb:

        board_web = GameBoardWeb(
            matrix = game.board.matrix.copy(),
            size   = game.board.size,
        )

        return GameWeb(
            id           = str(game.id),
            board        = board_web,
            state        = game.state.value,
            opponent_type = game.opponent_type,
            player_x_id  = str(game.player_x_id) if game.player_x_id else None,
            player_o_id  = str(game.player_o_id) if game.player_o_id else None,
            current_turn = str(game.current_turn) if game.current_turn else None,
        )