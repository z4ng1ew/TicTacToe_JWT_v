import os
from flask import Flask, send_from_directory

from datasource.database import db, init_db
from datasource.repository.game_repo import GameRepository
from datasource.repository.user_repo import UserRepository
from datasource.mapper.mapper import GameMapper, UserMapper
from datasource.service.game_service_impl import GameServiceImplWithRepo
from domain.service.user_service import UserService
from domain.service.auth_service import AuthService
from web.auth.authenticator import UserAuthenticator
from web.route.controller import create_game_controller
from web.route.auth_controller import create_auth_controller


class Container:

    def __init__(self):
        self._app = Flask(__name__)

        init_db(self._app)

        with self._app.app_context():
            db.create_all()

        self._game_repo   = GameRepository()
        self._user_repo   = UserRepository()
        self._game_mapper = GameMapper()
        self._user_mapper = UserMapper()

        self._user_service = UserService(
            user_repo = self._user_repo,
        )

        self._game_service = GameServiceImplWithRepo(
            repository = self._game_repo,
            mapper     = self._game_mapper,
            user_repo  = self._user_repo,
        )

        self._auth_service = AuthService(
            user_service = self._user_service,
        )

        self._authenticator = UserAuthenticator(
            auth_service = self._auth_service,
        )

        game_bp, user_bp = create_game_controller(
            service       = self._game_service,
            authenticator = self._authenticator,
        )
        self._app.register_blueprint(game_bp)
        self._app.register_blueprint(user_bp)

        auth_bp = create_auth_controller(
            auth_service = self._auth_service,
        )
        self._app.register_blueprint(auth_bp)

        static_dir = os.path.join(
            os.path.dirname(__file__), '..', 'web', 'static'
        )

        @self._app.route('/')
        def index():
            return send_from_directory(static_dir, 'index.html')

        @self._app.route('/assets/<path:filename>')
        def serve_static(filename):
            return send_from_directory(static_dir, filename)

    def get_app(self) -> Flask:
        return self._app