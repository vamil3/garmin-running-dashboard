-- Staging layer: clean and rename raw Garmin data

WITH source AS (
    SELECT * FROM raw_activities
),

cleaned AS (
    SELECT
        activity_id,
        activity_name,
        activity_type,
        start_time                                    AS activity_date,

        -- Distance
        ROUND((distance_meters / 1000.0)::numeric, 2) AS distance_km,

        -- Duration
        ROUND((duration_seconds / 60.0)::numeric, 1)  AS duration_mins,

        -- Pace (seconds per km → min:sec format as decimal)
        CASE
            WHEN distance_meters > 0
            THEN ROUND((duration_seconds / (distance_meters / 1000.0) / 60)::numeric, 2)
        END                                            AS pace_min_per_km,

        -- Heart rate
        avg_hr,
        max_hr,

        -- Other metrics
        calories,
        ROUND(elevation_gain::numeric, 1)              AS elevation_gain_m,
        avg_cadence,
        vo2max,

        ingested_at
    FROM source
    WHERE activity_type = 'running'
      AND distance_meters > 100   -- filter out accidental starts
      AND duration_seconds > 60
)

SELECT * FROM cleaned