from flask import Blueprint, request, jsonify, Response

from domain.service.auth_service   import AuthService
from domain.model.signup_request   import SignUpRequest


def create_auth_controller(auth_service: AuthService) -> Blueprint:
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
        auth_header = request.headers.get("Authorization")

        if auth_header is None:
            return jsonify({"error": "Authorization header required"}), 401

        user_id = auth_service.login(auth_header)

        if user_id is None:
            return jsonify({"error": "invalid login or password"}), 401
        else:
            return jsonify({"user_id": str(user_id)}), 200

    return blueprint
