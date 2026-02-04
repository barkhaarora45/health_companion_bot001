import json
import os
import datetime

# ==============================
# CONFIG
# ==============================

PATIENTS_JSON = os.path.join(
    os.path.dirname(__file__),
    "..", "data", "patients", "patients.json"
)

# memory to avoid repeated triggers
triggered_events = set()

# ==============================
# LOAD PATIENTS
# ==============================

def load_patients():
    with open(PATIENTS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)["patients"]

# ==============================
# CHECK SCHEDULE
# ==============================

def check_time_events():
    patients = load_patients()

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    for patient in patients:
        pid = patient["patient_id"]
        name = patient.get("preferred_name", patient["full_name"])

        # MEDICINE TIMES
        for t in patient.get("medication_times", []):
            event_id = f"{today}_{pid}_MEDICINE_{t}"

            if current_time == t and event_id not in triggered_events:
                triggered_events.add(event_id)
                print(f"[{current_time}] MEDICINE EVENT for {name}")
                return {
                    "event": "MEDICINE",
                    "patient_id": pid,
                    "patient_name": name
                }

        # CHECKUP TIMES
        for t in patient.get("checkup_times", []):
            event_id = f"{today}_{pid}_CHECKUP_{t}"

            if current_time == t and event_id not in triggered_events:
                triggered_events.add(event_id)
                print(f"[{current_time}] CHECKUP EVENT for {name}")
                return {
                    "event": "CHECKUP",
                    "patient_id": pid,
                    "patient_name": name
                }

    return None

# ==============================
# TEST LOOP (ONLY FOR NOW)
# ==============================

if __name__ == "__main__":
    print("⏰ Time Scheduler started (Ctrl+C to stop)\n")

    while True:
        event = check_time_events()

        if event is None:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] No scheduled event")

        # check every 30 seconds
        time_to_sleep = 30
        try:
            import time
            time.sleep(time_to_sleep)
        except KeyboardInterrupt:
            print("\nScheduler stopped")
            break
