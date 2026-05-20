from typing import List, Optional


class GameField:
    def __init__(self, grid: Optional[List[List[int]]] = None, side_length: int = 3) -> None:
        if grid is None:
            self.grid: List[List[int]] = [[0 for _ in range(side_length)] for _ in range(side_length)]
        else:
            self.grid = [row.copy() for row in grid]
        self.side_length: int = len(self.grid)
