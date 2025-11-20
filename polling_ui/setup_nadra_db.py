import sqlite3

conn = sqlite3.connect("nadra.db")
c = conn.cursor()

# Drop old table if it exists (OPTIONAL)
c.execute("DROP TABLE IF EXISTS voters")

# Create new table
c.execute("""
CREATE TABLE voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cnic TEXT NOT NULL UNIQUE,
    face_template TEXT
)
""")

# Insert sample NADRA-approved voters
sample_data = [
    ("Abiha Ehtisham", "35202-1234567-1", "placeholder"),
    ("Azka Saqib", "35201-9876543-0", "placeholder"),
    ("Eman Fatima", "61101-4567890-2", "placeholder")
]

c.executemany("INSERT INTO voters (name, cnic, face_template) VALUES (?, ?, ?)", sample_data)

conn.commit()
conn.close()

print("NADRA database created with sample voters.")
