from datetime import datetime, timedelta

from sqlalchemy import or_, text

from datasource.database      import db
from datasource.model.game_ds import GameDS


class GameRepository:

    def save(self, game_ds: GameDS) -> None:
        db.session.merge(game_ds)
        db.session.commit()

    def get_by_id(self, game_id: str) -> GameDS | None:
        return db.session.get(GameDS, game_id)

    def get_all_waiting(self) -> list[GameDS]:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        return GameDS.query.filter(
            GameDS.state      == "waiting",
            GameDS.created_at >= one_hour_ago,
        ).all()

    def get_finished_by_user(self, user_id: str) -> list[GameDS]:
        return GameDS.query.filter(
            GameDS.state.in_(["win", "draw"]),
            or_(
                GameDS.player_x_id == user_id,
                GameDS.player_o_id == user_id,
            ),
        ).order_by(GameDS.created_at.desc()).all()

    def get_leaderboard(self, top_n: int) -> list[dict]:
        query = text("""
            WITH participations AS (
                SELECT
                    player_x_id AS user_id,
                    CASE
                        WHEN state = 'draw' THEN 'draw'
                        WHEN state = 'win' AND current_turn = player_x_id THEN 'win'
                        ELSE 'loss'
                    END AS result
                FROM games
                WHERE state IN ('win', 'draw') AND player_x_id IS NOT NULL

                UNION ALL

                SELECT
                    player_o_id AS user_id,
                    CASE
                        WHEN state = 'draw' THEN 'draw'
                        WHEN state = 'win' AND current_turn = player_o_id THEN 'win'
                        ELSE 'loss'
                    END AS result
                FROM games
                WHERE state IN ('win', 'draw') AND player_o_id IS NOT NULL
            ),
            stats AS (
                SELECT
                    user_id,
                    SUM(CASE WHEN result = 'win'  THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) AS losses,
                    SUM(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) AS draws
                FROM participations
                GROUP BY user_id
            )
            SELECT
                u.id    AS user_id,
                u.login AS login,
                s.wins   AS wins,
                s.losses AS losses,
                s.draws  AS draws,
                CAST(s.wins AS FLOAT)
                    / GREATEST(s.losses + s.draws, 1) AS win_ratio
            FROM stats s
            JOIN users u ON u.id = s.user_id
            ORDER BY win_ratio DESC, s.wins DESC
            LIMIT :n;
        """)

        rows = db.session.execute(query, {"n": top_n}).mappings().all()

        return [dict(row) for row in rows]
