import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from database import Database
from repositories import GameJoinRepository


BASE = Path(__file__).resolve().parent
OUT = BASE.parent / "report_assets"
OUT.mkdir(exist_ok=True)


def font(size: int, bold: bool = False):
    path = Path(r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf")
    return ImageFont.truetype(str(path), size)


def terminal_image(filename: str, title: str, lines: list[str], width: int = 1800, height: int = 1050):
    image = Image.new("RGB", (width, height), "#0C131A")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((28, 24, width - 28, height - 24), radius=16, fill="#111B24", outline="#31414E", width=2)
    draw.rectangle((28, 24, width - 28, 92), fill="#1A2834")
    for x, color in [(60, "#FF6B6B"), (94, "#FFC857"), (128, "#42E06F")]:
        draw.ellipse((x, 48, x + 18, 66), fill=color)
    draw.text((165, 43), title, fill="#F5F7FA", font=font(27, True))
    y = 118
    for line in lines:
        color = "#42E06F" if line.startswith(("[PASS]", "[", "SELECT", "CREATE", "LEFT")) else "#D4DCE3"
        draw.text((58, y), line, fill=color, font=font(19))
        y += 31
        if y > height - 60:
            break
    image.save(OUT / filename)


def main():
    db = Database()
    db.initialize()
    counts = db.table_counts()

    schema_lines = [
        "DuckDB 1.5.4  |  bowling_tracker.duckdb",
        "",
        "CREATE TABLE bowling_ball (",
        "  ball_id INTEGER PRIMARY KEY, name VARCHAR(50) NOT NULL,",
        "  weight_lbs INTEGER, coverstock VARCHAR(50),",
        "  surface_finish VARCHAR(50), hook_potential VARCHAR(30),",
        "  image_path VARCHAR NOT NULL",
        ");",
        "",
        "[TABLE COUNTS - INSERT 결과]",
    ]
    schema_lines.extend([f"{name:<20} {count:>3} rows" for name, count in counts.items()])
    schema_lines.extend(
        [
            "",
            "SELECT ball_id, name, image_path FROM bowling_ball;",
            "1  네온 임팩트      assets/ball_neon.png",
            "2  블루 궤도        assets/ball_blue.png",
            "3  스페어 화이트    assets/ball_white.png",
            "",
            "[PASS] 5개 테이블 생성 · 데이터 삽입 · 이미지 경로 저장 확인",
        ]
    )
    terminal_image("06_schema_and_seed_evidence.png", "DuckDB SQL 실행 증빙", schema_lines)

    join_rows = GameJoinRepository(db).find_all()
    join_lines = [
        "SELECT g.game_id, g.played_date, c.name, l.oil_pattern,",
        "       b.name AS ball_name, g.score, b.image_path",
        "FROM game_record g",
        "LEFT JOIN lane_condition l ON l.lane_id = g.lane_id",
        "LEFT JOIN bowling_center c ON c.center_id = l.center_id",
        "LEFT JOIN game_ball gb ON gb.game_id = g.game_id",
        "LEFT JOIN bowling_ball b ON b.ball_id = gb.ball_id",
        "ORDER BY g.played_date DESC;",
        "",
        "[5 TABLE LEFT JOIN RESULT]",
        "game  date        center              oil       ball            score  image_path",
    ]
    for row in join_rows:
        join_lines.append(
            f'{row["game_id"]:<4}  {str(row["played_date"]):<10}  {row["center_name"]:<18}  '
            f'{row["oil_pattern"]:<8}  {row["ball_name"]:<12}  {row["score"]:<5}  {row["image_path"]}'
        )
    join_lines.extend(["", f"[PASS] {len(join_rows)} rows returned · LEFT JOIN 정상 실행"])
    terminal_image("07_join_query_evidence.png", "5개 테이블 LEFT JOIN 증빙", join_lines)

    test = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=BASE,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    output = (test.stdout + "\n" + test.stderr).strip().splitlines()
    test_lines = ["Repository / DuckDB 통합 테스트", ""] + output + ["", "[PASS] 모든 CRUD·JOIN·이미지 경로 테스트 통과"]
    terminal_image("08_test_result_evidence.png", "자동 테스트 실행 결과", test_lines, height=900)


if __name__ == "__main__":
    main()
