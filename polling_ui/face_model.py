import os
import cv2
import pickle
import numpy as np
from deepface import DeepFace

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACE_DB_FILE = os.path.join(BASE_DIR, "face_db.pkl")

if os.path.exists(FACE_DB_FILE):
    with open(FACE_DB_FILE, "rb") as f:
        face_db = pickle.load(f)
else:
    face_db = {}


def _embedding_from_frame(frame, enforce_detection=False):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    reps = DeepFace.represent(
        img_path=rgb,
        model_name="ArcFace",
        enforce_detection=enforce_detection
    )

    if not reps or "embedding" not in reps[0]:
        return None

    return np.array(reps[0]["embedding"], dtype="float32")


def verify_face(cnic, frame, threshold=0.10):
    if cnic not in face_db:
        print(f"No embedding found for CNIC {cnic}")
        return False

    stored = np.array(face_db[cnic], dtype="float32")

    try:
        emb = _embedding_from_frame(frame, enforce_detection=False)
        if emb is None:
            print("Face verification: no face detected in frame")
            return False

        sim = float(np.dot(emb, stored) / (np.linalg.norm(emb) * np.linalg.norm(stored) + 1e-8))
        print(f"Cosine similarity for {cnic}: {sim:.4f} (threshold={threshold})")

        return sim >= threshold

    except Exception as e:
        print("Face verification error:", e)
        return False


def register_face(cnic, frame):
    emb = _embedding_from_frame(frame, enforce_detection=True)
    if emb is None:
        raise RuntimeError("No face detected during enrollment.")

    face_db[cnic] = emb.tolist()

    with open(FACE_DB_FILE, "wb") as f:
        pickle.dump(face_db, f)

    print(f"Face enrolled for {cnic}")
    print("FACE_DB_FILE path:", FACE_DB_FILE)
    print("Currently enrolled CNICs:", list(face_db.keys()))
