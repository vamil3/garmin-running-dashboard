# 🏃 Garmin Running Dashboard

A real-time running analytics pipeline built with 100% open-source tools.

## Tech Stack
| Layer | Tool |
|---|---|
| Data Extraction | python-garminconnect |
| Orchestration | Apache Airflow |
| Database | TimescaleDB (PostgreSQL) |
| Transformation | dbt |
| Visualization | Grafana |
| Infrastructure | Docker Compose |

## Architecture
Garmin Watch → Garmin Connect → Python Ingestion → Airflow DAG → TimescaleDB → dbt → Grafana

## Setup
See `/docs` for step-by-step setup guide.

## Author
Built as a data engineering portfolio project.