import uuid
from typing import Any, Dict
from domain.model.board import GameField
from domain.model.game import MatchSession
from web.model.board_view import FieldView
from web.model.game_view import SessionView


class ViewDomainTranslator:
    @staticmethod
    def domain_to_view(session: MatchSession) -> SessionView:
        board_view: FieldView = FieldView(
            grid=[row.copy() for row in session.field.grid],
            side_length=session.field.side_length,
        )
        return SessionView(id=str(session.session_id), board=board_view)

    @staticmethod
    def view_to_domain(view_session: SessionView) -> MatchSession:
        board_data: Dict[str, Any] = (
            {"grid": view_session.board.grid, "size": view_session.board.side_length}
            if isinstance(view_session.board, FieldView)
            else view_session.board
        )
        grid_data = board_data["grid"]
        size_data = board_data.get("size", 3)
        domain_board: GameField = GameField(grid=[row.copy() for row in grid_data], side_length=size_data)
        return MatchSession(
            current_field=domain_board,
            session_id=uuid.UUID(view_session.id),
        )
