import cv2
import json
import time
import numpy as np
import mediapipe as mp
from collections import deque

# ==============================
# CONFIGURATION
# ==============================

EMBEDDINGS_PATH = r"D:\robot_system\vision\embeddings.json"

MODEL_NAME = "ArcFace"

KNOWN_THRESHOLD = 0.70
UNKNOWN_THRESHOLD = 0.60

STATE_ANALYZING = 0
STATE_KNOWN = 1
STATE_UNKNOWN = 2

recognition_state = STATE_ANALYZING


HISTORY_LEN = 6
UNKNOWN_RATIO = 0.66
UNKNOWN_TIME_REQUIRED = 1.5  # seconds

FRAME_SKIP = 8  # run recognition every N frames

# ROI (bed region)
ROI_X1, ROI_Y1 = 150, 200
ROI_X2, ROI_Y2 = 500, 450

# ==============================
# LOAD PRECOMPUTED EMBEDDINGS
# ==============================

with open(EMBEDDINGS_PATH, "r") as f:
    patient_db = json.load(f)

print(f"Loaded {len(patient_db)} embeddings")

# ==============================
# MEDIAPIPE FACE DETECTOR
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
unknown_start_time = None
frame_count = 0
last_final_id = None

# ==============================
# HELPER FUNCTIONS
# ==============================

def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def decide_identity(history):
    if len(history) < history.maxlen:
        return None

    unknown_count = history.count("UNKNOWN")
    if unknown_count / len(history) >= UNKNOWN_RATIO:
        return "UNKNOWN"

    known = [x for x in history if x != "UNKNOWN"]
    if not known:
        return "UNKNOWN"

    return max(set(known), key=known.count)


# ==============================
# CAMERA
# ==============================

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
print("Press Q to quit")

# ==============================
# MAIN LOOP
# ==============================

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Draw ROI
    cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0, 255, 0), 2)
    cv2.putText(frame, "BED ROI", (ROI_X1, ROI_Y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    detections = face_detector.process(rgb)

    face_crop = None

    if detections.detections:
        for det in detections.detections:
            bbox = det.location_data.relative_bounding_box

            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)

            cx, cy = x + bw // 2, y + bh // 2

            if ROI_X1 <= cx <= ROI_X2 and ROI_Y1 <= cy <= ROI_Y2:
                face_crop = frame[y:y + bh, x:x + bw]
                cv2.rectangle(frame, (x, y), (x + bw, y + bh), (255, 0, 0), 2)
                break

    # ==============================
    # FACE RECOGNITION (SKIPPED FRAMES)
    # ==============================

    if face_crop is not None:
        frame_count += 1

        if frame_count % FRAME_SKIP == 0:
            try:
                from deepface import DeepFace

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

                if min_dist < KNOWN_THRESHOLD:
                    id_history.append(matched_id)

                elif min_dist > UNKNOWN_THRESHOLD:
                    id_history.append("UNKNOWN")

                else:
                    # Ambiguous → soft unknown
                    id_history.append("UNKNOWN")


            except Exception as e:
                print("Recognition error:", e)

    # ==============================
    # FINAL DECISION
    # ==============================

    final_id = decide_identity(id_history)
    current_time = time.time()

    if recognition_state == STATE_ANALYZING:

        if final_id == "UNKNOWN":
            if unknown_start_time is None:
                unknown_start_time = current_time

            if current_time - unknown_start_time >= UNKNOWN_TIME_REQUIRED:
                recognition_state = STATE_UNKNOWN
                display_text = "UNKNOWN PERSON"
            else:
                display_text = "UNKNOWN (CONFIRMING...)"
        elif final_id is None:
            display_text = "Analyzing..."

        else:
            recognition_state = STATE_KNOWN
            display_text = f"PATIENT: {final_id}"

    elif recognition_state == STATE_UNKNOWN:
        display_text = "UNKNOWN PERSON"
    elif recognition_state == STATE_KNOWN:
        display_text = f"PATIENT: {final_id}"



    # ==============================
    # DISPLAY
    # ==============================

    cv2.putText(frame, display_text, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 255, 0) if "PATIENT" in display_text else (0, 0, 255), 2)

    cv2.imshow("Stable Patient Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==============================
# CLEANUP
# ==============================

cap.release()
cv2.destroyAllWindows()
