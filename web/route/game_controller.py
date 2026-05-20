import uuid

from flask import Blueprint, request, jsonify, Response

from domain.service.game_service_interface import GameServiceInterface
from web.module.user_authenticator         import UserAuthenticator
from web.mapper.game_web_mapper            import GameWebMapper


def create_game_controller(
    game_service:  GameServiceInterface,
    authenticator: UserAuthenticator,
) -> Blueprint:
    blueprint = Blueprint("game", __name__, url_prefix="/games")

    @blueprint.route("", methods=["POST"])
    @authenticator.authenticate
    def create_game(user_id: uuid.UUID) -> tuple[Response, int]:
        data          = request.get_json(silent=True) or {}
        opponent_type = data.get("opponent_type", "computer")

        if opponent_type not in ("computer", "user"):
            return jsonify({"error": "opponent_type must be computer or user"}), 400
        else:
            game = game_service.create_game(
                player_id     = user_id,
                opponent_type = opponent_type,
            )
            return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 201

    @blueprint.route("", methods=["GET"])
    @authenticator.authenticate
    def get_available_games(user_id: uuid.UUID) -> tuple[Response, int]:
        games = game_service.get_available_games()

        return jsonify([
            GameWebMapper.domain_to_web(game).to_dict() for game in games
        ]), 200

    @blueprint.route("/history", methods=["GET"])
    @authenticator.authenticate
    def get_history(user_id: uuid.UUID) -> tuple[Response, int]:
        games = game_service.get_finished_games_by_user(str(user_id))

        return jsonify([
            GameWebMapper.domain_to_web(game).to_dict() for game in games
        ]), 200

    @blueprint.route("/<string:game_id>/join", methods=["POST"])
    @authenticator.authenticate
    def join_game(game_id: str, user_id: uuid.UUID) -> tuple[Response, int]:
        game = game_service.join_game(
            game_id   = game_id,
            player_id = user_id,
        )

        if game is None:
            return jsonify({"error": "game not found or already started"}), 404
        else:
            return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 200

    @blueprint.route("/<string:game_id>", methods=["GET"])
    @authenticator.authenticate
    def get_game(game_id: str, user_id: uuid.UUID) -> tuple[Response, int]:
        game = game_service.get_game(game_id)

        if game is None:
            return jsonify({"error": "game not found"}), 404
        else:
            return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 200

    @blueprint.route("/<string:game_id>", methods=["PATCH"])
    @authenticator.authenticate
    def make_move(game_id: str, user_id: uuid.UUID) -> tuple[Response, int]:
        data = request.get_json(silent=True)

        if data is None or "row" not in data or "col" not in data:
            return jsonify({"error": "row and col required"}), 400

        game = game_service.make_move(
            game_id   = game_id,
            player_id = user_id,
            row       = data["row"],
            col       = data["col"],
        )

        if game is None:
            return jsonify({"error": "game not found or move not allowed"}), 400
        else:
            return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 200

    return blueprint
