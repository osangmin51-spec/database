from contextlib import contextmanager
from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "bowling_tracker.duckdb"


class Database:
    """DuckDB 연결과 초기 스키마 생성을 한곳에서 관리한다."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self):
        """요청 단위로 연결을 열고 사용 후 반드시 닫아 파일 잠금을 줄인다."""
        con = duckdb.connect(str(self.db_path))
        try:
            yield con
        finally:
            con.close()

    def initialize(self):
        """테이블과 시연용 초기 데이터를 중복 없이 생성한다."""
        schema_sql = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
        seed_sql = (BASE_DIR / "seed.sql").read_text(encoding="utf-8")
        with self.connection() as con:
            con.execute(schema_sql)
            con.execute(seed_sql)

    def table_counts(self) -> dict[str, int]:
        """대시보드에서 초기화 상태를 확인할 수 있도록 테이블별 행 수를 반환한다."""
        tables = [
            "bowling_center",
            "lane_condition",
            "bowling_ball",
            "game_record",
            "game_ball",
        ]
        with self.connection() as con:
            return {table: con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}
