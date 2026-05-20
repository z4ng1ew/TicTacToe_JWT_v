from typing import Any, Dict, Optional, Tuple
from flask import Blueprint, current_app, jsonify, request
from domain.service.auth_service import AuthService
from web.model.auth_request import SignUpRequest


def create_auth_routes() -> Blueprint:
    bp: Blueprint = Blueprint("auth", __name__)

    @bp.route("/signup", methods=["POST"])
    def signup_endpoint() -> Tuple[Any, int]:
        service: AuthService = current_app.config["auth_service"]
        payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
        if payload is None:
            return jsonify({"error": "Пустое или некорректное тело запроса"}), 400
        elif "login" not in payload or "password" not in payload:
            return jsonify({"error": "Отсутствуют поля login/password"}), 400
        else:
            req: SignUpRequest = SignUpRequest(login=payload["login"], password=payload["password"])
            success: bool = service.register(req.login, req.password)
            if success:
                return jsonify({"status": "registered"}), 201
            else:
                return jsonify({"error": "Логин уже занят или данные пусты"}), 409

    @bp.route("/login", methods=["POST"])
    def login_endpoint() -> Tuple[Any, int]:
        service: AuthService = current_app.config["auth_service"]
        header: Optional[str] = request.headers.get("Authorization")
        if not header:
            return jsonify({"error": "Требуется заголовок Authorization: Basic"}), 401
        else:
            user_id: Optional[str] = service.authorize(header)
            if user_id is not None:
                return jsonify({"user_id": user_id}), 200
            else:
                return jsonify({"error": "Неверный логин или пароль"}), 401

    return bp
