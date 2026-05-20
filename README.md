# Крестики-Нолики — T05

Многопользовательская игра «крестики-нолики» на Flask + PostgreSQL + SQLAlchemy + JWT.

## Что нового в T05 по сравнению с T04

- **JWT** вместо Basic-авторизации (`flask_jwt_extended`)
- `JwtProvider` — генерация и валидация access/refresh токенов
- Эндпоинты `/auth/login` (JSON body), `/auth/access` (обновление access), `/auth/refresh` (обновление обоих), `/auth/me`
- **История игр** игрока — `GET /games/history`
- **Таблица лидеров** — `GET /leaderboard?n=10`
- `Bearer {token}` в заголовке вместо `Basic base64(login:password)`

## Подготовка БД (PostgreSQL)

Если БД от T04 уже есть, лучше пересоздать (схема таблиц не изменилась, но проще начать с чистого листа):

```bash
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='tictactoe_db' AND pid <> pg_backend_pid();"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS tictactoe_db;"
sudo -u postgres psql -c "CREATE USER myuser WITH PASSWORD 'mypassword';" || true
sudo -u postgres psql -c "CREATE DATABASE tictactoe_db OWNER myuser;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tictactoe_db TO myuser;"
sudo -u postgres psql -d tictactoe_db -c "GRANT ALL ON SCHEMA public TO myuser;"
```

## Запуск

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Открыть: http://127.0.0.1:5000

## Эндпоинты

### Открытые (без авторизации)
| Метод | URL              | Описание |
|-------|------------------|----------|
| POST  | /auth/register   | body: {login, password} |
| POST  | /auth/login      | body: {login, password} → JwtResponse |
| POST  | /auth/access     | body: {refreshToken} → JwtResponse с новым accessToken |
| POST  | /auth/refresh    | body: {refreshToken} → JwtResponse с обоими новыми токенами |

### Защищённые (Authorization: Bearer {accessToken})
| Метод | URL                  | Описание |
|-------|----------------------|----------|
| GET   | /auth/me             | информация о текущем пользователе |
| POST  | /games               | создать игру (computer/user) |
| GET   | /games               | список доступных игр (waiting) |
| GET   | /games/history       | мои завершённые игры (win/draw) |
| POST  | /games/{id}/join     | присоединиться |
| GET   | /games/{id}          | получить игру |
| PATCH | /games/{id}          | сделать ход (body: row, col) |
| GET   | /users/{uuid}        | информация о пользователе |
| GET   | /leaderboard?n=N     | топ N игроков по соотношению побед |

## Примеры curl

```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"vasya","password":"12345"}'

ACCESS=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"vasya","password":"12345"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['accessToken'])")

curl http://127.0.0.1:5000/auth/me           -H "Authorization: Bearer $ACCESS"
curl http://127.0.0.1:5000/games/history     -H "Authorization: Bearer $ACCESS"
curl "http://127.0.0.1:5000/leaderboard?n=5" -H "Authorization: Bearer $ACCESS"
```

## Соответствие чек-листу T05

### Задание 1. JWT
- [x] `JwtRequest` (login, password) — `domain/model/jwt_request.py`
- [x] `JwtResponse` (type, accessToken, refreshToken) — `domain/model/jwt_response.py`
- [x] `RefreshJwtRequest` (refreshToken) — `domain/model/refresh_jwt_request.py`
- [x] `JwtProvider` — `domain/service/jwt_provider.py`, использует `flask_jwt_extended`:
    - генерация accessToken/refreshToken по User с UUID в claim
    - валидация accessToken/refreshToken
    - получение UUID из токена
- [x] `AuthService.login(JwtRequest) -> JwtResponse`
- [x] `AuthService.refresh_access(refresh_token) -> JwtResponse`
- [x] `AuthService.refresh_refresh(refresh_token) -> JwtResponse`
- [x] Контроллер авторизации: `/auth/login`, `/auth/access`, `/auth/refresh`
- [x] Basic убрана, добавлен Bearer в `UserAuthenticator`
- [x] Валидация через `JwtProvider`, 401 при ошибке
- [x] `/auth/access` доступен без авторизации
- [x] `/auth/me` — информация о пользователе по accessToken

### Задание 2. История игр
- [x] `created_at` в `GameDS` (Mapped[datetime])
- [x] Запрос `get_finished_by_user` — `state ∈ {win, draw}` и `user_id ∈ {player_x_id, player_o_id}`
- [x] Метод `get_finished_games_by_user` в сервисе
- [x] `GET /games/history` — только для авторизованных

### Задание 3. Таблица лидеров
- [x] `LeaderboardEntry` (user_id, login, wins, losses, draws, win_ratio)
- [x] SQL: `participations` (UNION ALL по X/O) → `stats` (агрегаты) → JOIN с users → `ORDER BY win_ratio DESC LIMIT N`
- [x] Метод `get_leaderboard(top_n)` в сервисе
- [x] `GET /leaderboard?n=N` — только для авторизованных
