import os
from typing import Any, Dict, List, Optional, Tuple
from flask import Flask, abort, g, jsonify, request, send_from_directory
from datasource.repository.game_repository import GameRepository
from datasource.service.logic_handler import LogicWithArchive
from domain.model.board import GameField
from domain.model.game import GameState, MatchSession
from domain.service.auth_service import AuthService
from domain.service.user_service import UserService
from web.mapper.view_translator import ViewDomainTranslator
from web.middleware.user_authenticator import UserAuthenticator
from web.model.board_view import FieldView
from web.model.game_view import SessionView


def build_app(
    logic_service: LogicWithArchive,
    auth_service: AuthService,
    game_repo: GameRepository,
    user_svc: UserService,
) -> Flask:
    application: Flask = Flask(__name__)
    application.config["auth_service"] = auth_service
    application.config["game_repo"] = game_repo
    application.config["user_svc"] = user_svc
    authenticator: UserAuthenticator = UserAuthenticator(auth_service)
    static_path: str = os.path.join(os.path.dirname(__file__), "..", "static")

    def _respond(session: MatchSession) -> Tuple[Any, int]:
        logic_service.save_match_state(session)
        view: SessionView = ViewDomainTranslator.domain_to_view(session)
        body: Dict[str, Any] = view.to_json_dict()
        body["state"] = session.state.value
        body["mode"] = session.mode
        body["player_x_id"] = session.player_x_id
        body["player_o_id"] = session.player_o_id
        return jsonify(body), 200

    @application.route("/")
    def show_main_page() -> Any:
        return send_from_directory(static_path, "play.html")

    @application.route("/static/<path:filename>")
    def show_static(filename: str) -> Any:
        return send_from_directory(static_path, filename)

    @application.route("/game", methods=["POST"])
    @authenticator.authenticate
    def create_game() -> Tuple[Any, int]:
        payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
        if payload is None:
            abort(400, description="Требуется тело запроса")
        else:
            mode: str = payload.get("mode", "pve")
            player_id: str = g.user_id
            if mode == "pvp":
                state: GameState = GameState.WAITING
                px: Optional[str] = player_id
            elif mode == "pve":
                state = GameState.PLAYER_X_TURN
                px = player_id
            else:
                abort(400, description="Неизвестный режим игры")

            new_session: MatchSession = MatchSession(
                current_field=GameField(),
                player_x_id=px,
                player_o_id=None,
                state=state,
                mode=mode,
            )
            logic_service.save_match_state(new_session)
            return jsonify({
                "id": str(new_session.session_id),
                "mode": new_session.mode,
                "state": new_session.state.value,
                "player_x_id": new_session.player_x_id,
                "player_o_id": new_session.player_o_id,
                "board": {
                    "grid": new_session.field.grid,
                    "size": new_session.field.side_length,
                },
            }), 201

    @application.route("/games/available", methods=["GET"])
    @authenticator.authenticate
    def list_available_games() -> Tuple[Any, int]:
        waiting: List[Dict[str, Any]] = game_repo.find_waiting_games()
        return jsonify({"games": waiting}), 200

    @application.route("/game/<string:game_id>/join", methods=["POST"])
    @authenticator.authenticate
    def join_game(game_id: str) -> Tuple[Any, int]:
        player_id: str = g.user_id
        success: bool = game_repo.join_game(game_id, player_id)
        if not success:
            abort(409, description="Не удалось присоединиться: игра занята или не найдена")
        else:
            loaded: Optional[Dict[str, Any]] = game_repo.load_match(game_id)
            if loaded is None:
                abort(500, description="Не удалось загрузить данные игры")
            else:
                return jsonify({
                    "id": loaded["session_id"],
                    "state": loaded["state"],
                    "mode": loaded["mode"],
                    "player_x_id": loaded["player_x_id"],
                    "player_o_id": loaded["player_o_id"],
                    "board": {"grid": loaded["grid"], "size": loaded["side_length"]},
                }), 200

    @application.route("/game/<string:game_id>", methods=["GET"])
    @authenticator.authenticate
    def get_game(game_id: str) -> Tuple[Any, int]:
        data: Optional[Dict[str, Any]] = game_repo.load_match(game_id)
        if data is None:
            abort(404, description="Игра не найдена")
        else:
            return jsonify({
                "id": data["session_id"],
                "state": data["state"],
                "mode": data["mode"],
                "player_x_id": data["player_x_id"],
                "player_o_id": data["player_o_id"],
                "board": {"grid": data["grid"], "size": data["side_length"]},
            }), 200

    @application.route("/game/<string:game_id>", methods=["POST"])
    @authenticator.authenticate
    def process_turn(game_id: str) -> Tuple[Any, int]:
        payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
        if payload is None or not isinstance(payload, dict):
            abort(400, description="Тело запроса должно быть JSON-объектом")
        else:
            stored: Optional[Dict[str, Any]] = game_repo.load_match(game_id)
            if stored is None:
                abort(404, description="Игра не найдена")
            else:
                board_payload: Dict[str, Any] = payload.get("board", {})
                grid_payload: List[List[int]] = board_payload.get("grid", stored["grid"])

                domain_session: MatchSession = MatchSession(
                    current_field=GameField(grid=grid_payload, side_length=stored["side_length"]),
                    player_x_id=stored["player_x_id"],
                    player_o_id=stored["player_o_id"],
                    state=GameState(stored["state"]),
                    mode=stored["mode"],
                )
                import uuid as _uuid
                domain_session.session_id = _uuid.UUID(stored["session_id"])

                prev_board: Optional[GameField] = logic_service.load_previous_field(domain_session.session_id)
                if prev_board is not None and not logic_service.check_board_changes(domain_session, prev_board):
                    abort(400, description="Проверка поля не пройдена: изменены старые ходы")
                else:
                    pass

                if logic_service.verify_end_state(domain_session):
                    logic_service.update_game_state(domain_session)
                    return _respond(domain_session)
                elif domain_session.mode == "pve":
                    logic_service.update_game_state(domain_session)
                    if not logic_service.verify_end_state(domain_session):
                        row, col = logic_service.calculate_ai_turn(domain_session)
                        if row != -1 and domain_session.field.grid[row][col] == 0:
                            domain_session.field.grid[row][col] = 2
                            logic_service.update_game_state(domain_session)
                        else:
                            abort(500, description="Невозможно сделать ход ИИ")
                    else:
                        pass
                    return _respond(domain_session)
                else:
                    logic_service.update_game_state(domain_session)
                    return _respond(domain_session)

    @application.route("/user/<string:user_id>", methods=["GET"])
    @authenticator.authenticate
    def get_user_info(user_id: str) -> Tuple[Any, int]:
        record = user_svc.find_by_id(user_id)
        if record is None:
            abort(404, description="Пользователь не найден")
        else:
            return jsonify({"user_id": record.user_id, "login": record.login}), 200

    return application
