import gspread
import json
import os
import uuid
import cv2
import io

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# =========================
# CONFIG
# =========================

SPREADSHEET_ID = "11NcgmPJXgap8wBcH1jxZ_AKes4o3kDphVZdwa68Ijsc"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATIENT_JSON_PATH = os.path.join(BASE_DIR, "data", "patients", "patients.json")
FACE_DATASET_PATH = os.path.join(BASE_DIR, "face_dataset")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "service_account.json")

os.makedirs(os.path.dirname(PATIENT_JSON_PATH), exist_ok=True)
os.makedirs(FACE_DATASET_PATH, exist_ok=True)

# =========================
# AUTHENTICATION
# =========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_PATH, scope
)

gs_client = gspread.authorize(creds)
sheet = gs_client.open_by_key(SPREADSHEET_ID).sheet1
rows = sheet.get_all_records()

# Print all available column headers for debugging
if rows:
    print("📋 Available columns in sheet:")
    for col in rows[0].keys():
        print(f"  - '{col}'")
    print()

drive_service = build("drive", "v3", credentials=creds)

# =========================
# HELPERS
# =========================

def clean_row(row):
    return {k.strip(): v for k, v in row.items()}

def is_valid_image(path):
    img = cv2.imread(path)
    return img is not None

def download_drive_image(file_id, save_path):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(save_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.close()

# =========================
# LOAD EXISTING DATA
# =========================

existing_patients = []

if os.path.exists(PATIENT_JSON_PATH):
    try:
        with open(PATIENT_JSON_PATH, "r", encoding="utf-8") as f:
            existing_patients = json.load(f).get("patients", [])
    except json.JSONDecodeError:
        existing_patients = []

existing_names = {p["full_name"] for p in existing_patients}

# =========================
# PROCESS NEW PATIENTS
# =========================

for raw_row in rows:
    row = clean_row(raw_row)

    full_name = row.get("Patient full name", "").strip()
    if not full_name or full_name in existing_names:
        continue

    patient_id = f"P_{uuid.uuid4().hex[:8]}"
    patient_face_dir = os.path.join(FACE_DATASET_PATH, patient_id)
    os.makedirs(patient_face_dir, exist_ok=True)

    # -------- Download face images --------
    photo_links = row.get("Patient Photo", "")

    if photo_links:
        links = photo_links.split(",")
        for idx, link in enumerate(links):
            if "id=" not in link:
                continue

            file_id = link.split("id=")[-1]
            img_path = os.path.join(patient_face_dir, f"face_{idx+1}.jpg")

            try:
                download_drive_image(file_id, img_path)

                if not is_valid_image(img_path):
                    os.remove(img_path)
                    print(f"⚠ Invalid image skipped for {patient_id}")

            except Exception as e:
                print("Image download error:", e)

    # -------- Save patient record --------
    # Extract medication times for all 5 doses
    medication_times = []
    for dose_num in range(1, 6):
        # Try multiple column name variations
        possible_keys = [
            f"Medication time  [Dose {dose_num}]",  # Double space
            f"Medication time [Dose {dose_num}]",   # Single space
            f"Medication time[Dose {dose_num}]",    # No space
            f"Medication time  [Dose {dose_num}]",  # With extra spaces
        ]
        
        dose_time = ""
        for key in possible_keys:
            if key in row:
                dose_time = row.get(key, "").strip()
                if dose_time:
                    break
        
        if dose_time:
            medication_times.append(dose_time)
    
    # Debug: Print all column names and medication times found
    if full_name:
        print(f"Processing {full_name}: Found {len(medication_times)} medication times")
        if medication_times:
            print(f"  Medication times: {medication_times}")
    
    patient_record = {
        "patient_id": patient_id,
        "timestamp": row.get("Timestamp", ""),
        "full_name": full_name,
        "patient_photo": row.get("Patient Photo", ""),
        "medical_condition": row.get("Primary Medical Condition", ""),
        "medication_times": medication_times,
        "health_check_frequency": row.get("Health Check Frequency", ""),
        "emergency_contact": row.get("Emergency contact number", ""),
        "special_notes": row.get("Special Notes for AI", ""),
        "active": True
    }

    existing_patients.append(patient_record)
    existing_names.add(full_name)

# =========================
# SAVE JSON
# =========================

with open(PATIENT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump({"patients": existing_patients}, f, indent=4)

print("✅ Patient data synced successfully (IDs + images validated)")
