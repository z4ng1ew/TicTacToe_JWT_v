import uuid

from flask import Blueprint, jsonify, Response

from domain.service.game_service_interface import GameServiceInterface
from web.module.user_authenticator         import UserAuthenticator


def create_user_controller(
    game_service:  GameServiceInterface,
    authenticator: UserAuthenticator,
) -> Blueprint:
    blueprint = Blueprint("user", __name__, url_prefix="/users")

    @blueprint.route("/<string:target_user_id>", methods=["GET"])
    @authenticator.authenticate
    def get_user(target_user_id: str, user_id: uuid.UUID) -> tuple[Response, int]:
        user = game_service.get_user(target_user_id)

        if user is None:
            return jsonify({"error": "user not found"}), 404
        else:
            return jsonify({
                "id":    str(user.id),
                "login": user.login,
            }), 200

    return blueprint
