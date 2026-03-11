import os
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

email    = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

print("🔐 Logging in to Garmin to save session token...")

client = Garmin(email, password)
client.login()

# Save the session token to a local folder
client.garth.dump("garmin_tokens")

print("✅ Token saved to ./garmin_tokens folder!")
print("This token will be shared with Docker so Airflow can log in silently.")