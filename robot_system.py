import time
import os
import json

from logic.time_scheduler import check_time_events
from logic.patient_context import load_patient_context
from voice.chatnew import chat
from voice.chatnew import run_conversation
from voice.voice_io import speak

# ==============================
# GLOBAL STATE
# ==============================

CURRENT_EVENT = None
WAITING_FOR_FACE = False
ROBOT_MOVING = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACE_EVENT_FILE = os.path.join(BASE_DIR, "runtime", "face_event.json")

# ==============================
# FACE EVENT READER
# ==============================

def check_face_event():
    if not os.path.exists(FACE_EVENT_FILE):
        return None

    with open(FACE_EVENT_FILE, "r") as f:
        data = json.load(f)

    os.remove(FACE_EVENT_FILE)
    return data.get("patient_id")

# ==============================
# FACE CALLBACK
# ==============================

def on_face_event(patient_id):
    global CURRENT_EVENT, WAITING_FOR_FACE

    print(f"[CONTROLLER] Face verified: {patient_id}")

    patient = load_patient_context(patient_id)
    if not patient:
        print("[CONTROLLER] Patient not found")
        WAITING_FOR_FACE = False
        return

    if CURRENT_EVENT["event"] == "MEDICINE":
        prompt = f"Hello {patient['preferred_name']}, it is time for your medicine."
    else:
        prompt = f"Hello {patient['preferred_name']}, it is time for your health checkup."
    speak(prompt)
    run_conversation()
    reply = chat(prompt)
    speak(reply)

    WAITING_FOR_FACE = False
    CURRENT_EVENT = None

# ==============================
# MAIN LOOP
# ==============================

def run_controller():
    global CURRENT_EVENT, WAITING_FOR_FACE, ROBOT_MOVING

    print("🤖 Robot Controller started")

    while True:
        event = check_time_events()

        if event and not WAITING_FOR_FACE and not ROBOT_MOVING:
            CURRENT_EVENT = event
            ROBOT_MOVING = True

            print(f"[CONTROLLER] Event triggered: {event['event']} for {event['patient_name']}")
            print("Moving robot to patient bed...")
            time.sleep(3)

            ROBOT_MOVING = False
            WAITING_FOR_FACE = True
            print("Robot reached patient bed")
            print("Waiting for face recognition...")

        if WAITING_FOR_FACE:
            patient_id = check_face_event()
            if patient_id:
                on_face_event(patient_id)

        time.sleep(1)

if __name__ == "__main__":
    run_controller()
