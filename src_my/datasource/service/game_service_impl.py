import uuid
from typing import Optional

from domain.service.impl import GameServiceImpl, check_winner
from domain.model.game import Game
from domain.model.game_board import GameBoard
from domain.model.game_state import GameState
from domain.model.user import User
from datasource.repository.game_repo import GameRepository
from datasource.repository.user_repo import UserRepository
from datasource.mapper.mapper import GameMapper, UserMapper


class GameServiceImplWithRepo(GameServiceImpl):

    def __init__(
        self,
        repository: GameRepository,
        mapper:     GameMapper,
        user_repo:  UserRepository,
    ):
        super().__init__()
        self._repo      = repository
        self._mapper    = mapper
        self._user_repo = user_repo

    def create_game(
        self,
        player_id:     uuid.UUID,
        opponent_type: str = 'computer',
    ) -> Game:
        game               = Game()
        game.player_x_id   = player_id
        game.opponent_type = opponent_type

        if opponent_type == 'computer':
            game.state        = GameState.TURN
            game.current_turn = player_id
        else:
            game.state = GameState.WAITING

        self._repo.save(self._mapper.domain_to_ds(game))

        return game

    def get_available_games(self) -> list[Game]:
        return [
            self._mapper.ds_to_domain(ds)
            for ds in self._repo.get_all_waiting()
        ]

    def join_game(
        self,
        game_id:   str,
        player_id: uuid.UUID,
    ) -> Optional[Game]:
        game_ds = self._repo.get_by_id(game_id)

        if game_ds is None:
            return None
        else:
            game = self._mapper.ds_to_domain(game_ds)

            if game.state != GameState.WAITING:
                return None
            elif game.player_x_id == player_id:
                return None
            else:
                game.player_o_id  = player_id
                game.state        = GameState.TURN
                game.current_turn = game.player_x_id

                self._repo.save(self._mapper.domain_to_ds(game))

                return game

    def get_game(self, game_id: str) -> Optional[Game]:
        game_ds = self._repo.get_by_id(game_id)

        if game_ds is None:
            return None
        else:
            return self._mapper.ds_to_domain(game_ds)

    def get_user(self, user_id: str) -> Optional[User]:
        user_ds = self._user_repo.get_by_id(user_id)

        if user_ds is None:
            return None
        else:
            return UserMapper().ds_to_domain(user_ds)

    def make_move(
        self,
        game_id:   str,
        player_id: uuid.UUID,
        row:       int,
        col:       int,
    ) -> Optional[Game]:
        game_ds = self._repo.get_by_id(game_id)

        if game_ds is None:
            return None
        else:
            game = self._mapper.ds_to_domain(game_ds)

            if game.state != GameState.TURN:
                return None
            elif game.current_turn != player_id:
                return None
            elif game.board.matrix[row][col] != 0:
                return None
            else:
                symbol                      = 1 if game.player_x_id == player_id else 2
                game.board.matrix[row][col] = symbol
                game                        = self._update_state(game, player_id)

                if game.state == GameState.TURN and game.opponent_type == 'computer':
                    game = self._computer_move(game)

                self._repo.save(self._mapper.domain_to_ds(game))

                return game

    def _update_state(self, game: Game, last_player_id: uuid.UUID) -> Game:
        if self.is_game_over(game):
            winner_symbol = check_winner(game.board.matrix)

            if winner_symbol == 0:
                game.state = GameState.DRAW
            else:
                game.state        = GameState.WIN
                game.current_turn = (
                    game.player_x_id if winner_symbol == 1
                    else game.player_o_id
                )
        else:
            game.state        = GameState.TURN
            game.current_turn = (
                game.player_o_id if last_player_id == game.player_x_id
                else game.player_x_id
            )

        return game

    def _computer_move(self, game: Game) -> Game:
        r, c = self.get_next_move(game)

        if r != -1 and game.board.matrix[r][c] == 0:
            game.board.matrix[r][c] = 2

        game = self._update_state(game, game.player_o_id or uuid.uuid4())

        return game

    def save_game_state(self, game: Game) -> None:
        self._repo.save(self._mapper.domain_to_ds(game))

    def get_previous_board(self, game_id: str) -> Optional[GameBoard]:
        game_ds = self._repo.get_by_id(str(game_id))

        if game_ds is None:
            return None
        else:
            return self._mapper.ds_to_domain(game_ds).board