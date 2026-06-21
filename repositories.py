from dataclasses import dataclass
from datetime import date
from typing import Any

from database import Database


@dataclass
class BowlingBall:
    ball_id: int
    name: str
    weight_lbs: int
    coverstock: str
    surface_finish: str
    hook_potential: str
    image_path: str


class BowlingCenterRepository:
    def __init__(self, db: Database):
        self.db = db

    def find_all(self) -> list[dict[str, Any]]:
        with self.db.connection() as con:
            rows = con.execute(
                "SELECT center_id, name, region, lane_count FROM bowling_center ORDER BY name"
            ).fetchall()
        return [dict(zip(["center_id", "name", "region", "lane_count"], row)) for row in rows]


class LaneConditionRepository:
    def __init__(self, db: Database):
        self.db = db

    def find_all(self) -> list[dict[str, Any]]:
        sql = """
            SELECT l.lane_id, l.center_id, c.name AS center_name, l.oil_pattern,
                   l.oil_length, l.difficulty, l.surface_type
            FROM lane_condition l
            JOIN bowling_center c ON c.center_id = l.center_id
            ORDER BY c.name, l.lane_id
        """
        with self.db.connection() as con:
            cur = con.execute(sql)
            columns = [item[0] for item in cur.description]
            rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]


class BowlingBallRepository:
    def __init__(self, db: Database):
        self.db = db

    def find_all(self, keyword: str = "") -> list[BowlingBall]:
        sql = """
            SELECT ball_id, name, weight_lbs, coverstock, surface_finish,
                   hook_potential, image_path
            FROM bowling_ball
            WHERE lower(name) LIKE lower(?) OR lower(coverstock) LIKE lower(?)
            ORDER BY ball_id
        """
        pattern = f"%{keyword.strip()}%"
        with self.db.connection() as con:
            rows = con.execute(sql, [pattern, pattern]).fetchall()
        return [BowlingBall(*row) for row in rows]

    def find_by_id(self, ball_id: int) -> BowlingBall | None:
        with self.db.connection() as con:
            row = con.execute(
                """SELECT ball_id, name, weight_lbs, coverstock, surface_finish,
                          hook_potential, image_path
                   FROM bowling_ball WHERE ball_id = ?""",
                [ball_id],
            ).fetchone()
        return BowlingBall(*row) if row else None

    def insert(self, data: dict[str, Any]) -> int:
        with self.db.connection() as con:
            next_id = con.execute("SELECT COALESCE(MAX(ball_id), 0) + 1 FROM bowling_ball").fetchone()[0]
            con.execute(
                """INSERT INTO bowling_ball
                   (ball_id, name, weight_lbs, coverstock, surface_finish, hook_potential, image_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [
                    next_id,
                    data["name"],
                    data["weight_lbs"],
                    data["coverstock"],
                    data["surface_finish"],
                    data["hook_potential"],
                    data["image_path"],
                ],
            )
        return next_id

    def update(self, ball_id: int, data: dict[str, Any]):
        with self.db.connection() as con:
            con.execute(
                """UPDATE bowling_ball
                   SET name = ?, weight_lbs = ?, coverstock = ?, surface_finish = ?,
                       hook_potential = ?, image_path = ?
                   WHERE ball_id = ?""",
                [
                    data["name"],
                    data["weight_lbs"],
                    data["coverstock"],
                    data["surface_finish"],
                    data["hook_potential"],
                    data["image_path"],
                    ball_id,
                ],
            )

    def delete(self, ball_id: int):
        with self.db.connection() as con:
            used = con.execute("SELECT COUNT(*) FROM game_ball WHERE ball_id = ?", [ball_id]).fetchone()[0]
            if used:
                raise ValueError("경기 기록에서 사용 중인 볼링공은 삭제할 수 없습니다.")
            con.execute("DELETE FROM bowling_ball WHERE ball_id = ?", [ball_id])


class GameRecordRepository:
    def __init__(self, db: Database):
        self.db = db

    def insert_with_ball(self, game: dict[str, Any], game_ball: dict[str, Any]) -> int:
        """경기와 사용 공 관계를 하나의 트랜잭션으로 저장한다."""
        with self.db.connection() as con:
            con.execute("BEGIN TRANSACTION")
            try:
                next_id = con.execute("SELECT COALESCE(MAX(game_id), 0) + 1 FROM game_record").fetchone()[0]
                con.execute(
                    """INSERT INTO game_record
                       (game_id, lane_id, played_date, score, strike_count, spare_count,
                        open_frame_count, average_speed_kmh, memo)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    [
                        next_id,
                        game["lane_id"],
                        game["played_date"],
                        game["score"],
                        game["strike_count"],
                        game["spare_count"],
                        game["open_frame_count"],
                        game["average_speed_kmh"],
                        game["memo"],
                    ],
                )
                con.execute(
                    """INSERT INTO game_ball
                       (game_id, ball_id, usage_order, purpose, target_board,
                        breakpoint_board, reaction_note)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    [
                        next_id,
                        game_ball["ball_id"],
                        1,
                        game_ball["purpose"],
                        game_ball["target_board"],
                        game_ball["breakpoint_board"],
                        game_ball["reaction_note"],
                    ],
                )
                con.execute("COMMIT")
                return next_id
            except Exception:
                con.execute("ROLLBACK")
                raise

    def update_score(self, game_id: int, score: int, memo: str):
        with self.db.connection() as con:
            con.execute(
                "UPDATE game_record SET score = ?, memo = ? WHERE game_id = ?",
                [score, memo, game_id],
            )

    def delete(self, game_id: int):
        # DuckDB 1.5.x는 같은 트랜잭션에서 자식 행을 삭제한 직후 부모 행을
        # 삭제할 때 FK 인덱스가 즉시 갱신되지 않는 제한이 있다. 따라서 자식
        # 관계를 먼저 확정하고 부모를 삭제하되, 실패하면 관계 행을 복구한다.
        with self.db.connection() as con:
            children = con.execute(
                """SELECT game_id, ball_id, usage_order, purpose, target_board,
                          breakpoint_board, reaction_note
                   FROM game_ball WHERE game_id = ?""",
                [game_id],
            ).fetchall()
            con.execute("DELETE FROM game_ball WHERE game_id = ?", [game_id])
        try:
            with self.db.connection() as con:
                con.execute("DELETE FROM game_record WHERE game_id = ?", [game_id])
        except Exception:
            if children:
                with self.db.connection() as con:
                    con.executemany(
                        """INSERT INTO game_ball
                           (game_id, ball_id, usage_order, purpose, target_board,
                            breakpoint_board, reaction_note)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        children,
                    )
            raise


class GameJoinRepository:
    """보고서 제한조건을 증명하는 5개 테이블 LEFT JOIN 전용 Repository."""

    JOIN_SQL = """
        SELECT
            g.game_id,
            g.played_date,
            g.score,
            g.strike_count,
            g.spare_count,
            g.open_frame_count,
            g.average_speed_kmh,
            c.name AS center_name,
            c.region,
            l.oil_pattern,
            l.oil_length,
            l.difficulty,
            b.ball_id,
            b.name AS ball_name,
            b.image_path,
            gb.purpose,
            gb.target_board,
            gb.breakpoint_board,
            gb.reaction_note,
            g.memo
        FROM game_record g
        LEFT JOIN lane_condition l ON l.lane_id = g.lane_id
        LEFT JOIN bowling_center c ON c.center_id = l.center_id
        LEFT JOIN game_ball gb ON gb.game_id = g.game_id
        LEFT JOIN bowling_ball b ON b.ball_id = gb.ball_id
        WHERE CAST(g.played_date AS VARCHAR) LIKE ?
           OR lower(c.name) LIKE lower(?)
           OR lower(b.name) LIKE lower(?)
        ORDER BY g.played_date DESC, g.game_id DESC, gb.usage_order
    """

    def __init__(self, db: Database):
        self.db = db

    def find_all(self, keyword: str = "") -> list[dict[str, Any]]:
        pattern = f"%{keyword.strip()}%"
        with self.db.connection() as con:
            cur = con.execute(self.JOIN_SQL, [pattern, pattern, pattern])
            columns = [item[0] for item in cur.description]
            rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def summary(self) -> dict[str, float | int]:
        with self.db.connection() as con:
            row = con.execute(
                """SELECT COUNT(*), COALESCE(ROUND(AVG(score), 1), 0),
                          COALESCE(MAX(score), 0), COALESCE(SUM(strike_count), 0)
                   FROM game_record"""
            ).fetchone()
        return {"games": row[0], "average": row[1], "high": row[2], "strikes": row[3]}
