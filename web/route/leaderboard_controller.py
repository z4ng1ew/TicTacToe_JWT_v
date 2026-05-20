import uuid

from flask import Blueprint, request, jsonify, Response

from domain.service.game_service_interface import GameServiceInterface
from web.module.user_authenticator         import UserAuthenticator


def create_leaderboard_controller(
    game_service:  GameServiceInterface,
    authenticator: UserAuthenticator,
) -> Blueprint:
    blueprint = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")

    @blueprint.route("", methods=["GET"])
    @authenticator.authenticate
    def get_leaderboard(user_id: uuid.UUID) -> tuple[Response, int]:
        try:
            top_n = int(request.args.get("n", "10"))
        except ValueError:
            return jsonify({"error": "n must be an integer"}), 400

        if top_n <= 0:
            return jsonify({"error": "n must be positive"}), 400
        else:
            entries = game_service.get_leaderboard(top_n)
            return jsonify([entry.to_dict() for entry in entries]), 200

    return blueprint
