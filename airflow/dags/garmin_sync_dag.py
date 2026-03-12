from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

sys.path.insert(0, '/opt/airflow/ingestion')

default_args = {
    'owner':            'garmin_pipeline',
    'retries':          3,
    'retry_delay':      timedelta(minutes=5),
    'email_on_failure': False,
}

with DAG(
    dag_id='garmin_sync_dag',
    description='Fetches running data from Garmin Connect every 30 minutes',
    default_args=default_args,
    schedule_interval='*/30 * * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['garmin', 'running', 'ingestion'],
) as dag:

    def task_fetch_garmin():
        """Pull latest activities from Garmin and load into TimescaleDB."""
        from garmin_ingest import run_ingestion
        run_ingestion(num_activities=50)

    def task_health_check():
        """Confirm DB has data after ingestion."""
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv('/opt/airflow/.env')

        conn = psycopg2.connect(
            host="timescaledb",
            port=5432,
            dbname="garmin_db",
            user="garmin",
            password="garmin123"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM raw_activities;")
        count = cursor.fetchone()[0]

        # Check latest activity timestamp
        cursor.execute("SELECT MAX(start_time) FROM raw_activities;")
        latest = cursor.fetchone()[0]

        conn.close()
        print(f"✅ Health check passed — {count} total activities in DB")
        print(f"✅ Latest activity: {latest}")

        if count == 0:
            raise ValueError("❌ No activities found in database!")

    # ── Task 1: Fetch from Garmin ────────────────────────
    fetch_task = PythonOperator(
        task_id='fetch_garmin_activities',
        python_callable=task_fetch_garmin,
    )

    # ── Task 2: Run dbt transformations ─────────────────
    dbt_task = BashOperator(
        task_id='run_dbt_transformations',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir /opt/airflow/dbt_project',
        env={
            'DBT_PROFILES_DIR': '/opt/airflow/dbt_project',
            'PATH': '/usr/local/bin:/usr/bin:/bin'
        }
    )

    # ── Task 3: Health Check ─────────────────────────────
    health_task = PythonOperator(
        task_id='health_check_db',
        python_callable=task_health_check,
    )

    # ── Pipeline: fetch → dbt → health check ────────────
    fetch_task >> dbt_task >> health_task