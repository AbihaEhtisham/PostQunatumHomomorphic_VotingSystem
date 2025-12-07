# enroll_face.py (put this in the same folder as face_model.py)
import cv2
from face_model import register_face

# CNIC must match what's in nadra.db
CNIC = "35202-1234567-1"   
IMAGE_PATH = "Azka.jpg"   

frame = cv2.imread(IMAGE_PATH)
if frame is None:
    raise RuntimeError(f"Could not load image from {IMAGE_PATH}")

register_face(CNIC, frame)
print("Face enrolled for", CNIC)
