import json
import os

PATIENTS_JSON = os.path.join(
    os.path.dirname(__file__),
    "..", "data", "patients", "patients.json"
)

def load_patient_context(patient_id):
    with open(PATIENTS_JSON, "r", encoding="utf-8") as f:
        patients = json.load(f)["patients"]

    for p in patients:
        if p["patient_id"] == patient_id:
            return {
                "patient_id": p["patient_id"],
                "full_name": p["full_name"],
                "preferred_name": p.get("preferred_name", p["full_name"]),
                "medical_condition": p.get("medical_condition", ""),
                "notes": p.get("notes", ""),
                "medicine_times": p.get("medicine_times", [])
            }

    return None
