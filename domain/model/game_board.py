class GameBoard:

    def __init__(self, matrix: list[list[int]] | None = None, size: int = 3) -> None:
        if matrix is None:
            self.matrix: list[list[int]] = [[0] * size for _ in range(size)]
        else:
            self.matrix = [row[:] for row in matrix]

        self.size: int = len(self.matrix)

    def copy(self) -> "GameBoard":
        return GameBoard(matrix=self.matrix)
