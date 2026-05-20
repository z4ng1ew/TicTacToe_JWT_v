from domain.model.game_board import GameBoard


WINNING_LINES: list[list[tuple[int, int]]] = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)],
]


def check_winner(matrix: list[list[int]]) -> int:
    for line in WINNING_LINES:
        cells = [matrix[r][c] for r, c in line]

        if cells[0] != 0 and cells[0] == cells[1] == cells[2]:
            return cells[0]

    return 0


def is_board_full(matrix: list[list[int]]) -> bool:
    return all(cell != 0 for row in matrix for cell in row)


def is_game_over(board: GameBoard) -> bool:
    if check_winner(board.matrix) != 0:
        return True
    elif is_board_full(board.matrix):
        return True
    else:
        return False


def validate_board(current: GameBoard, previous: GameBoard) -> bool:
    if current.size != previous.size:
        return False

    diff_count = 0

    for r in range(current.size):
        for c in range(current.size):
            if current.matrix[r][c] != previous.matrix[r][c]:
                diff_count += 1

    return diff_count == 1


def find_best_move(board: GameBoard) -> tuple[int, int]:
    matrix     = [row[:] for row in board.matrix]
    best_score = float("-inf")
    best_move  = (-1, -1)

    for r in range(board.size):
        for c in range(board.size):
            if matrix[r][c] == 0:
                matrix[r][c] = 2
                score        = _minimax(matrix, depth=0, is_maximizing=False)
                matrix[r][c] = 0

                if score > best_score:
                    best_score = score
                    best_move  = (r, c)

    return best_move


def _minimax(matrix: list[list[int]], depth: int, is_maximizing: bool) -> int:
    winner = check_winner(matrix)

    if winner == 2:
        return 10 - depth
    elif winner == 1:
        return depth - 10
    elif is_board_full(matrix):
        return 0
    elif is_maximizing:
        best = -1000

        for r in range(3):
            for c in range(3):
                if matrix[r][c] == 0:
                    matrix[r][c] = 2
                    score        = _minimax(matrix, depth + 1, False)
                    matrix[r][c] = 0

                    if score > best:
                        best = score

        return best
    else:
        best = 1000

        for r in range(3):
            for c in range(3):
                if matrix[r][c] == 0:
                    matrix[r][c] = 1
                    score        = _minimax(matrix, depth + 1, True)
                    matrix[r][c] = 0

                    if score < best:
                        best = score

        return best
