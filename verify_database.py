from database import Database
from repositories import GameJoinRepository


def main():
    db = Database()
    db.initialize()
    print("[TABLE COUNTS]")
    for table, count in db.table_counts().items():
        print(f"{table}: {count}")

    print("\n[5 TABLE LEFT JOIN]")
    rows = GameJoinRepository(db).find_all()
    for row in rows:
        print(
            row["game_id"],
            row["played_date"],
            row["center_name"],
            row["oil_pattern"],
            row["ball_name"],
            row["score"],
            row["image_path"],
        )


if __name__ == "__main__":
    main()

