import uuid

from flask import Blueprint, request, jsonify, Response

from domain.service.auth_service       import AuthService
from domain.service.user_service       import UserService
from domain.model.signup_request       import SignUpRequest
from domain.model.jwt_request          import JwtRequest
from web.module.user_authenticator     import UserAuthenticator


def create_auth_controller(
    auth_service:  AuthService,
    user_service:  UserService,
    authenticator: UserAuthenticator,
) -> Blueprint:
    blueprint = Blueprint("auth", __name__, url_prefix="/auth")

    @blueprint.route("/register", methods=["POST"])
    def register() -> tuple[Response, int]:
        data = request.get_json(silent=True)

        if data is None or "login" not in data or "password" not in data:
            return jsonify({"error": "login and password required"}), 400

        signup_request = SignUpRequest(
            login    = data["login"],
            password = data["password"],
        )

        is_registered = auth_service.register(signup_request)

        if is_registered:
            return jsonify({"message": "registered successfully"}), 201
        else:
            return jsonify({"error": "login already taken"}), 409

    @blueprint.route("/login", methods=["POST"])
    def login() -> tuple[Response, int]:
        data = request.get_json(silent=True)

        if data is None or "login" not in data or "password" not in data:
            return jsonify({"error": "login and password required"}), 400

        jwt_request = JwtRequest(
            login    = data["login"],
            password = data["password"],
        )

        jwt_response = auth_service.login(jwt_request)

        if jwt_response is None:
            return jsonify({"error": "invalid login or password"}), 401
        else:
            return jsonify(jwt_response.to_dict()), 200

    @blueprint.route("/access", methods=["POST"])
    def refresh_access() -> tuple[Response, int]:
        data = request.get_json(silent=True)

        if data is None or "refreshToken" not in data:
            return jsonify({"error": "refreshToken required"}), 400

        jwt_response = auth_service.refresh_access(data["refreshToken"])

        if jwt_response is None:
            return jsonify({"error": "invalid refresh token"}), 401
        else:
            return jsonify(jwt_response.to_dict()), 200

    @blueprint.route("/refresh", methods=["POST"])
    def refresh_refresh() -> tuple[Response, int]:
        data = request.get_json(silent=True)

        if data is None or "refreshToken" not in data:
            return jsonify({"error": "refreshToken required"}), 400

        jwt_response = auth_service.refresh_refresh(data["refreshToken"])

        if jwt_response is None:
            return jsonify({"error": "invalid refresh token"}), 401
        else:
            return jsonify(jwt_response.to_dict()), 200

    @blueprint.route("/me", methods=["GET"])
    @authenticator.authenticate
    def me(user_id: uuid.UUID) -> tuple[Response, int]:
        user_ds = user_service.get_by_id(str(user_id))

        if user_ds is None:
            return jsonify({"error": "user not found"}), 404
        else:
            return jsonify({
                "id":    user_ds.id,
                "login": user_ds.login,
            }), 200

    return blueprint
