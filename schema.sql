CREATE TABLE IF NOT EXISTS bowling_center (
    center_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    lane_count INTEGER CHECK (lane_count > 0),
    memo VARCHAR
);

CREATE TABLE IF NOT EXISTS lane_condition (
    lane_id INTEGER PRIMARY KEY,
    center_id INTEGER NOT NULL REFERENCES bowling_center(center_id),
    oil_pattern VARCHAR(50) NOT NULL,
    oil_length INTEGER CHECK (oil_length BETWEEN 30 AND 50),
    difficulty VARCHAR(20),
    surface_type VARCHAR(30),
    memo VARCHAR
);

CREATE TABLE IF NOT EXISTS bowling_ball (
    ball_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    weight_lbs INTEGER CHECK (weight_lbs BETWEEN 6 AND 16),
    coverstock VARCHAR(50),
    surface_finish VARCHAR(50),
    hook_potential VARCHAR(30),
    image_path VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS game_record (
    game_id INTEGER PRIMARY KEY,
    lane_id INTEGER NOT NULL REFERENCES lane_condition(lane_id),
    played_date DATE NOT NULL,
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 300),
    strike_count INTEGER DEFAULT 0 CHECK (strike_count BETWEEN 0 AND 12),
    spare_count INTEGER DEFAULT 0 CHECK (spare_count BETWEEN 0 AND 10),
    open_frame_count INTEGER DEFAULT 0 CHECK (open_frame_count BETWEEN 0 AND 10),
    average_speed_kmh DOUBLE,
    memo VARCHAR
);

CREATE TABLE IF NOT EXISTS game_ball (
    game_id INTEGER NOT NULL REFERENCES game_record(game_id),
    ball_id INTEGER NOT NULL REFERENCES bowling_ball(ball_id),
    usage_order INTEGER DEFAULT 1,
    purpose VARCHAR(30),
    target_board INTEGER,
    breakpoint_board INTEGER,
    reaction_note VARCHAR,
    PRIMARY KEY (game_id, ball_id)
);

