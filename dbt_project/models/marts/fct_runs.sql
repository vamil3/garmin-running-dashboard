-- Facts layer: enriched running metrics with performance zones

WITH staging AS (
    SELECT * FROM {{ ref('stg_garmin_activities') }}
),

enriched AS (
    SELECT
        activity_id,
        activity_name,
        activity_date,
        distance_km,
        duration_mins,
        pace_min_per_km,
        avg_hr,
        max_hr,
        calories,
        elevation_gain_m,
        avg_cadence,
        vo2max,

        -- Pace zone classification
        CASE
            WHEN pace_min_per_km < 4.5  THEN 'Race Pace'
            WHEN pace_min_per_km < 5.0  THEN 'Tempo'
            WHEN pace_min_per_km < 5.5  THEN 'Threshold'
            WHEN pace_min_per_km < 6.5  THEN 'Easy'
            ELSE                              'Recovery'
        END AS pace_zone,

        -- HR zone classification
        CASE
            WHEN avg_hr < 115 THEN 'Z1 - Recovery'
            WHEN avg_hr < 135 THEN 'Z2 - Easy'
            WHEN avg_hr < 155 THEN 'Z3 - Aerobic'
            WHEN avg_hr < 170 THEN 'Z4 - Threshold'
            ELSE                   'Z5 - Max'
        END AS hr_zone,

        -- Run type by distance
        CASE
            WHEN distance_km < 6    THEN 'Short Run'
            WHEN distance_km < 12   THEN 'Mid Run'
            WHEN distance_km < 18   THEN 'Long-ish'
            WHEN distance_km < 25   THEN 'Long Run'
            ELSE                         'Ultra/Race'
        END AS run_type,

        -- Effort score (simple composite)
        ROUND((distance_km * 1.0 + elevation_gain_m * 0.01 +
              (avg_hr - 100) * 0.1)::numeric, 1) AS effort_score

    FROM staging
)

SELECT * FROM enriched
ORDER BY activity_date DESC