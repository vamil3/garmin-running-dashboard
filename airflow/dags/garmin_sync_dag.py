from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

# Make our ingestion module importable inside Airflow
sys.path.insert(0, '/opt/airflow/ingestion')

# ── Default settings for all tasks ──────────────────────
default_args = {
    'owner':            'garmin_pipeline',
    'retries':          3,
    'retry_delay':      timedelta(minutes=5),
    'email_on_failure': False,
}

# ── Define the DAG ───────────────────────────────────────
with DAG(
    dag_id='garmin_sync_dag',
    description='Fetches running data from Garmin Connect every 30 minutes',
    default_args=default_args,
    schedule_interval='*/30 * * * *',   # every 30 minutes
    start_date=days_ago(1),
    catchup=False,
    tags=['garmin', 'running', 'ingestion'],
) as dag:

    def task_fetch_garmin():
        """Pull latest activities from Garmin and load into TimescaleDB."""
        from garmin_ingest import run_ingestion
        run_ingestion(num_activities=50)

    def task_health_check():
        """Simple check to confirm DB has data after ingestion."""
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv('/opt/airflow/.env')

        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "timescaledb"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "garmin_db"),
            user=os.getenv("DB_USER", "garmin"),
            password=os.getenv("DB_PASSWORD", "garmin123")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM raw_activities;")
        count = cursor.fetchone()[0]
        conn.close()

        print(f"✅ Health check passed — {count} total activities in DB")
        if count == 0:
            raise ValueError("❌ No activities found in database!")

    # ── Task 1: Fetch from Garmin ────────────────────────
    fetch_task = PythonOperator(
        task_id='fetch_garmin_activities',
        python_callable=task_fetch_garmin,
    )

    # ── Task 2: Health Check ─────────────────────────────
    health_task = PythonOperator(
        task_id='health_check_db',
        python_callable=task_health_check,
    )

    # ── Pipeline order: fetch → health check ────────────
    fetch_task >> health_task