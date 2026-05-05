import os
import json
from deepface import DeepFace
from PIL import Image # for file validation

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

"""
doubt: Don't have a folder name robot_system locally on my computer, it is not present in the repo I was given, I only have robot_system.py as a file

The hardcoded Windows paths in build_embeddings.py are environment-specific and not portable. On my Mac, I need to replace them with dynamic paths using os.path so the script correctly locates the dataset and embeddings file relative to the project directory.

Chatgpt fixes:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # vision/
ROOT_DIR = os.path.dirname(BASE_DIR)                    # project root
FACE_DATASET = os.path.join(ROOT_DIR, "face_dataset")
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "embeddings.json")
"""

FACE_DATASET = r"D:\robot_system\face_dataset"
EMBEDDINGS_FILE = r"D:\robot_system\vision\embeddings.json"
MODEL_NAME = "ArcFace"

db = [] # database initialisation

# loop over each patient's id and then appending them into the dataset
for pid in os.listdir(FACE_DATASET):
    
    folder = os.path.join(FACE_DATASET, pid) # pid = "alice" → folder = "face_dataset/alice"
    if not os.path.isdir(folder): # checks if the path is actually a folder, here alice is a folder, not a file. If it is a file, we will skip and continue the loop for the next person
        continue

    for img in os.listdir(folder):
        img_path = os.path.join(folder, img) # img_path = "face_dataset/alice/img1.jpg"

        # file validation fix: before sending a file to deepface, we ensure it is actually a file, has image type and it is readable/valid
        # 1. Must be a file
        if not os.path.isfile(img_path):
            continue
        # 2. Must be an image
        if not img.lower().endswith(VALID_EXTENSIONS):
            continue
        # 3. Must be readable
        try:
            Image.open(img_path).verify() # from PIL import image
        except:
            continue

        emb = DeepFace.represent(
            img_path=img_path,
            model_name=MODEL_NAME,
            enforce_detection=False # generates fake embeddings despite no face detected → pollutes data
        )[0]["embedding"]
        # Deepface:
        # 1. Load image
        # 2. Detect face
        # 3. Align face
        # 4. Pass through ArcFace model
        # 5. Output embedding vector

        db.append({
            "patient_id": pid,
            "embedding": emb
        })

with open(EMBEDDINGS_FILE, "w") as f: # Dataset → rebuild embeddings → overwrite file
    json.dump(db, f)

print("✅ Embeddings built")