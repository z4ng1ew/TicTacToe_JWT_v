from typing import List, Tuple
from domain.model.board import GameField
from domain.model.game import GameState, MatchSession


class AiEngine:
    def calculate_ai_turn(self, session: MatchSession) -> Tuple[int, int]:
        grid: List[List[int]] = [row.copy() for row in session.field.grid]
        top_score: float = float("-inf")
        best_cell: Tuple[int, int] = (-1, -1)

        for r in range(session.field.side_length):
            for c in range(session.field.side_length):
                if grid[r][c] == 0:
                    grid[r][c] = 2
                    score: int = self._run_minimax(grid, depth=0, is_max=False)
                    grid[r][c] = 0
                    if score > top_score:
                        top_score = score
                        best_cell = (r, c)
                    else:
                        continue
                else:
                    continue
        return best_cell

    def check_board_changes(self, current: MatchSession, previous: GameField) -> bool:
        if current.field.side_length != previous.side_length:
            return False
        else:
            change_count: int = 0
            for r in range(current.field.side_length):
                for c in range(current.field.side_length):
                    if current.field.grid[r][c] != previous.grid[r][c]:
                        change_count += 1
                    else:
                        continue
            if change_count == 1:
                return True
            else:
                return False

    def verify_end_state(self, session: MatchSession) -> bool:
        winner_code: int = self._find_winner(session.field.grid)
        if winner_code != 0:
            return True
        elif all(cell != 0 for row in session.field.grid for cell in row):
            return True
        else:
            return False

    def update_game_state(self, session: MatchSession) -> None:
        winner: int = self._find_winner(session.field.grid)
        if winner == 1:
            session.state = GameState.WIN_X
        elif winner == 2:
            session.state = GameState.WIN_O
        elif all(cell != 0 for row in session.field.grid for cell in row):
            session.state = GameState.DRAW
        elif session.state == GameState.PLAYER_X_TURN:
            session.state = GameState.PLAYER_O_TURN
        elif session.state == GameState.PLAYER_O_TURN:
            session.state = GameState.PLAYER_X_TURN
        else:
            session.state = GameState.PLAYER_X_TURN

    def _run_minimax(self, grid: List[List[int]], depth: int, is_max: bool) -> int:
        winner_code: int = self._find_winner(grid)
        if winner_code == 2:
            return 10 - depth
        elif winner_code == 1:
            return depth - 10
        elif all(cell != 0 for row in grid for cell in row):
            return 0
        elif is_max:
            best_max: int = -1000
            for r in range(3):
                for c in range(3):
                    if grid[r][c] == 0:
                        grid[r][c] = 2
                        score: int = self._run_minimax(grid, depth + 1, False)
                        grid[r][c] = 0
                        if score > best_max:
                            best_max = score
                        else:
                            continue
                    else:
                        continue
            return best_max
        else:
            best_min: int = 1000
            for r in range(3):
                for c in range(3):
                    if grid[r][c] == 0:
                        grid[r][c] = 1
                        score = self._run_minimax(grid, depth + 1, True)
                        grid[r][c] = 0
                        if score < best_min:
                            best_min = score
                        else:
                            continue
                    else:
                        continue
            return best_min

    @staticmethod
    def _find_winner(grid: List[List[int]]) -> int:
        lines: List[List[Tuple[int, int]]] = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]
        for line in lines:
            cells: List[int] = [grid[r][c] for r, c in line]
            if cells[0] != 0 and cells[0] == cells[1] == cells[2]:
                return cells[0]
            else:
                continue
        return 0
