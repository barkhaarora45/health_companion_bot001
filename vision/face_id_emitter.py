import cv2
import json
import time
import os
import numpy as np
import mediapipe as mp
from collections import deque
from deepface import DeepFace

# ==============================
# CONFIGURATION
# ==============================

EMBEDDINGS_PATH = r"D:\robot_system\vision\embeddings.json"

MODEL_NAME = "ArcFace"

KNOWN_THRESHOLD = 0.70
UNKNOWN_THRESHOLD = 0.60

KNOWN_CONFIRM_TIME = 1.0
UNKNOWN_CONFIRM_TIME = 1.5

HISTORY_LEN = 6
UNKNOWN_RATIO = 0.66
FRAME_SKIP = 8

ROI_X1, ROI_Y1 = 150, 200
ROI_X2, ROI_Y2 = 500, 450

STATE_ANALYZING = 0
STATE_KNOWN = 1
STATE_UNKNOWN = 2

# ==============================
# EVENT FILE SETUP
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVENT_DIR = os.path.join(BASE_DIR, "..", "runtime")
EVENT_FILE = os.path.join(EVENT_DIR, "face_event.json")

os.makedirs(EVENT_DIR, exist_ok=True)

# ==============================
# LOAD EMBEDDINGS
# ==============================

with open(EMBEDDINGS_PATH, "r") as f:
    patient_db = json.load(f)

print(f"[INFO] Loaded {len(patient_db)} embeddings")

# ==============================
# FACE DETECTOR
# ==============================

mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.7
)

# ==============================
# TEMPORAL STATE
# ==============================

id_history = deque(maxlen=HISTORY_LEN)

frame_count = 0
recognition_state = STATE_ANALYZING

known_start_time = None
unknown_start_time = None

confirmed_patient_id = None
last_emitted_patient_id = None

# ==============================
# HELPERS
# ==============================

def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def decide_identity(history):
    if len(history) < history.maxlen:
        return None

    if history.count("UNKNOWN") / len(history) >= UNKNOWN_RATIO:
        return "UNKNOWN"

    known = [x for x in history if x != "UNKNOWN"]
    return max(set(known), key=known.count) if known else "UNKNOWN"


def emit_patient_id(patient_id):
    event = {
        "patient_id": patient_id,
        "timestamp": time.time()
    }

    with open(EVENT_FILE, "w") as f:
        json.dump(event, f)

    print(f"[FACE_ID_EVENT] Written patient_id={patient_id}")

# ==============================
# CAMERA
# ==============================

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
print("[INFO] Face recognition running. Press Q to quit.")

# ==============================
# MAIN LOOP
# ==============================

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0, 255, 0), 2)

    detections = face_detector.process(rgb)
    face_crop = None

    if detections.detections:
        for det in detections.detections:
            bbox = det.location_data.relative_bounding_box
            x, y = int(bbox.xmin * w), int(bbox.ymin * h)
            bw, bh = int(bbox.width * w), int(bbox.height * h)

            cx, cy = x + bw // 2, y + bh // 2
            if ROI_X1 <= cx <= ROI_X2 and ROI_Y1 <= cy <= ROI_Y2:
                face_crop = frame[y:y+bh, x:x+bw]
                break

    if face_crop is not None:
        frame_count += 1

        if frame_count % FRAME_SKIP == 0:
            emb = DeepFace.represent(
                img_path=face_crop,
                model_name=MODEL_NAME,
                enforce_detection=False
            )[0]["embedding"]

            min_dist = 999
            matched_id = "UNKNOWN"

            for entry in patient_db:
                dist = cosine_distance(emb, entry["embedding"])
                if dist < min_dist:
                    min_dist = dist
                    matched_id = entry["patient_id"]

            id_history.append(matched_id if min_dist < KNOWN_THRESHOLD else "UNKNOWN")

    final_id = decide_identity(id_history)
    now = time.time()

    if recognition_state == STATE_ANALYZING and final_id not in (None, "UNKNOWN"):
        if known_start_time is None:
            known_start_time = now
        elif now - known_start_time >= KNOWN_CONFIRM_TIME:
            recognition_state = STATE_KNOWN
            confirmed_patient_id = final_id

            if confirmed_patient_id != last_emitted_patient_id:
                emit_patient_id(confirmed_patient_id)
                last_emitted_patient_id = confirmed_patient_id

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
