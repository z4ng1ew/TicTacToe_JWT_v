from dataclasses import dataclass
from typing import Any, Dict, Union
from web.model.board_view import FieldView


@dataclass
class SessionView:
    id: str
    board: Union[FieldView, Dict[str, Any]]

    def to_json_dict(self) -> Dict[str, Any]:
        if isinstance(self.board, FieldView):
            grid_data = self.board.grid
            size_data = self.board.side_length
        else:
            grid_data = self.board["grid"]
            size_data = self.board.get("size", 3)
        return {
            "id": self.id,
            "board": {"grid": grid_data, "size": size_data},
        }
