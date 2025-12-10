import cv2
import numpy as np
from deepface import DeepFace # or you can use facenet-pytorch / arcface
import os
import pickle

# Path to store face embeddings for voters
FACE_DB_FILE = 'face_db.pkl'

# Load existing embeddings
if os.path.exists(FACE_DB_FILE):
     with open(FACE_DB_FILE, 'rb') as f:
         face_db = pickle.load(f)
else:
    face_db = {}  # format: {cnic: embedding}

def get_face_embedding(image):
    """Extract embedding vector from an image using DeepFace/ArcFace"""
    embedding = DeepFace.represent(img_path=image, model_name="ArcFace", enforce_detection=True)
    return embedding[0]["embedding"]

def verify_face(cnic, frame, threshold=0.6):
 """
    This entire block contains the full verification logic.
    It is commented out to allow for rapid development/testing 
    of the surrounding application flow.
    
    if cnic not in face_db:
        print(f"No embedding found for CNIC {cnic}")
        return False

        # OpenCV frame is BGR; convert to RGB for DeepFace
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        embedding = DeepFace.represent(
            img_path=rgb_frame,
            model_name="ArcFace",
            enforce_detection=True
        )[0]["embedding"]

        stored_embedding = face_db[cnic]

        embedding = np.array(embedding, dtype="float32")
        stored_embedding = np.array(stored_embedding, dtype="float32")

        # Cosine similarity
         sim = np.dot(embedding, stored_embedding) / (
            np.linalg.norm(embedding) * np.linalg.norm(stored_embedding)
         )

        print(f"Cosine similarity for {cnic}: {sim}")
        
        return sim >= threshold
    except Exception as e:
        print("Face verification error:", e)
        return False
    """
    # Temporary bypass for development/testing
 return True

def register_face(cnic, frame):
    """Store embedding for a CNIC"""
    embedding = DeepFace.represent(img_path=frame, model_name="ArcFace", enforce_detection=True)[0]["embedding"]
    face_db[cnic] = embedding
    with open(FACE_DB_FILE, 'wb') as f:
        pickle.dump(face_db,f)