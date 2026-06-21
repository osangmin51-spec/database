from datetime import date
from typing import Any

from repositories import (
    BowlingBallRepository,
    BowlingCenterRepository,
    GameJoinRepository,
    GameRecordRepository,
    LaneConditionRepository,
)


class BowlingService:
    """UI 입력값 검증과 여러 Repository가 필요한 업무 흐름을 담당한다."""

    def __init__(
        self,
        centers: BowlingCenterRepository,
        lanes: LaneConditionRepository,
        balls: BowlingBallRepository,
        games: GameRecordRepository,
        joins: GameJoinRepository,
    ):
        self.centers = centers
        self.lanes = lanes
        self.balls = balls
        self.games = games
        self.joins = joins

    def save_ball(self, ball_id: int | None, form: dict[str, str]) -> int:
        if not form["name"].strip():
            raise ValueError("볼링공 이름을 입력하세요.")
        try:
            weight = int(form["weight_lbs"])
        except ValueError as exc:
            raise ValueError("무게는 숫자로 입력하세요.") from exc
        if not 6 <= weight <= 16:
            raise ValueError("볼링공 무게는 6~16파운드 범위로 입력하세요.")
        if not form["image_path"].strip():
            raise ValueError("이미지 경로를 입력하세요.")

        data = {
            "name": form["name"].strip(),
            "weight_lbs": weight,
            "coverstock": form["coverstock"].strip(),
            "surface_finish": form["surface_finish"].strip(),
            "hook_potential": form["hook_potential"].strip(),
            "image_path": form["image_path"].strip(),
        }
        if ball_id is None:
            return self.balls.insert(data)
        self.balls.update(ball_id, data)
        return ball_id

    def save_game(self, form: dict[str, str]) -> int:
        required = ["lane_id", "ball_id", "played_date", "score"]
        if any(not form[key] for key in required):
            raise ValueError("날짜, 레인, 볼링공, 점수는 반드시 입력하세요.")
        try:
            score = int(form["score"])
            strike_count = int(form["strike_count"] or 0)
            spare_count = int(form["spare_count"] or 0)
            open_count = int(form["open_frame_count"] or 0)
            speed = float(form["average_speed_kmh"] or 0)
            target = int(form["target_board"] or 0)
            breakpoint = int(form["breakpoint_board"] or 0)
            played = date.fromisoformat(form["played_date"])
        except ValueError as exc:
            raise ValueError("날짜 형식과 숫자 입력값을 확인하세요.") from exc
        if not 0 <= score <= 300:
            raise ValueError("점수는 0~300 범위로 입력하세요.")
        if strike_count + spare_count + open_count < 1:
            raise ValueError("스트라이크, 스페어, 오픈 프레임 수를 입력하세요.")

        return self.games.insert_with_ball(
            {
                "lane_id": int(form["lane_id"]),
                "played_date": played,
                "score": score,
                "strike_count": strike_count,
                "spare_count": spare_count,
                "open_frame_count": open_count,
                "average_speed_kmh": speed,
                "memo": form["memo"].strip(),
            },
            {
                "ball_id": int(form["ball_id"]),
                "purpose": form["purpose"].strip() or "첫 투구",
                "target_board": target,
                "breakpoint_board": breakpoint,
                "reaction_note": form["reaction_note"].strip(),
            },
        )

