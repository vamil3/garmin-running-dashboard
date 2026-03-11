# 🏃 Garmin Running Dashboard

> A real-time running analytics pipeline built with 100% open-source tools.
> Automatically syncs Garmin Connect data every 30 minutes into a live Grafana dashboard.

![Pipeline](https://img.shields.io/badge/Pipeline-Airflow-017CEE?style=flat&logo=apacheairflow)
![Database](https://img.shields.io/badge/Database-TimescaleDB-FDB515?style=flat)
![Transform](https://img.shields.io/badge/Transform-dbt-FF694B?style=flat&logo=dbt)
![Dashboard](https://img.shields.io/badge/Dashboard-Grafana-F46800?style=flat&logo=grafana)
![Container](https://img.shields.io/badge/Container-Docker-2496ED?style=flat&logo=docker)

---

## 🏗 Architecture
```
Garmin Watch
     ↓
Garmin Connect (cloud)
     ↓
python-garminconnect (ingestion)
     ↓
Apache Airflow (orchestration — runs every 30 mins)
     ↓
TimescaleDB / PostgreSQL (time-series storage)
     ↓
dbt (staging → facts → marts transformation)
     ↓
Grafana (live dashboard)
```

---

## 📊 Dashboard Features

- **Live sync** — auto-refreshes every 30 minutes via Airflow
- **Weekly distance trends** — 12-week rolling view
- **HR zone distribution** — Z1 through Z5 breakdown
- **Pace zone analysis** — Recovery to Race Pace
- **VO₂ Max tracking** — trend over time
- **Recent runs table** — with effort score, elevation, cadence

---

## 🛠 Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Ingestion | python-garminconnect | Pulls data from Garmin Connect API |
| Orchestration | Apache Airflow 2.8 | Schedules pipeline every 30 mins |
| Database | TimescaleDB (PostgreSQL 15) | Time-series optimized storage |
| Transformation | dbt 1.7 | Staging → Facts → Marts models |
| Visualization | Grafana OSS | Live dashboard with auto-refresh |
| Infrastructure | Docker Compose | Single-command local deployment |

---

## 🚀 Run It Yourself

### Prerequisites
- Docker Desktop
- Python 3.8+
- Garmin Connect account

### Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/garmin-running-dashboard.git
cd garmin-running-dashboard
```

**2. Add your credentials**
```bash
cp .env.example .env
# Edit .env with your Garmin email and password
```

**3. Start the pipeline**
```bash
docker compose up -d
```

**4. Generate Garmin auth token**
```bash
pip install -r requirements.txt
python ingestion/save_garmin_token.py
```

**5. Run initial data load**
```bash
python ingestion/garmin_ingest.py
```

**6. Run dbt transformations**
```bash
cd dbt_project && dbt run
```

**7. Open dashboards**
- Grafana: http://localhost:3000 (admin/admin123)
- Airflow: http://localhost:8080 (admin/admin123)

---

## 📁 Project Structure
```
garmin-running-dashboard/
├── ingestion/
│   ├── garmin_ingest.py        # Main ingestion script
│   └── save_garmin_token.py    # One-time auth token setup
├── airflow/
│   └── dags/
│       └── garmin_sync_dag.py  # Airflow DAG (every 30 mins)
├── dbt_project/
│   └── models/
│       ├── staging/
│       │   └── stg_garmin_activities.sql
│       └── marts/
│           ├── fct_runs.sql
│           └── mart_weekly_summary.sql
├── grafana/
│   ├── dashboards/
│   │   └── running_dashboard.json
│   └── provisioning/
├── docker/
│   └── init.sql                # DB schema + TimescaleDB setup
├── docker-compose.yml
└── requirements.txt
```

---

## 💡 Key Engineering Decisions

- **TimescaleDB over plain PostgreSQL** — hypertables give 10-100x faster time-series queries
- **dbt layered architecture** — raw → staging → facts → marts mirrors production data warehouses
- **Token-based Garmin auth** — OAuth token reuse avoids repeated logins and MFA prompts
- **Docker Compose** — entire stack spins up with one command, fully reproducible

---

## 🔮 Future Improvements

- [ ] Add Azure deployment with Terraform IaC
- [ ] Slack/email alerts for missed Airflow runs  
- [ ] Strava data source integration
- [ ] Predictive race time model using scikit-learn
- [ ] dbt tests and data quality checks

---

*Built as a data engineering portfolio project.*