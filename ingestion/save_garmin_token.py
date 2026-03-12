import os
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

email    = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

print("🔐 Logging in to Garmin...")
client = Garmin(email, password)
client.login()

# Save token
client.garth.dump("garmin_tokens")
print("✅ Token saved!")

# Immediately test activity fetch
print("\n📥 Testing activity fetch...")
activities = client.get_activities(0, 5)
print(f"✅ Found {len(activities)} activities")

for a in activities:
    type_key = a.get("activityType", {}).get("typeKey", "unknown")
    name     = a.get("activityName", "unnamed")
    date     = a.get("startTimeLocal", "unknown")
    print(f"  → {name} | {type_key} | {date}")