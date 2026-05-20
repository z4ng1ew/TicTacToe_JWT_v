import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory

from domain.service.interface import GameServiceInterface
from web.auth.authenticator import UserAuthenticator
from web.mapper.mapper import GameWebMapper


def create_game_controller(
    service:       GameServiceInterface,
    authenticator: UserAuthenticator,
) -> tuple:

    game_bp = Blueprint('game', __name__, url_prefix='/games')
    user_bp = Blueprint('user', __name__, url_prefix='/users')

    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')

    @game_bp.route('/', defaults={'path': ''})
    @game_bp.route('/<path:path>')
    def serve_frontend(path):
        if path == '' or path == '/':
            return send_from_directory(static_dir, 'index.html')
        else:
            return send_from_directory(static_dir, path)

    @game_bp.route('', methods=['POST'])
    @authenticator.required
    def create_game(user_id: uuid.UUID):
        data          = request.get_json() or {}
        opponent_type = data.get('opponent_type', 'computer')

        if opponent_type not in ('computer', 'user'):
            return jsonify({'error': 'opponent_type must be computer or user'}), 400
        else:
            game = service.create_game(
                player_id     = user_id,
                opponent_type = opponent_type,
            )
            return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 201

    @game_bp.route('', methods=['GET'])
    @authenticator.required
    def get_games(user_id: uuid.UUID):
        games = service.get_available_games()
        return jsonify([
            GameWebMapper.domain_to_web(g).to_dict() for g in games
        ]), 200

    @game_bp.route('/<string:game_id>/join', methods=['POST'])
    @authenticator.required
    def join_game(game_id: str, user_id: uuid.UUID):
        game = service.join_game(
            game_id   = game_id,
            player_id = user_id,
        )

        if game is None:
            return jsonify({'error': 'game not found or already started'}), 404
        else:
            return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 200

    @game_bp.route('/<string:game_id>', methods=['GET'])
    @authenticator.required
    def get_game(game_id: str, user_id: uuid.UUID):
        game = service.get_game(game_id)

        if game is None:
            return jsonify({'error': 'game not found'}), 404
        else:
            return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 200

    @game_bp.route('/<string:game_id>', methods=['PATCH'])
    @authenticator.required
    def make_move(game_id: str, user_id: uuid.UUID):
        data = request.get_json()

        if not data or 'row' not in data or 'col' not in data:
            return jsonify({'error': 'row and col required'}), 400
        else:
            game = service.make_move(
                game_id   = game_id,
                player_id = user_id,
                row       = data['row'],
                col       = data['col'],
            )

            if game is None:
                return jsonify({'error': 'game not found or move not allowed'}), 400
            else:
                return jsonify(GameWebMapper.domain_to_web(game).to_dict()), 200

    @user_bp.route('/<string:user_uuid>', methods=['GET'])
    @authenticator.required
    def get_user(user_uuid: str, user_id: uuid.UUID):
        user = service.get_user(user_uuid)

        if user is None:
            return jsonify({'error': 'user not found'}), 404
        else:
            return jsonify({
                'id':    str(user.id),
                'login': user.login,
            }), 200

    return game_bp, user_bp