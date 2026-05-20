from typing import Any, Callable, Dict
from flask import Flask
from datasource.repository.game_repository import GameRepository
from datasource.repository.user_repository import UserRepository
from datasource.service.logic_handler import LogicWithArchive
from domain.service.auth_service import AuthService
from domain.service.user_service import UserService
from web.auth.auth_controller import create_auth_routes
from web.route.game_router import build_app


class DependencyBox:
    def __init__(self) -> None:
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._setup()

    def _setup(self) -> None:
        self.register_singleton("game_repo", lambda: GameRepository())
        self.register_singleton("user_repo", lambda: UserRepository())
        self.register_singleton("logic", lambda: LogicWithArchive(self.get("game_repo")))
        self.register_singleton("user_svc", lambda: UserService(self.get("user_repo")))
        self.register_singleton("auth_svc", lambda: AuthService(self.get("user_svc")))
        self.register_singleton("web_app", self._build_web_app)

    def _build_web_app(self) -> Flask:
        app: Flask = build_app(
            logic_service=self.get("logic"),
            auth_service=self.get("auth_svc"),
            game_repo=self.get("game_repo"),
            user_svc=self.get("user_svc"),
        )
        app.register_blueprint(create_auth_routes())
        return app

    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        self._factories[name] = factory
        self._singletons[name] = factory()

    def get(self, name: str) -> Any:
        if name in self._singletons:
            return self._singletons[name]
        elif name in self._factories:
            return self._factories[name]()
        else:
            raise ValueError(f"Компонент '{name}' не найден в реестре")
