import json
import uuid

from domain.model.game import Game
from domain.model.game_board import GameBoard
from domain.model.game_state import GameState
from datasource.model.game_ds import GameDS
from datasource.model.user_ds import UserDS
from domain.model.user import User


class GameMapper:

    @staticmethod
    def domain_to_ds(game: Game) -> GameDS:

        return GameDS(
            id            = str(game.id),
            state         = game.state.value,
            player_x_id   = str(game.player_x_id) if game.player_x_id else None,
            player_o_id   = str(game.player_o_id) if game.player_o_id else None,
            current_turn  = str(game.current_turn) if game.current_turn else None,
            opponent_type = game.opponent_type,
            board_json    = json.dumps(game.board.matrix),
        )

    @staticmethod
    def ds_to_domain(ds: GameDS) -> Game:

        board = GameBoard(matrix=json.loads(ds.board_json))
        game  = Game(board=board)

        game.id            = uuid.UUID(ds.id)
        game.state         = GameState(ds.state)
        game.player_x_id   = uuid.UUID(ds.player_x_id) if ds.player_x_id else None
        game.player_o_id   = uuid.UUID(ds.player_o_id) if ds.player_o_id else None
        game.current_turn  = uuid.UUID(ds.current_turn) if ds.current_turn else None
        game.opponent_type = ds.opponent_type

        return game


class UserMapper:

    @staticmethod
    def domain_to_ds(user: User) -> UserDS:

        return UserDS(
            id            = str(user.id),
            login         = user.login,
            password_hash = user.password_hash,
        )

    @staticmethod
    def ds_to_domain(ds: UserDS) -> User:

        user               = User(login=ds.login, password='')
        user.id            = uuid.UUID(ds.id)
        user.password_hash = ds.password_hash

        return user