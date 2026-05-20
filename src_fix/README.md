# H-T04 — Крестики-Нолики (исправленная версия)

## Главная причина ошибки 500

В `main.py` не вызывалась функция `init_db()`. Таблиц `users` и `game_sessions`
в базе PostgreSQL не существовало, поэтому любой запрос (signup, login и т.д.)
падал с `psycopg2.errors.UndefinedTable: relation "users" does not exist`.

В новой версии `main.py` добавлен вызов `init_db()` перед запуском Flask.

## Что удалено из старой структуры

- `web/module/play_module.py` — пустой Blueprint (модуль маршрутов Flask), нигде не использовался
- `web/module/__init__.py` — папка целиком не нужна
- `domain/model/user.py` — dataclass `User` нигде не использовался (везде `UserDB`)
- `domain/service/rules_contract.py` — абстрактный класс (ABC = Abstract Base Class),
  наследовался только одним классом, избыточный слой абстракции для учебного проекта
- `datasource/mapper/` — пустая папка

## Что исправлено в логике

1. **`init_db()`** теперь вызывается при старте — таблицы создаются автоматически
2. **`/login`** теперь принимает заголовок `Authorization: Basic base64(login:password)`,
   как требует задание (в задании 2.5: "принимает в заголовке логин и пароль в виде base64(login:password)")
3. **`/user/<user_id>`** теперь ищет по UUID, а не по логину
4. **`UserAuthenticator`** пробрасывает `user_id` в Flask-`g`, и эндпоинты `/game`, `/game/<id>/join`
   используют именно авторизованного пользователя, а не заголовок `X-User-Id`
5. **`MatchSession.mode`** теперь нормальное поле, а не хак через `hasattr`
6. **`game_repository.join_game`** проверяет, что игрок не пытается присоединиться к своей же игре
7. **`process_turn`** загружает игровое состояние из БД (раньше доверял клиенту),
   что корректнее с точки зрения безопасности

## Как запустить

```bash
# 1) Поднять PostgreSQL и создать БД tictactoe_db
sudo -u postgres psql -c "CREATE DATABASE tictactoe_db;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# 2) Активировать venv и установить зависимости
python3 -m venv .venv
source .venv/bin/activate
pip install flask sqlalchemy psycopg2-binary werkzeug

# 3) Запустить (из папки src/)
cd src
python main.py
```

## Если таблицы остались с косячными данными от старых попыток

Можно дропнуть и пересоздать БД:

```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS tictactoe_db;"
sudo -u postgres psql -c "CREATE DATABASE tictactoe_db;"
```

Или удалить таблицы вручную:

```bash
sudo -u postgres psql -d tictactoe_db -c "DROP TABLE IF EXISTS users, game_sessions CASCADE;"
```

После этого `init_db()` создаст их заново при запуске.

## Структура проекта (после чистки)

```
src/
├── main.py
├── datasource/
│   ├── db.py
│   ├── model/
│   │   ├── game_db.py
│   │   └── user_db.py
│   ├── repository/
│   │   ├── game_repository.py
│   │   └── user_repository.py
│   └── service/
│       └── logic_handler.py
├── di/
│   └── app_box.py
├── domain/
│   ├── model/
│   │   ├── board.py
│   │   └── game.py
│   └── service/
│       ├── ai_engine.py
│       ├── auth_service.py
│       └── user_service.py
└── web/
    ├── auth/
    │   └── auth_controller.py
    ├── mapper/
    │   └── view_translator.py
    ├── middleware/
    │   └── user_authenticator.py
    ├── model/
    │   ├── auth_request.py
    │   ├── board_view.py
    │   └── game_view.py
    ├── route/
    │   └── game_router.py
    └── static/
        └── play.html
```

Итого: **15 .py + 1 .html** (раньше было ~20 .py + 1 .html).
