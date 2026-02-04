import json
import cv2
import os
import mediapipe as mp
from deepface import DeepFace
import numpy as np


# ==============================
# 1. CONFIGURATION
# ==============================

PATIENT_DB_PATH = r"D:\robot_system\face_dataset"
MODEL_NAME = "ArcFace"
DISTANCE_THRESHOLD = 0.6

# ROI (adjust if needed)
ROI_X1, ROI_Y1 = 150, 200
ROI_X2, ROI_Y2 = 500, 450

# Temporal stability
STABILITY_THRESHOLD = 7
stable_counter = 0
face_is_stable = False

# ==============================
# 2. LOAD PATIENT DATABASE
# ==============================

def load_patient_embeddings():
    database = []

    for patient_id in os.listdir(PATIENT_DB_PATH):
        patient_folder = os.path.join(PATIENT_DB_PATH, patient_id)

        if not os.path.isdir(patient_folder):
            continue

        for img in os.listdir(patient_folder):
            img_path = os.path.join(patient_folder, img)

            embedding = DeepFace.represent(
                img_path=img_path,
                model_name=MODEL_NAME,
                enforce_detection=False
            )[0]["embedding"]

            database.append({
                "patient_id": patient_id,
                "embedding": embedding
            })

    return database


print("Loading patient database...")
#patient_db = load_patient_embeddings()
with open("vision/embeddings.json") as f:
    patient_db = json.load(f)

print(f"Loaded {len(patient_db)} embeddings")

# ==============================
# 3. MEDIAPIPE FACE DETECTION
# ==============================

mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.8
)

# ==============================
# 4. OPEN CAMERA
# ==============================

cap = cv2.VideoCapture(0)

print("Press Q to quit")

# ==============================
# 5. MAIN LOOP
# ==============================

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_detection.process(rgb)

    # Draw ROI
    cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0,255,0), 2)
    cv2.putText(frame, "BED ROI", (ROI_X1, ROI_Y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    face_detected_in_roi = False
    cropped_face = None

    if results.detections:
        for det in results.detections:
            bbox = det.location_data.relative_bounding_box

            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)

            cx = x + bw // 2
            cy = y + bh // 2

            if ROI_X1 <= cx <= ROI_X2 and ROI_Y1 <= cy <= ROI_Y2:
                face_detected_in_roi = True

                cropped_face = frame[y:y+bh, x:x+bw]
                cv2.rectangle(frame, (x,y), (x+bw, y+bh), (255,0,0), 2)

    # ==============================
    # TEMPORAL STABILITY
    # ==============================

    if face_detected_in_roi:
        stable_counter += 1
    else:
        stable_counter = 0
        face_is_stable = False

    if stable_counter >= STABILITY_THRESHOLD:
        face_is_stable = True

    # ==============================
    # FACE RECOGNITION
    # ==============================

    if face_is_stable and cropped_face is not None:
        try:
            result = DeepFace.represent(
                img_path=cropped_face,
                model_name=MODEL_NAME,
                enforce_detection=False
            )

            emb = result[0]["embedding"]

            min_dist = 999
            matched_patient = "UNKNOWN"

            for entry in patient_db:
                dist = np.dot(emb, entry["embedding"]) / (
                np.linalg.norm(emb) * np.linalg.norm(entry["embedding"])
                ) 
                dist = 1 - dist  # convert similarity → distance
                if dist < min_dist:
                    min_dist = dist
                    matched_patient = entry["patient_id"]

            if min_dist < DISTANCE_THRESHOLD:
                label = f"PATIENT: {matched_patient}"
                color = (0,255,0)
            else:
                label = "UNKNOWN PERSON"
                color = (0,0,255)

            cv2.putText(frame, label, (30,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        except Exception as e:
            print("Recognition error:", e)

    else:
        cv2.putText(frame, "Waiting for stable face...",
                    (30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    cv2.imshow("Live Patient Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==============================
# CLEANUP
# ==============================

cap.release()
cv2.destroyAllWindows()
