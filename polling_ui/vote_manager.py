import sqlite3
import os
from datetime import datetime

# ✅ Make DB path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "votes.db")

# ---------------------------
# INITIALIZE DATABASE
# ---------------------------
def init_votes_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Drop old table if exists (optional during development)
    c.execute("DROP TABLE IF EXISTS votes")

    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnic TEXT UNIQUE,
            candidate TEXT,
            bfv_cipher BLOB,
            signature BLOB,
            receipt_hash TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------------------------
# CHECK IF CNIC ALREADY VOTED
# ---------------------------
def has_voted(cnic, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT candidate FROM votes WHERE cnic=?", (cnic,))
    row = c.fetchone()
    conn.close()
    return row is not None


# ---------------------------
# SAVE A NEW VOTE
# ---------------------------
def save_vote(cnic, candidate, bfv_cipher=None, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO votes (cnic, candidate, bfv_cipher, timestamp) VALUES (?, ?, ?, ?)",
        (cnic, candidate, bfv_cipher, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


# ---------------------------
# GET ALL VOTES
# ---------------------------
def get_all_votes(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT candidate, bfv_cipher FROM votes")
    votes = c.fetchall()
    conn.close()
    return votes
