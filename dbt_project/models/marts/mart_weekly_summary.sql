-- Weekly summary: what Grafana will query for the dashboard

WITH runs AS (
    SELECT * FROM {{ ref('fct_runs') }}
),

weekly AS (
    SELECT
        DATE_TRUNC('week', activity_date)    AS week_start,
        COUNT(*)                              AS total_runs,
        ROUND(SUM(distance_km)::numeric, 1)  AS total_km,
        ROUND(AVG(distance_km)::numeric, 1)  AS avg_run_km,
        ROUND(SUM(duration_mins)::numeric, 0) AS total_mins,
        ROUND(AVG(pace_min_per_km)::numeric, 2) AS avg_pace,
        ROUND(AVG(avg_hr)::numeric, 0)       AS avg_hr,
        ROUND(MAX(distance_km)::numeric, 1)  AS longest_run_km,
        ROUND(SUM(calories)::numeric, 0)     AS total_calories,
        ROUND(SUM(elevation_gain_m)::numeric, 0) AS total_elevation_m,

        -- Zone distribution this week
        ROUND(100.0 * SUM(CASE WHEN hr_zone = 'Z1 - Recovery'  THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_z1,
        ROUND(100.0 * SUM(CASE WHEN hr_zone = 'Z2 - Easy'      THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_z2,
        ROUND(100.0 * SUM(CASE WHEN hr_zone = 'Z3 - Aerobic'   THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_z3,
        ROUND(100.0 * SUM(CASE WHEN hr_zone = 'Z4 - Threshold' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_z4,
        ROUND(100.0 * SUM(CASE WHEN hr_zone = 'Z5 - Max'       THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_z5

    FROM runs
    GROUP BY DATE_TRUNC('week', activity_date)
)

SELECT * FROM weekly
ORDER BY week_start DESC