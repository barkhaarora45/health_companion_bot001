import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# --- CONFIG ---
SHEET_NAME = "Health Companion Robot (Responses)"
OUTPUT_JSON = r"/Volumes/Macintosh/sahay/health_companion_bot001/data/patients/patients.json"
SYNC_LOG = r"/Volumes/Macintosh/sahay/health_companion_bot001/data/patients/last_sync.txt"

# --- AUTH ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"/Volumes/Macintosh/sahay/health_companion_bot001/credentials/service_account.json",
    scope
)
client = gspread.authorize(creds)

# --- FETCH DATA ---
sheet = client.open(SHEET_NAME).sheet1
rows = sheet.get_all_records()

patients = []

for idx, row in enumerate(rows):
    # Collect dose times (skip empty ones)
    dose_times = []
    for i in range(1, 6):
        time = row.get(f"Dose {i} Time")
        if time:
            dose_times.append(time)

    patient = {
        "patient_id": f"PAT_{idx+1}",

        "name": row.get("Patient Full Name"),

        "age": int(row.get("Enter Age", 0)),

        "photo": row.get("Patient Photo"),

        "conditions": row.get("Medical Condition"),

        "medication_times": dose_times,

        "check_frequency": row.get("Health Check Frequency"),

        "emergency_contact": row.get("Emergency contact number"),

        "notes": row.get("Add Special Notes for AI"),

        "active": True
    }
    patients.append(patient)

# --- SAVE JSON ---
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"patients": patients}, f, indent=4)

# --- SAVE SYNC TIME ---
with open(SYNC_LOG, "w") as f:
    f.write(datetime.now().isoformat())

print("Patient data synced successfully.")
