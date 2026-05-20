from dataclasses import dataclass
from typing import List


@dataclass
class FieldView:
    grid: List[List[int]]
    side_length: int = 3
