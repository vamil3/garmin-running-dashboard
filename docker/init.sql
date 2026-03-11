-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Raw activities table
CREATE TABLE IF NOT EXISTS raw_activities (
    id              BIGSERIAL,
    activity_id     BIGINT UNIQUE NOT NULL,
    activity_name   TEXT,
    activity_type   TEXT,
    start_time      TIMESTAMPTZ NOT NULL,
    distance_meters FLOAT,
    duration_seconds FLOAT,
    avg_hr          INT,
    max_hr          INT,
    avg_pace        FLOAT,
    calories        INT,
    elevation_gain  FLOAT,
    avg_cadence     INT,
    vo2max          FLOAT,
    raw_json        JSONB,
    ingested_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable (TimescaleDB superpower for time-series)
SELECT create_hypertable('raw_activities', 'start_time', if_not_exists => TRUE);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_activities_type
    ON raw_activities (activity_type, start_time DESC);