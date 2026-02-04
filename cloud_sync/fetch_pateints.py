import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# --- CONFIG ---
SHEET_NAME = "HCB"
OUTPUT_JSON = r"D:\robot_system\data\patients\patients.json"
SYNC_LOG = r"D:\robot_system\data\patients\last_sync.txt"

# --- AUTH ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"D:\robot_system\credentials\service_account.json",
    scope
)
client = gspread.authorize(creds)

# --- FETCH DATA ---
sheet = client.open(SHEET_NAME).sheet1
rows = sheet.get_all_records()

patients = []

for row in rows:
    patient = {
        "patient_id": row["Patient ID"],
        "name": row["Patient Name"],
        "age": int(row["Age"]),
        "language": "en" if row["Language"] == "English" else "hi",
        "medicine": {
            "name": row["Medicine Name"],
            "time": row["Medicine Time"],
            "count": int(row["Medicine Count"])
        },
        "checkup_time": row["Checkup Time"],
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
