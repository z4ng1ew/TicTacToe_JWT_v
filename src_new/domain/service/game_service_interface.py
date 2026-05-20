import uuid
from abc import ABC, abstractmethod

from domain.model.game        import Game
from domain.model.game_board  import GameBoard
from domain.model.user        import User


class GameServiceInterface(ABC):

    @abstractmethod
    def get_next_move(self, game: Game) -> tuple[int, int]:
        pass

    @abstractmethod
    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        pass

    @abstractmethod
    def is_game_over(self, game: Game) -> bool:
        pass

    @abstractmethod
    def create_game(self, player_id: uuid.UUID, opponent_type: str) -> Game:
        pass

    @abstractmethod
    def get_available_games(self) -> list[Game]:
        pass

    @abstractmethod
    def join_game(self, game_id: str, player_id: uuid.UUID) -> Game | None:
        pass

    @abstractmethod
    def get_game(self, game_id: str) -> Game | None:
        pass

    @abstractmethod
    def make_move(self, game_id: str, player_id: uuid.UUID, row: int, col: int) -> Game | None:
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> User | None:
        pass
