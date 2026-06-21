# Two-Hand Bowling Tracker

Flet과 DuckDB로 구현한 개인용 투핸드 볼링 경기·장비 기록 애플리케이션입니다. 경기 점수뿐 아니라 볼링장, 레인 상태, 사용한 볼링공, 투구 위치와 공의 반응을 관계형 데이터로 함께 저장합니다.

## 실행 화면

![대시보드](docs/screenshots/dashboard.png)

| 볼링공 관리 | 경기 기록 입력 |
|---|---|
| ![볼링공 관리](docs/screenshots/ball-management.png) | ![경기 기록 입력](docs/screenshots/game-form.png) |

![5개 테이블 LEFT JOIN 통합 조회](docs/screenshots/join-result.png)

## 과제 제한 요소

| 요구 사항 | 구현 내용 |
|---|---|
| 테이블 3개 이상 | Entity와 Relationship을 포함한 5개 테이블 생성 |
| 데이터 삽입 | `seed.sql`로 모든 테이블의 초기 데이터 삽입 |
| 3개 이상 테이블 JOIN | 5개 테이블 `LEFT JOIN` 통합 조회 |
| Flet GUI | 한국어 대시보드, 장비 관리, 경기 입력, 통합 조회 구현 |
| DuckDB 접근 | Repository 계층에서 매개변수 바인딩 SQL 실행 |
| 이미지 저장·출력 | DB에 상대 경로를 저장하고 Flet `Image`로 출력 |
| CRUD | 볼링공 및 경기 기록의 조회·등록·변경·삭제 |

## 전체 구조

![애플리케이션 전체 구조](docs/screenshots/architecture.png)

- `main.py`: Flet 화면과 사용자 이벤트 처리
- `services.py`: 입력값 검증과 Use Case 흐름 제어
- `repositories.py`: 테이블 CRUD와 5개 테이블 JOIN
- `database.py`: DuckDB 연결과 스키마 초기화
- `schema.sql`: 테이블, PK/FK, CHECK 제약조건
- `seed.sql`: 볼링장·레인·볼링공·경기 초기 데이터
- `tests/test_repositories.py`: Repository와 DuckDB 통합 테스트

화면에서 발생한 이벤트는 Flet Page가 받고 Service가 입력값과 Use Case 흐름을 처리한 뒤 Repository가 DuckDB에 접근합니다. Repository 객체는 Service 생성자에 전달하여 화면 코드와 SQL 코드가 직접 결합되지 않도록 구성했습니다. 이번 과제는 DuckDB 사용이 명확하므로 여러 DBMS를 동적으로 교체하는 구조는 추가하지 않았습니다.

## 데이터베이스 설계

![Crow's feet ERD](docs/screenshots/erd.png)

ERD는 수업에서 사용한 VSCode ERD Editor로 작성했으며, Crow's feet 표기법으로 필수 참여와 일대다 관계를 나타냈습니다. 편집 가능한 원본은 [`docs/design/two_hand_bowling_tracker.erd`](docs/design/two_hand_bowling_tracker.erd)입니다.

| 테이블 | 구분 | 역할 |
|---|---|---|
| `bowling_center` | Entity | 볼링장 이름과 지역 |
| `lane_condition` | Entity | 볼링장별 오일 패턴과 난이도 |
| `bowling_ball` | Entity | 보유 볼링공 정보와 이미지 경로 |
| `game_record` | Entity | 경기 날짜, 점수, 프레임 결과와 메모 |
| `game_ball` | Relationship | 경기와 사용 볼링공의 다대다 관계 |

통합 조회에서는 경기 정보가 관계 데이터 누락 때문에 사라지지 않도록 `LEFT JOIN`을 사용합니다.

```sql
FROM game_record g
LEFT JOIN lane_condition l ON l.lane_id = g.lane_id
LEFT JOIN bowling_center c ON c.center_id = l.center_id
LEFT JOIN game_ball gb ON gb.game_id = g.game_id
LEFT JOIN bowling_ball b ON b.ball_id = gb.ball_id
```

각 테이블은 원자값만 저장하도록 1NF를 만족시키고, 복합키를 사용하는 `game_ball`에는 키 전체에 종속되는 속성만 두었습니다. 볼링장, 레인 상태, 볼링공과 경기 기록을 분리하여 부분 함수 종속과 이행 함수 종속을 제거했으며, 모든 결정자가 후보키가 되도록 BCNF까지 검토했습니다.

## 수업 내용 반영

| 수업 주제 | 프로젝트 적용 내용 |
|---|---|
| Use Case와 Sequence Diagram | 사용자 관점의 5개 기능을 정의하고 Page-Service-Repository-DuckDB 흐름으로 대응 |
| Repository 설계 | 테이블 CRUD와 5개 테이블 JOIN 책임을 Repository 계층에 분리 |
| VSCode ERD Editor | 편집 가능한 `.erd` 원본과 Crow's feet ERD 제공 |
| DuckDB | 파일 기반 DB 연결, `execute()`, `?` Parameter Binding, 트랜잭션 사용 |
| Flet | `Page`, `Row`, `Column`, `Container`, 입력 컨트롤, 이벤트와 `page.update()` 사용 |

수업 예제의 pandas DataFrame과 여러 DBMS Repository 교체 기능은 현재 요구사항에 필요하지 않아 억지로 추가하지 않았습니다. 실제 구현 범위와 설계상의 확장 가능성을 구분해 기록했습니다.

## 최종 보고서

- [데이터베이스 Term Project 최종 결과 보고서](docs/report/final-report.docx)
- 보고서에는 Use Case, UI Design, Crow's feet ERD, SQL DDL, BCNF 정규화, Sequence Diagram, Repository Interface 설계, 구현 코드와 실행 증빙을 포함했습니다.

## 사용 기술

- Python 3
- Flet 0.85.3
- DuckDB 1.5.4
- Pillow 12.2.0

## 수업 자료

- [아키텍처 설계](https://nano5.notion.site/355daf211d42807e8f60ca7eca521f69)
- [설계서 작성](https://nano5.notion.site/365daf211d4280dcbd33eb1645b30a4f)
- [ERD와 정규화](https://nano5.notion.site/ERD-318daf211d42812c901dfea36b4b03a0)
- [DuckDB](https://nano5.notion.site/DuckDB-350daf211d4280189a1ecaa5ca2da47b)
- [Flet](https://nano5.notion.site/Flet-34fdaf211d428077aec0f5d2cff2c1a9?v=318daf211d42814d9beb000c97572fd2)
