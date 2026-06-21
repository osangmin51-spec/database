INSERT INTO bowling_center
SELECT 1, '구미 중앙볼링장', '경북 구미', 20, '주말 연습 장소'
WHERE NOT EXISTS (SELECT 1 FROM bowling_center WHERE center_id = 1);

INSERT INTO bowling_center
SELECT 2, '금오 볼링클럽', '경북 구미', 16, '학교에서 가까운 볼링장'
WHERE NOT EXISTS (SELECT 1 FROM bowling_center WHERE center_id = 2);

INSERT INTO lane_condition
SELECT 1, 1, '하우스 패턴', 40, '보통', '합성 레인', '중앙은 미끄럽고 바깥쪽은 마찰이 큼'
WHERE NOT EXISTS (SELECT 1 FROM lane_condition WHERE lane_id = 1);

INSERT INTO lane_condition
SELECT 2, 1, '롱 오일', 45, '어려움', '합성 레인', '공이 늦게 휘는 편'
WHERE NOT EXISTS (SELECT 1 FROM lane_condition WHERE lane_id = 2);

INSERT INTO lane_condition
SELECT 3, 2, '숏 오일', 36, '쉬움', '우드 레인', '공이 일찍 휘므로 바깥 라인 사용'
WHERE NOT EXISTS (SELECT 1 FROM lane_condition WHERE lane_id = 3);

INSERT INTO bowling_ball
SELECT 1, '네온 임팩트', 15, '하이브리드 리액티브', '2000 Grit', '중간', 'assets/ball_neon.png'
WHERE NOT EXISTS (SELECT 1 FROM bowling_ball WHERE ball_id = 1);

INSERT INTO bowling_ball
SELECT 2, '블루 궤도', 15, '솔리드 리액티브', '1500 Grit', '강함', 'assets/ball_blue.png'
WHERE NOT EXISTS (SELECT 1 FROM bowling_ball WHERE ball_id = 2);

INSERT INTO bowling_ball
SELECT 3, '스페어 화이트', 14, '폴리에스터', 'Polished', '약함', 'assets/ball_white.png'
WHERE NOT EXISTS (SELECT 1 FROM bowling_ball WHERE ball_id = 3);

INSERT INTO game_record
SELECT 1, 1, DATE '2026-06-03', 184, 5, 3, 2, 24.8, '중반 이후 오른쪽으로 두 보드 이동'
WHERE NOT EXISTS (SELECT 1 FROM game_record WHERE game_id = 1);

INSERT INTO game_record
SELECT 2, 2, DATE '2026-06-08', 211, 7, 2, 1, 25.4, '롱 오일에서 속도를 조금 낮춤'
WHERE NOT EXISTS (SELECT 1 FROM game_record WHERE game_id = 2);

INSERT INTO game_record
SELECT 3, 3, DATE '2026-06-14', 196, 6, 2, 2, 25.1, '바깥쪽 8보드 공략이 안정적이었음'
WHERE NOT EXISTS (SELECT 1 FROM game_record WHERE game_id = 3);

INSERT INTO game_ball
SELECT 1, 1, 1, '첫 투구', 12, 8, '후반부에 각이 커짐'
WHERE NOT EXISTS (SELECT 1 FROM game_ball WHERE game_id = 1 AND ball_id = 1);

INSERT INTO game_ball
SELECT 1, 3, 2, '스페어', 10, 10, '직선으로 스페어 처리'
WHERE NOT EXISTS (SELECT 1 FROM game_ball WHERE game_id = 1 AND ball_id = 3);

INSERT INTO game_ball
SELECT 2, 2, 1, '첫 투구', 14, 9, '오일이 길어 블루 궤도가 안정적'
WHERE NOT EXISTS (SELECT 1 FROM game_ball WHERE game_id = 2 AND ball_id = 2);

INSERT INTO game_ball
SELECT 3, 1, 1, '첫 투구', 10, 7, '마찰 구간에서 일찍 반응함'
WHERE NOT EXISTS (SELECT 1 FROM game_ball WHERE game_id = 3 AND ball_id = 1);

