import uuid

from domain.model.game               import Game
from domain.model.game_board         import GameBoard
from domain.model.game_state         import GameState
from domain.model.user               import User
from domain.model.leaderboard_entry  import LeaderboardEntry
from domain.service.game_service_interface import GameServiceInterface
from domain.service                  import game_logic
from datasource.repository.game_repository import GameRepository
from datasource.repository.user_repository import UserRepository
from datasource.mapper.game_mapper         import GameMapper
from datasource.mapper.user_mapper         import UserMapper


class GameServiceImpl(GameServiceInterface):

    def __init__(
        self,
        game_repository: GameRepository,
        user_repository: UserRepository,
        game_mapper:     GameMapper,
        user_mapper:     UserMapper,
    ) -> None:
        self._game_repository = game_repository
        self._user_repository = user_repository
        self._game_mapper     = game_mapper
        self._user_mapper     = user_mapper

    def get_next_move(self, game: Game) -> tuple[int, int]:
        return game_logic.find_best_move(game.board)

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        return game_logic.validate_board(game.board, previous_board)

    def is_game_over(self, game: Game) -> bool:
        return game_logic.is_game_over(game.board)

    def create_game(self, player_id: uuid.UUID, opponent_type: str = "computer") -> Game:
        game               = Game()
        game.player_x_id   = player_id
        game.opponent_type = opponent_type

        if opponent_type == "computer":
            game.state        = GameState.TURN
            game.current_turn = player_id
        else:
            game.state = GameState.WAITING

        self._game_repository.save(self._game_mapper.domain_to_ds(game))

        return game

    def get_available_games(self) -> list[Game]:
        return [
            self._game_mapper.ds_to_domain(game_ds)
            for game_ds in self._game_repository.get_all_waiting()
        ]

    def join_game(self, game_id: str, player_id: uuid.UUID) -> Game | None:
        game_ds = self._game_repository.get_by_id(game_id)

        if game_ds is None:
            return None

        game = self._game_mapper.ds_to_domain(game_ds)

        if game.state != GameState.WAITING:
            return None
        elif game.player_x_id == player_id:
            return None
        else:
            game.player_o_id  = player_id
            game.state        = GameState.TURN
            game.current_turn = game.player_x_id

            self._game_repository.save(self._game_mapper.domain_to_ds(game))

            return game

    def get_game(self, game_id: str) -> Game | None:
        game_ds = self._game_repository.get_by_id(game_id)

        if game_ds is None:
            return None
        else:
            return self._game_mapper.ds_to_domain(game_ds)

    def get_user(self, user_id: str) -> User | None:
        user_ds = self._user_repository.get_by_id(user_id)

        if user_ds is None:
            return None
        else:
            return self._user_mapper.ds_to_domain(user_ds)

    def make_move(
        self,
        game_id:   str,
        player_id: uuid.UUID,
        row:       int,
        col:       int,
    ) -> Game | None:
        game_ds = self._game_repository.get_by_id(game_id)

        if game_ds is None:
            return None

        game = self._game_mapper.ds_to_domain(game_ds)

        if game.state != GameState.TURN:
            return None
        elif game.current_turn != player_id:
            return None
        elif game.board.matrix[row][col] != 0:
            return None
        else:
            symbol = 1 if game.player_x_id == player_id else 2
            game.board.matrix[row][col] = symbol
            game = self._update_state(game, last_player_id=player_id)

            if game.state == GameState.TURN and game.opponent_type == "computer":
                game = self._make_computer_move(game)

            self._game_repository.save(self._game_mapper.domain_to_ds(game))

            return game

    def get_finished_games_by_user(self, user_id: str) -> list[Game]:
        return [
            self._game_mapper.ds_to_domain(game_ds)
            for game_ds in self._game_repository.get_finished_by_user(user_id)
        ]

    def get_leaderboard(self, top_n: int) -> list[LeaderboardEntry]:
        rows = self._game_repository.get_leaderboard(top_n)

        return [
            LeaderboardEntry(
                user_id   = row["user_id"],
                login     = row["login"],
                wins      = int(row["wins"]),
                losses    = int(row["losses"]),
                draws     = int(row["draws"]),
                win_ratio = float(row["win_ratio"]),
            )
            for row in rows
        ]

    def _update_state(self, game: Game, last_player_id: uuid.UUID) -> Game:
        if self.is_game_over(game):
            winner_symbol = game_logic.check_winner(game.board.matrix)

            if winner_symbol == 0:
                game.state = GameState.DRAW
            elif winner_symbol == 1:
                game.state        = GameState.WIN
                game.current_turn = game.player_x_id
            else:
                game.state        = GameState.WIN
                game.current_turn = game.player_o_id
        else:
            game.state = GameState.TURN

            if last_player_id == game.player_x_id:
                game.current_turn = game.player_o_id
            else:
                game.current_turn = game.player_x_id

        return game

    def _make_computer_move(self, game: Game) -> Game:
        row, col = self.get_next_move(game)

        if row != -1 and game.board.matrix[row][col] == 0:
            game.board.matrix[row][col] = 2

        computer_id = game.player_o_id if game.player_o_id is not None else uuid.uuid4()

        return self._update_state(game, last_player_id=computer_id)
