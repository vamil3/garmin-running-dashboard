import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from garminconnect import Garmin

# ── Load credentials from .env ──────────────────────────
load_dotenv()

GARMIN_EMAIL    = os.getenv("GARMIN_EMAIL")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")

import socket
# Auto-detect environment — use 'timescaledb' in Docker, 'localhost' otherwise
def get_db_host():
    try:
        socket.gethostbyname("timescaledb")
        return "timescaledb"
    except socket.gaierror:
        return "localhost"

DB_HOST = get_db_host()
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "garmin_db")
DB_USER     = os.getenv("DB_USER", "garmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "garmin123")


def connect_garmin():
    """Log in to Garmin Connect with auto token refresh."""
    print("🔐 Logging in to Garmin Connect...")

    token_path       = "/opt/airflow/garmin_tokens"
    local_token_path = "./garmin_tokens"
    active_token_path = token_path if os.path.exists(token_path) else local_token_path

    if os.path.exists(os.path.join(active_token_path, "oauth2_token.json")):
        print(f"  Loading OAuth tokens from {active_token_path}...")
        try:
            client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
            client.garth.load(active_token_path)
            client.get_full_name()
            print("✅ Garmin token login successful!")
            return client

        except Exception as e:
            print(f"  Token issue ({e}) — doing fresh login...")

    # Fresh login — always saves new token
    print("  Performing fresh login...")
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login()
    os.makedirs(active_token_path, exist_ok=True)
    client.garth.dump(active_token_path)
    print("✅ Fresh login successful, token refreshed!")
    return client


def connect_db():
    """Connect to TimescaleDB and return connection."""
    print("🗄  Connecting to TimescaleDB...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("✅ Database connected!")
    return conn


def parse_activity(activity: dict) -> dict:
    """Extract the fields we care about from a raw Garmin activity."""
    return {
        "activity_id":       activity.get("activityId"),
        "activity_name":     activity.get("activityName"),
        "activity_type":     activity.get("activityType", {}).get("typeKey", "unknown"),
        "start_time":        activity.get("startTimeLocal"),
        "distance_meters":   activity.get("distance"),
        "duration_seconds":  activity.get("duration"),
        "avg_hr":            activity.get("averageHR"),
        "max_hr":            activity.get("maxHR"),
        "avg_pace":          activity.get("averageSpeed"),
        "calories":          activity.get("calories"),
        "elevation_gain":    activity.get("elevationGain"),
        "avg_cadence":       activity.get("averageRunningCadenceInStepsPerMinute"),
        "vo2max":            activity.get("vO2MaxValue"),
        "raw_json":          json.dumps(activity)
    }


def save_activity(cursor, activity: dict):
    """Insert one activity into the database, skip if already exists."""
    cursor.execute("""
        INSERT INTO raw_activities (
            activity_id, activity_name, activity_type,
            start_time, distance_meters, duration_seconds,
            avg_hr, max_hr, avg_pace, calories,
            elevation_gain, avg_cadence, vo2max, raw_json
        )
        VALUES (
            %(activity_id)s, %(activity_name)s, %(activity_type)s,
            %(start_time)s, %(distance_meters)s, %(duration_seconds)s,
            %(avg_hr)s, %(max_hr)s, %(avg_pace)s, %(calories)s,
            %(elevation_gain)s, %(avg_cadence)s, %(vo2max)s, %(raw_json)s
        )
        ON CONFLICT (activity_id) DO NOTHING;
    """, activity)


def run_ingestion(num_activities: int = 100):
    """Main ingestion function — pulls latest activities from Garmin."""

    # Connect to Garmin
    client = connect_garmin()

    # Connect to DB
    conn = connect_db()
    cursor = conn.cursor()

    print(f"\n📥 Fetching ALL running history from Garmin...")

    all_running = []
    batch_size  = 100
    start_index = 0

    # Keep fetching until no more activities come back
    while True:
        print(f"  Fetching batch starting at index {start_index}...")
        batch = client.get_activities(start_index, batch_size)

        # No more activities — we've reached the end
        if not batch:
            break

        # Filter running only from this batch
        running = [a for a in batch if
                   a.get("activityType", {}).get("typeKey", "") == "running"]

        all_running.extend(running)
        print(f"  Found {len(running)} runs in this batch")

        # If batch returned less than we asked for — we've hit the end
        if len(batch) < batch_size:
            break

        start_index += batch_size

    print(f"\n🏃 Total running activities found: {len(all_running)}")

    # Save each one
    saved   = 0
    skipped = 0

    for activity in all_running:
        parsed = parse_activity(activity)
        save_activity(cursor, parsed)
        if cursor.rowcount > 0:
            saved += 1
            print(f"  ✅ Saved: {parsed['activity_name']} — {parsed['start_time']}")
        else:
            skipped += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n🎉 Done! Saved: {saved} new | Skipped: {skipped} duplicates")


if __name__ == "__main__":
    run_ingestion(num_activities=50)