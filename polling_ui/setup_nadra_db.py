# setup_nadra_db.py
import sqlite3

conn = sqlite3.connect("nadra.db")
c = conn.cursor()

# 1️⃣ Create voters table only if it does NOT already exist
c.execute("""
CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cnic TEXT NOT NULL UNIQUE,
    face_template TEXT
)
""")

# 2️⃣ Insert sample voters safely (no duplicates allowed)
sample_data = [
    ("Abiha Ehtisham", "35202-1234567-1", "placeholder"),
    ("Azka Saqib", "35201-9876543-0", "placeholder"),
    ("Eman Fatima", "61101-4567890-2", "placeholder")
]

for name, cnic, face in sample_data:
    # INSERT OR IGNORE prevents duplicate CNIC errors
    c.execute("""
        INSERT OR IGNORE INTO voters (name, cnic, face_template)
        VALUES (?, ?, ?)
    """, (name, cnic, face))

conn.commit()
conn.close()

print("NADRA database is ready. Voters table ensured and sample voters inserted.")
