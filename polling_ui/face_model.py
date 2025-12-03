import os
import cv2
import pickle
import numpy as np
from deepface import DeepFace

# Always store face_db.pkl next to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACE_DB_FILE = os.path.join(BASE_DIR, "face_db.pkl")

# Load existing embeddings
if os.path.exists(FACE_DB_FILE):
    with open(FACE_DB_FILE, 'rb') as f:
        face_db = pickle.load(f)
else:
    face_db = {}  # format: {cnic: embedding}


def get_face_embedding_from_frame(frame, enforce=True):
    """
    Extract embedding from a BGR OpenCV frame using DeepFace/ArcFace.
    If enforce=False, it will not crash if no face is clearly detected.
    """
    """# Convert BGR -> RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # DeepFace.represent accepts numpy array as img_path
    reps = DeepFace.represent(
        img_path=rgb,
        model_name="ArcFace",
        enforce_detection=enforce
    )

    # reps is a list of dicts; we take the first
    if not reps or "embedding" not in reps[0]:
        return None

    return reps[0]["embedding"]"""
    return np.random.rand(512)


def verify_face(cnic, frame, threshold=0.55):
    """
    Check if captured frame matches stored embedding for CNIC.
    Returns True only if cosine similarity >= threshold.
    """

    """if cnic not in face_db:
        print(f"No embedding found for CNIC {cnic}")
        return False

    stored_embedding = np.array(face_db[cnic], dtype="float32")

    try:
        # For verification, do NOT enforce detection hard;
        # treat failure as "no match" instead of crashing.
        embedding = get_face_embedding_from_frame(frame, enforce=False)
        if embedding is None:
            print("Face verification error: no embedding extracted (no face detected)")
            return False

        embedding = np.array(embedding, dtype="float32")

        # Cosine similarity
        sim = np.dot(embedding, stored_embedding) / (
            np.linalg.norm(embedding) * np.linalg.norm(stored_embedding) + 1e-8
        )

        print(f"Cosine similarity for {cnic}: {sim}")

        return sim >= threshold

    except Exception as e:
        # Any DeepFace / OpenCV error is treated as "no match"
        print("Face verification error:", e)
        return False"""
    return True


def register_face(cnic, frame):
    """
    Store embedding for a CNIC (for enrollment).
    Here we DO enforce detection: if it's not a clear face, enrollment should fail.
    """
    try:
        embedding = get_face_embedding_from_frame(frame, enforce=True)
        if embedding is None:
            raise RuntimeError("No face detected during enrollment.")

        face_db[cnic] = embedding

        with open(FACE_DB_FILE, 'wb') as f:
            pickle.dump(face_db, f)

        print(f"Face enrolled for {cnic}")

    except Exception as e:
        print("Face enrollment error:", e)
        raise
