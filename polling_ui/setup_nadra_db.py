# setup_nadra_db.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NADRA_DB_PATH = os.path.join(BASE_DIR, "nadra.db")

conn = sqlite3.connect(NADRA_DB_PATH)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cnic TEXT NOT NULL UNIQUE,
    face_template TEXT
)
""")

sample_data = [
    ("Abiha Ehtisham", "35202-1234567-1", "placeholder"),
    ("Azka Saqib", "35201-9876543-0", "placeholder"),
    ("Eman Fatima", "61101-4567890-2", "placeholder")
]

for name, cnic, face in sample_data:
    c.execute("""
        INSERT OR IGNORE INTO voters (name, cnic, face_template)
        VALUES (?, ?, ?)
    """, (name, cnic, face))

conn.commit()
conn.close()

print("NADRA database is ready at:", NADRA_DB_PATH)
