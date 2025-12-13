import sqlite3
import os
from dilithium import generate_keys

DB_PATH = os.path.join("voters.db")

voters = [
    ("Abiha Ehtisham", "35202-1234567-1"),
    ("Azka Saqib", "35202-7848640-8"),
    ("Eman Fatima", "61101-4567890-2")
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("""
CREATE TABLE voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cnic TEXT NOT NULL UNIQUE,
    dilithium_privkey BLOB NOT NULL,
    dilithium_pubkey BLOB NOT NULL
)
""")

for name, cnic in voters:
    sk, pk = generate_keys()   # CORRECT ORDER
    c.execute("""
        INSERT INTO voters (name, cnic, dilithium_privkey, dilithium_pubkey)
        VALUES (?, ?, ?, ?)
    """, (name, cnic, sqlite3.Binary(sk), sqlite3.Binary(pk)))

conn.commit()
conn.close()

print("voters.db regenerated correctly")
