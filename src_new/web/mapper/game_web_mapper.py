from domain.model.game        import Game
from web.model.game_web       import GameWeb
from web.model.game_board_web import GameBoardWeb


class GameWebMapper:

    @staticmethod
    def domain_to_web(game: Game) -> GameWeb:
        board_web = GameBoardWeb(
            matrix = [row[:] for row in game.board.matrix],
            size   = game.board.size,
        )

        return GameWeb(
            id            = str(game.id),
            board         = board_web,
            state         = game.state.value,
            opponent_type = game.opponent_type,
            player_x_id   = str(game.player_x_id)  if game.player_x_id  is not None else None,
            player_o_id   = str(game.player_o_id)  if game.player_o_id  is not None else None,
            current_turn  = str(game.current_turn) if game.current_turn is not None else None,
        )
