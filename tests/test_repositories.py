import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from database import Database  # noqa: E402
from repositories import (  # noqa: E402
    BowlingBallRepository,
    GameJoinRepository,
    GameRecordRepository,
)


class RepositoryIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp_dir.name) / "test.duckdb")
        self.db.initialize()
        self.balls = BowlingBallRepository(self.db)
        self.games = GameRecordRepository(self.db)
        self.joins = GameJoinRepository(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_five_tables_are_seeded(self):
        counts = self.db.table_counts()
        self.assertEqual(set(counts), {"bowling_center", "lane_condition", "bowling_ball", "game_record", "game_ball"})
        self.assertTrue(all(count > 0 for count in counts.values()))

    def test_ball_crud_and_image_path(self):
        ball_id = self.balls.insert(
            {
                "name": "테스트 볼",
                "weight_lbs": 15,
                "coverstock": "솔리드",
                "surface_finish": "2000 Grit",
                "hook_potential": "중간",
                "image_path": "assets/ball_neon.png",
            }
        )
        inserted = self.balls.find_by_id(ball_id)
        self.assertEqual(inserted.image_path, "assets/ball_neon.png")

        self.balls.update(
            ball_id,
            {
                "name": "테스트 볼 수정",
                "weight_lbs": 14,
                "coverstock": "하이브리드",
                "surface_finish": "Polished",
                "hook_potential": "약함",
                "image_path": "assets/ball_white.png",
            },
        )
        self.assertEqual(self.balls.find_by_id(ball_id).name, "테스트 볼 수정")
        self.balls.delete(ball_id)
        self.assertIsNone(self.balls.find_by_id(ball_id))

    def test_game_insert_and_five_table_left_join(self):
        game_id = self.games.insert_with_ball(
            {
                "lane_id": 1,
                "played_date": date(2026, 6, 21),
                "score": 205,
                "strike_count": 6,
                "spare_count": 3,
                "open_frame_count": 1,
                "average_speed_kmh": 25.2,
                "memo": "통합 테스트",
            },
            {
                "ball_id": 2,
                "purpose": "첫 투구",
                "target_board": 13,
                "breakpoint_board": 8,
                "reaction_note": "안정적",
            },
        )
        rows = self.joins.find_all("2026-06-21")
        self.assertEqual(rows[0]["game_id"], game_id)
        self.assertEqual(rows[0]["center_name"], "구미 중앙볼링장")
        self.assertEqual(rows[0]["ball_name"], "블루 궤도")
        self.assertEqual(rows[0]["image_path"], "assets/ball_blue.png")

    def test_game_update_and_delete(self):
        self.games.update_score(1, 190, "수정 확인")
        row = next(item for item in self.joins.find_all() if item["game_id"] == 1)
        self.assertEqual(row["score"], 190)
        self.games.delete(1)
        self.assertFalse(any(item["game_id"] == 1 for item in self.joins.find_all()))


if __name__ == "__main__":
    unittest.main()

