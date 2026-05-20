from flask import Blueprint, request, jsonify

from domain.service.auth_service import AuthService
from domain.model.signup_request import SignUpRequest


def create_auth_controller(auth_service: AuthService) -> Blueprint:

    bp = Blueprint('auth', __name__, url_prefix='/auth')

    @bp.route('/register', methods=['POST'])
    def register():
        data = request.get_json()

        if not data or 'login' not in data or 'password' not in data:
            return jsonify({'error': 'login and password required'}), 400

        signup = SignUpRequest(
            login    = data['login'],
            password = data['password'],
        )

        success = auth_service.register(signup)

        if not success:
            return jsonify({'error': 'login already taken'}), 409

        return jsonify({'message': 'registered successfully'}), 201

    @bp.route('/login', methods=['POST'])
    def login():
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401

        user_id = auth_service.login(auth_header)

        if user_id is None:
            return jsonify({'error': 'invalid login or password'}), 401

        return jsonify({'user_id': str(user_id)}), 200

    return bp