import os
import json
from deepface import DeepFace

FACE_DATASET = r"D:\robot_system\face_dataset"
EMBEDDINGS_FILE = r"D:\robot_system\vision\embeddings.json"
MODEL_NAME = "ArcFace"

db = []

for pid in os.listdir(FACE_DATASET):
    folder = os.path.join(FACE_DATASET, pid)
    if not os.path.isdir(folder):
        continue

    for img in os.listdir(folder):
        img_path = os.path.join(folder, img)

        emb = DeepFace.represent(
            img_path=img_path,
            model_name=MODEL_NAME,
            enforce_detection=False
        )[0]["embedding"]

        db.append({
            "patient_id": pid,
            "embedding": emb
        })

with open(EMBEDDINGS_FILE, "w") as f:
    json.dump(db, f)

print("✅ Embeddings built")
