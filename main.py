from datetime import date
from pathlib import Path

import flet as ft

from database import Database
from repositories import (
    BowlingBall,
    BowlingBallRepository,
    BowlingCenterRepository,
    GameJoinRepository,
    GameRecordRepository,
    LaneConditionRepository,
)
from services import BowlingService


BASE_DIR = Path(__file__).resolve().parent
BG = "#0D151D"
SIDE = "#121D26"
PANEL = "#18242E"
PANEL_2 = "#202E39"
GREEN = "#42E06F"
GREEN_DARK = "#1EA64A"
TEXT = "#F5F7FA"
MUTED = "#9BABBA"
LINE = "#31414E"
RED = "#FF6B6B"


def text_field(label: str, value: str = "", **kwargs) -> ft.TextField:
    return ft.TextField(
        label=label,
        value=value,
        filled=True,
        fill_color=PANEL_2,
        border_color=LINE,
        focused_border_color=GREEN,
        border_radius=6,
        text_size=14,
        label_style=ft.TextStyle(color=MUTED),
        **kwargs,
    )


def dropdown(label: str, options: list[ft.DropdownOption], value: str | None = None, **kwargs) -> ft.Dropdown:
    return ft.Dropdown(
        label=label,
        options=options,
        value=value,
        filled=True,
        fill_color=PANEL_2,
        border_color=LINE,
        focused_border_color=GREEN,
        border_radius=6,
        text_size=14,
        label_style=ft.TextStyle(color=MUTED),
        **kwargs,
    )


class BowlingTrackerApp:
    """Flet 화면을 조립하고 사용자 이벤트를 Service와 Repository에 연결한다."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.db.initialize()

        self.center_repo = BowlingCenterRepository(self.db)
        self.lane_repo = LaneConditionRepository(self.db)
        self.ball_repo = BowlingBallRepository(self.db)
        self.game_repo = GameRecordRepository(self.db)
        self.join_repo = GameJoinRepository(self.db)
        self.service = BowlingService(
            self.center_repo,
            self.lane_repo,
            self.ball_repo,
            self.game_repo,
            self.join_repo,
        )

        self.selected_view = 0
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.configure_page()
        self.build_shell()
        self.show_view(0)

    def configure_page(self):
        """한국어 스포츠 대시보드에 공통으로 적용할 테마와 창 속성을 설정한다."""
        self.page.title = "투핸드 볼링 트래커"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = BG
        self.page.padding = 0
        self.page.spacing = 0
        self.page.theme = ft.Theme(
            color_scheme_seed=GREEN,
            font_family="Malgun Gothic",
        )

    def build_shell(self):
        """고정 NavigationRail과 화면이 교체되는 콘텐츠 영역을 구성한다."""
        destinations = [
            (ft.Icons.HOME_OUTLINED, ft.Icons.HOME, "대시보드"),
            (ft.Icons.SPORTS_OUTLINED, ft.Icons.SPORTS, "볼링공 관리"),
            (ft.Icons.SCOREBOARD_OUTLINED, ft.Icons.SCOREBOARD, "경기 기록"),
            (ft.Icons.INSIGHTS_OUTLINED, ft.Icons.INSIGHTS, "통합 조회"),
        ]
        self.rail = ft.NavigationRail(
            selected_index=0,
            extended=True,
            min_extended_width=215,
            bgcolor=SIDE,
            indicator_color="#1D5C34",
            leading=ft.Container(
                padding=ft.Padding.only(left=18, top=20, bottom=22),
                content=ft.Row(
                    [
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=8,
                            bgcolor=GREEN,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.SPORTS, color="#07130B", size=25),
                        ),
                        ft.Column(
                            [
                                ft.Text("TWO-HAND", size=17, weight=ft.FontWeight.BOLD, color=TEXT),
                                ft.Text("BOWLING TRACKER", size=10, color=GREEN),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=12,
                ),
            ),
            trailing=ft.Container(
                padding=18,
                content=ft.Column(
                    [
                        ft.Divider(color=LINE),
                        ft.Text("DuckDB 연결됨", color=GREEN, size=12),
                        ft.Text("로컬 데이터베이스", color=MUTED, size=11),
                    ],
                    spacing=3,
                ),
            ),
            destinations=[
                ft.NavigationRailDestination(icon=icon, selected_icon=selected, label=label)
                for icon, selected, label in destinations
            ],
            on_change=lambda e: self.show_view(e.control.selected_index),
        )
        self.page.add(
            ft.Row(
                [
                    self.rail,
                    ft.VerticalDivider(width=1, color=LINE),
                    ft.Container(content=self.content, expand=True, padding=ft.Padding.all(24)),
                ],
                expand=True,
                spacing=0,
            )
        )

    def show_view(self, index: int):
        """선택한 메뉴의 화면만 다시 만들어 최신 DB 상태를 반영한다."""
        self.selected_view = index
        self.rail.selected_index = index
        views = [self.dashboard_view, self.ball_view, self.game_form_view, self.join_view]
        self.content.controls = [views[index]()]
        self.page.update()

    def header(self, title: str, subtitle: str, action: ft.Control | None = None) -> ft.Row:
        controls = [
            ft.Column(
                [
                    ft.Text(title, size=27, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Text(subtitle, size=13, color=MUTED),
                ],
                spacing=3,
                expand=True,
            )
        ]
        if action:
            controls.append(action)
        return ft.Row(controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def stat_card(self, label: str, value: str, detail: str, icon: ft.IconData, color: str) -> ft.Container:
        return ft.Container(
            col={"sm": 6, "lg": 3},
            bgcolor=PANEL,
            border=ft.Border.all(1, LINE),
            border_radius=8,
            padding=18,
            content=ft.Row(
                [
                    ft.Container(
                        width=44,
                        height=44,
                        border_radius=8,
                        bgcolor=f"{color}22",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(icon, color=color, size=24),
                    ),
                    ft.Column(
                        [
                            ft.Text(label, color=MUTED, size=12),
                            ft.Text(value, color=TEXT, size=25, weight=ft.FontWeight.BOLD),
                            ft.Text(detail, color=color, size=11),
                        ],
                        spacing=1,
                    ),
                ],
                spacing=13,
            ),
        )

    def dashboard_view(self) -> ft.Control:
        """집계값, 최근 JOIN 결과, 테이블 행 수를 첫 화면에 요약한다."""
        summary = self.join_repo.summary()
        recent = self.join_repo.find_all()[:4]
        stat_cards = ft.ResponsiveRow(
            [
                self.stat_card("전체 경기", str(summary["games"]), "누적 기록", ft.Icons.CALENDAR_MONTH, GREEN),
                self.stat_card("평균 점수", str(summary["average"]), "최근 데이터 기준", ft.Icons.INSIGHTS, "#59B8FF"),
                self.stat_card("최고 점수", str(summary["high"]), "개인 최고 기록", ft.Icons.EMOJI_EVENTS, "#FFC857"),
                self.stat_card("스트라이크", str(summary["strikes"]), "누적 횟수", ft.Icons.FLASH_ON, "#FF7F6E"),
            ],
            spacing=14,
            run_spacing=14,
        )

        recent_rows = []
        for row in recent:
            recent_rows.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    border=ft.Border(bottom=ft.BorderSide(1, LINE)),
                    content=ft.Row(
                        [
                            ft.Container(
                                width=48,
                                height=48,
                                border_radius=6,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                content=ft.Image(src=row["image_path"], fit=ft.BoxFit.COVER),
                            ),
                            ft.Column(
                                [
                                    ft.Text(str(row["played_date"]), color=TEXT, weight=ft.FontWeight.BOLD),
                                    ft.Text(f'{row["center_name"]} · {row["oil_pattern"]}', color=MUTED, size=12),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Text(row["ball_name"] or "미지정", color=MUTED, size=12),
                            ft.Text(str(row["score"]), color=GREEN, size=23, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                )
            )

        table_counts = self.db.table_counts()
        db_status = ft.Container(
            bgcolor=PANEL,
            border=ft.Border.all(1, LINE),
            border_radius=8,
            padding=18,
            col={"sm": 12, "lg": 4},
            content=ft.Column(
                [
                    ft.Text("데이터베이스 상태", size=17, weight=ft.FontWeight.BOLD),
                    ft.Text("5개 테이블 데이터 삽입 결과", size=12, color=MUTED),
                    ft.Divider(color=LINE),
                    *[
                        ft.Row(
                            [
                                ft.Text(name, color=MUTED, expand=True, size=12),
                                ft.Text(f"{count}건", color=TEXT, weight=ft.FontWeight.BOLD),
                            ]
                        )
                        for name, count in table_counts.items()
                    ],
                    ft.Container(height=5),
                    ft.Row(
                        [ft.Icon(ft.Icons.CHECK_CIRCLE, color=GREEN, size=17), ft.Text("DuckDB 정상 연결", color=GREEN, size=12)]
                    ),
                ],
                spacing=8,
            ),
        )

        recent_panel = ft.Container(
            bgcolor=PANEL,
            border=ft.Border.all(1, LINE),
            border_radius=8,
            col={"sm": 12, "lg": 8},
            content=ft.Column(
                [
                    ft.Container(
                        padding=16,
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("최근 경기", size=17, weight=ft.FontWeight.BOLD),
                                        ft.Text("5개 테이블 LEFT JOIN 결과", color=MUTED, size=12),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.TextButton("전체 보기", icon=ft.Icons.ARROW_FORWARD, on_click=lambda e: self.show_view(3)),
                            ]
                        ),
                    ),
                    *recent_rows,
                ],
                spacing=0,
            ),
        )

        return ft.Column(
            [
                self.header("나의 볼링 기록", "투핸드 볼러의 경기와 장비 반응을 한곳에서 관리합니다."),
                ft.Container(height=6),
                stat_cards,
                ft.Container(height=4),
                ft.ResponsiveRow([recent_panel, db_status], spacing=14, run_spacing=14),
            ],
            spacing=14,
        )

    def ball_view(self) -> ft.Control:
        """볼링공 검색 입력과 이미지 카드 목록을 표시한다."""
        keyword = text_field("이름 또는 재질 검색", width=320, prefix_icon=ft.Icons.SEARCH)
        cards = ft.ResponsiveRow(spacing=14, run_spacing=14)

        def refresh(_=None):
            cards.controls = [self.ball_card(ball) for ball in self.ball_repo.find_all(keyword.value or "")]
            self.page.update()

        keyword.on_submit = refresh
        refresh_button = ft.Button("검색", icon=ft.Icons.SEARCH, bgcolor=GREEN_DARK, color=TEXT, on_click=refresh)
        add_button = ft.Button(
            "볼링공 추가",
            icon=ft.Icons.ADD,
            bgcolor=GREEN,
            color="#07130B",
            on_click=lambda e: self.open_ball_dialog(None),
        )
        refresh()
        return ft.Column(
            [
                self.header("볼링공 관리", "이미지 경로를 DB에 저장하고 장비별 특성을 관리합니다.", add_button),
                ft.Row([keyword, refresh_button]),
                cards,
            ],
            spacing=16,
        )

    def ball_card(self, ball: BowlingBall) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6, "xl": 4},
            bgcolor=PANEL,
            border=ft.Border.all(1, LINE),
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column(
                [
                    ft.Container(
                        height=165,
                        content=ft.Image(src=ball.image_path, fit=ft.BoxFit.COVER, width=500, height=165),
                    ),
                    ft.Container(
                        padding=16,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(ball.name, size=19, weight=ft.FontWeight.BOLD, expand=True),
                                        ft.Container(
                                            bgcolor="#244231",
                                            border_radius=5,
                                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                            content=ft.Text(f"{ball.weight_lbs} lb", color=GREEN, size=11),
                                        ),
                                    ]
                                ),
                                ft.Text(ball.coverstock, color=MUTED, size=12),
                                ft.Row(
                                    [
                                        ft.Text(f"표면 {ball.surface_finish}", color=MUTED, size=11, expand=True),
                                        ft.Text(f"훅 {ball.hook_potential}", color=MUTED, size=11),
                                    ]
                                ),
                                ft.Divider(color=LINE),
                                ft.Row(
                                    [
                                        ft.TextButton("수정", icon=ft.Icons.EDIT_OUTLINED, on_click=lambda e: self.open_ball_dialog(ball)),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_color=RED,
                                            tooltip="볼링공 삭제",
                                            on_click=lambda e: self.delete_ball(ball.ball_id),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                            spacing=8,
                        ),
                    ),
                ],
                spacing=0,
            ),
        )

    def open_ball_dialog(self, ball: BowlingBall | None):
        """ball 값의 유무에 따라 등록 또는 수정 다이얼로그를 연다."""
        name = text_field("볼링공 이름", ball.name if ball else "")
        weight = text_field("무게(lb)", str(ball.weight_lbs) if ball else "15")
        cover = text_field("커버스톡(겉면 재질)", ball.coverstock if ball else "하이브리드 리액티브")
        surface = text_field("표면 처리", ball.surface_finish if ball else "2000 Grit")
        hook = dropdown(
            "훅 성향(휘어지는 정도)",
            [ft.DropdownOption(key=v, text=v) for v in ["약함", "중간", "강함"]],
            value=ball.hook_potential if ball else "중간",
        )
        image_path = dropdown(
            "DB에 저장할 이미지 경로",
            [
                ft.DropdownOption(key="assets/ball_neon.png", text="assets/ball_neon.png"),
                ft.DropdownOption(key="assets/ball_blue.png", text="assets/ball_blue.png"),
                ft.DropdownOption(key="assets/ball_white.png", text="assets/ball_white.png"),
            ],
            value=ball.image_path if ball else "assets/ball_neon.png",
        )
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("볼링공 수정" if ball else "새 볼링공 등록"),
            content=ft.Container(
                width=480,
                content=ft.Column([name, weight, cover, surface, hook, image_path], tight=True, spacing=12),
            ),
            actions=[
                ft.TextButton("취소", on_click=lambda e: self.close_dialog(dialog)),
                ft.Button(
                    "저장",
                    icon=ft.Icons.SAVE,
                    bgcolor=GREEN,
                    color="#07130B",
                    on_click=lambda e: self.save_ball_dialog(
                        dialog,
                        ball.ball_id if ball else None,
                        name,
                        weight,
                        cover,
                        surface,
                        hook,
                        image_path,
                    ),
                ),
            ],
        )
        self.page.show_dialog(dialog)

    def save_ball_dialog(self, dialog, ball_id, name, weight, cover, surface, hook, image_path):
        try:
            saved_id = self.service.save_ball(
                ball_id,
                {
                    "name": name.value or "",
                    "weight_lbs": weight.value or "",
                    "coverstock": cover.value or "",
                    "surface_finish": surface.value or "",
                    "hook_potential": hook.value or "",
                    "image_path": image_path.value or "",
                },
            )
            self.close_dialog(dialog)
            self.notify(f"볼링공 #{saved_id} 정보가 DB에 저장되었습니다.")
            self.show_view(1)
        except Exception as exc:
            self.notify(str(exc), error=True)

    def delete_ball(self, ball_id: int):
        try:
            self.ball_repo.delete(ball_id)
            self.notify("볼링공이 삭제되었습니다.")
            self.show_view(1)
        except Exception as exc:
            self.notify(str(exc), error=True)

    def game_form_view(self) -> ft.Control:
        """경기와 사용 공 관계를 한 번에 입력하는 Flet 폼을 구성한다."""
        lanes = self.lane_repo.find_all()
        balls = self.ball_repo.find_all()
        played = text_field("경기 날짜", date.today().isoformat(), width=220)
        lane = dropdown(
            "볼링장 · 레인 상태",
            [
                ft.DropdownOption(
                    key=str(item["lane_id"]),
                    text=f'{item["center_name"]} / {item["oil_pattern"]} ({item["oil_length"]}ft)',
                )
                for item in lanes
            ],
            value=str(lanes[0]["lane_id"]) if lanes else None,
            expand=True,
        )
        ball = dropdown(
            "사용 볼링공",
            [ft.DropdownOption(key=str(item.ball_id), text=f"{item.name} · {item.weight_lbs}lb") for item in balls],
            value=str(balls[0].ball_id) if balls else None,
            expand=True,
        )
        score = text_field("점수(0~300)", "180")
        strikes = text_field("스트라이크 수", "5")
        spares = text_field("스페어 수", "3")
        opens = text_field("오픈 프레임 수", "2")
        speed = text_field("평균 구속(km/h)", "24.5")
        purpose = dropdown(
            "사용 목적",
            [ft.DropdownOption(key=v, text=v) for v in ["첫 투구", "스페어", "레인 변화 대응"]],
            value="첫 투구",
        )
        target = text_field("에임 보드", "12")
        breakpoint = text_field("브레이크포인트 보드", "8")
        reaction = text_field("공 반응 메모", "핀 앞에서 안정적으로 휘어 들어감", multiline=True, min_lines=2)
        memo = text_field("경기 메모", "", multiline=True, min_lines=2)

        def save(_):
            try:
                game_id = self.service.save_game(
                    {
                        "played_date": played.value or "",
                        "lane_id": lane.value or "",
                        "ball_id": ball.value or "",
                        "score": score.value or "",
                        "strike_count": strikes.value or "",
                        "spare_count": spares.value or "",
                        "open_frame_count": opens.value or "",
                        "average_speed_kmh": speed.value or "",
                        "purpose": purpose.value or "",
                        "target_board": target.value or "",
                        "breakpoint_board": breakpoint.value or "",
                        "reaction_note": reaction.value or "",
                        "memo": memo.value or "",
                    }
                )
                self.notify(f"경기 #{game_id}와 사용 공 관계가 함께 저장되었습니다.")
                self.show_view(3)
            except Exception as exc:
                self.notify(str(exc), error=True)

        form = ft.Container(
            bgcolor=PANEL,
            border=ft.Border.all(1, LINE),
            border_radius=8,
            padding=20,
            content=ft.Column(
                [
                    ft.Row([played, lane]),
                    ball,
                    ft.ResponsiveRow(
                        [
                            ft.Container(content=score, col={"sm": 6, "lg": 3}),
                            ft.Container(content=strikes, col={"sm": 6, "lg": 3}),
                            ft.Container(content=spares, col={"sm": 6, "lg": 3}),
                            ft.Container(content=opens, col={"sm": 6, "lg": 3}),
                        ],
                        spacing=12,
                        run_spacing=12,
                    ),
                    ft.Row([speed, purpose]),
                    ft.Row([target, breakpoint]),
                    reaction,
                    memo,
                    ft.Row(
                        [
                            ft.Text("game_record + game_ball 트랜잭션 저장", color=MUTED, size=12, expand=True),
                            ft.Button("경기 저장", icon=ft.Icons.SAVE, bgcolor=GREEN, color="#07130B", on_click=save),
                        ]
                    ),
                ],
                spacing=13,
            ),
        )
        return ft.Column(
            [
                self.header("경기 기록 입력", "점수와 레인 상태, 사용 볼링공의 반응을 함께 기록합니다."),
                form,
            ],
            spacing=16,
        )

    def join_view(self) -> ft.Control:
        """5개 테이블 LEFT JOIN 결과를 검색 가능한 카드 목록으로 출력한다."""
        keyword = text_field("날짜·볼링장·볼링공 검색", width=330, prefix_icon=ft.Icons.SEARCH)
        body = ft.Column(spacing=12)

        def refresh(_=None):
            rows = self.join_repo.find_all(keyword.value or "")
            body.controls = [self.join_result_card(row) for row in rows]
            if not rows:
                body.controls = [ft.Text("검색 결과가 없습니다.", color=MUTED)]
            self.page.update()

        keyword.on_submit = refresh
        refresh()
        return ft.Column(
            [
                self.header(
                    "경기 통합 조회",
                    "bowling_center → lane_condition → game_record → game_ball → bowling_ball LEFT JOIN",
                ),
                ft.Row(
                    [
                        keyword,
                        ft.Button("조회", icon=ft.Icons.SEARCH, bgcolor=GREEN_DARK, color=TEXT, on_click=refresh),
                        ft.Container(expand=True),
                        ft.Container(
                            bgcolor="#183525",
                            border_radius=6,
                            padding=ft.Padding.symmetric(horizontal=12, vertical=9),
                            content=ft.Text("5 TABLE LEFT JOIN", color=GREEN, size=12, weight=ft.FontWeight.BOLD),
                        ),
                    ]
                ),
                body,
            ],
            spacing=16,
        )

    def join_result_card(self, row: dict) -> ft.Container:
        return ft.Container(
            bgcolor=PANEL,
            border=ft.Border.all(1, LINE),
            border_radius=8,
            padding=14,
            content=ft.Row(
                [
                    ft.Container(
                        width=92,
                        height=92,
                        border_radius=6,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(src=row["image_path"], fit=ft.BoxFit.COVER),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(str(row["played_date"]), size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f'#{row["game_id"]}', color=MUTED, size=11),
                                ]
                            ),
                            ft.Text(f'{row["center_name"]} · {row["region"]}', color=MUTED, size=12),
                            ft.Text(
                                f'{row["oil_pattern"]} {row["oil_length"]}ft · 난이도 {row["difficulty"]}',
                                color=MUTED,
                                size=12,
                            ),
                            ft.Text(
                                f'{row["ball_name"]} · {row["purpose"]} · 에임 {row["target_board"]} / 변곡 {row["breakpoint_board"]}',
                                color=TEXT,
                                size=12,
                            ),
                            ft.Text(row["reaction_note"] or "반응 메모 없음", color=GREEN, size=11),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text(str(row["score"]), size=30, weight=ft.FontWeight.BOLD, color=GREEN),
                            ft.Text(f'X {row["strike_count"]}  / {row["spare_count"]}', color=MUTED, size=11),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=1,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        tooltip="점수와 메모 수정",
                        on_click=lambda e: self.open_game_edit_dialog(row),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=RED,
                        tooltip="경기 삭제",
                        on_click=lambda e: self.delete_game(row["game_id"]),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def open_game_edit_dialog(self, row: dict):
        """기존 JOIN 결과를 이용해 점수와 메모 수정 창을 연다."""
        score = text_field("점수", str(row["score"]))
        memo = text_field("경기 메모", row["memo"] or "", multiline=True, min_lines=3)
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f'경기 #{row["game_id"]} 수정'),
            content=ft.Container(width=430, content=ft.Column([score, memo], tight=True, spacing=12)),
            actions=[
                ft.TextButton("취소", on_click=lambda e: self.close_dialog(dialog)),
                ft.Button(
                    "변경 저장",
                    icon=ft.Icons.SAVE,
                    bgcolor=GREEN,
                    color="#07130B",
                    on_click=lambda e: self.save_game_edit(dialog, row["game_id"], score, memo),
                ),
            ],
        )
        self.page.show_dialog(dialog)

    def save_game_edit(self, dialog, game_id: int, score_field, memo_field):
        try:
            score = int(score_field.value)
            if not 0 <= score <= 300:
                raise ValueError("점수는 0~300 범위로 입력하세요.")
            self.game_repo.update_score(game_id, score, memo_field.value or "")
            self.close_dialog(dialog)
            self.notify("경기 기록이 변경되었습니다.")
            self.show_view(3)
        except Exception as exc:
            self.notify(str(exc), error=True)

    def delete_game(self, game_id: int):
        try:
            self.game_repo.delete(game_id)
            self.notify(f"경기 #{game_id}가 관계 데이터와 함께 삭제되었습니다.")
            self.show_view(3)
        except Exception as exc:
            self.notify(str(exc), error=True)

    def close_dialog(self, dialog: ft.AlertDialog):
        dialog.open = False
        self.page.update()

    def notify(self, message: str, error: bool = False):
        """성공과 오류를 색상으로 구분한 SnackBar를 표시한다."""
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor="#6A2730" if error else "#174A2A",
                show_close_icon=True,
            )
        )


def main(page: ft.Page):
    BowlingTrackerApp(page)


if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        host="127.0.0.1",
        port=8550,
        assets_dir=str(BASE_DIR),
    )
