import json
import uuid

from domain.model.game        import Game
from domain.model.game_board  import GameBoard
from domain.model.game_state  import GameState
from datasource.model.game_ds import GameDS


class GameMapper:

    @staticmethod
    def domain_to_ds(game: Game) -> GameDS:
        return GameDS(
            id            = str(game.id),
            state         = game.state.value,
            player_x_id   = str(game.player_x_id)  if game.player_x_id  is not None else None,
            player_o_id   = str(game.player_o_id)  if game.player_o_id  is not None else None,
            current_turn  = str(game.current_turn) if game.current_turn is not None else None,
            opponent_type = game.opponent_type,
            board_json    = json.dumps(game.board.matrix),
        )

    @staticmethod
    def ds_to_domain(game_ds: GameDS) -> Game:
        board = GameBoard(matrix=json.loads(game_ds.board_json))
        game  = Game(board=board)

        game.id            = uuid.UUID(game_ds.id)
        game.state         = GameState(game_ds.state)
        game.player_x_id   = uuid.UUID(game_ds.player_x_id)  if game_ds.player_x_id  is not None else None
        game.player_o_id   = uuid.UUID(game_ds.player_o_id)  if game_ds.player_o_id  is not None else None
        game.current_turn  = uuid.UUID(game_ds.current_turn) if game_ds.current_turn is not None else None
        game.opponent_type = game_ds.opponent_type

        return game
