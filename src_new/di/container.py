import os

from flask import Flask, send_from_directory, Response

from datasource.database                   import db, init_db
from datasource.repository.game_repository import GameRepository
from datasource.repository.user_repository import UserRepository
from datasource.mapper.game_mapper         import GameMapper
from datasource.mapper.user_mapper         import UserMapper
from datasource.service.game_service_impl  import GameServiceImpl

from domain.service.user_service           import UserService
from domain.service.auth_service           import AuthService

from web.module.user_authenticator         import UserAuthenticator
from web.route.auth_controller             import create_auth_controller
from web.route.game_controller             import create_game_controller
from web.route.user_controller             import create_user_controller


class Container:

    def __init__(self) -> None:
        self._app = Flask(__name__)

        init_db(self._app)

        with self._app.app_context():
            db.create_all()

        self._game_repository = GameRepository()
        self._user_repository = UserRepository()
        self._game_mapper     = GameMapper()
        self._user_mapper     = UserMapper()

        self._user_service = UserService(
            user_repository = self._user_repository,
        )

        self._auth_service = AuthService(
            user_service = self._user_service,
        )

        self._game_service = GameServiceImpl(
            game_repository = self._game_repository,
            user_repository = self._user_repository,
            game_mapper     = self._game_mapper,
            user_mapper     = self._user_mapper,
        )

        self._authenticator = UserAuthenticator(
            auth_service = self._auth_service,
        )

        self._app.register_blueprint(create_auth_controller(
            auth_service = self._auth_service,
        ))
        self._app.register_blueprint(create_game_controller(
            game_service  = self._game_service,
            authenticator = self._authenticator,
        ))
        self._app.register_blueprint(create_user_controller(
            game_service  = self._game_service,
            authenticator = self._authenticator,
        ))

        self._register_static_routes()

    def _register_static_routes(self) -> None:
        static_dir = os.path.join(
            os.path.dirname(__file__), "..", "web", "static",
        )

        @self._app.route("/")
        def index() -> Response:
            return send_from_directory(static_dir, "index.html")

        @self._app.route("/assets/<path:filename>")
        def serve_static(filename: str) -> Response:
            return send_from_directory(static_dir, filename)

    def get_app(self) -> Flask:
        return self._app
