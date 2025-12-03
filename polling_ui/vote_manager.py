# vote_manager.py

import sqlite3
from datetime import datetime
DB_PATH = "votes.db"

# ---------------------------
# INITIALIZE DATABASE
# ---------------------------
def init_votes_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnic TEXT UNIQUE,
            candidate TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------
# CHECK IF CNIC ALREADY VOTED
# ---------------------------
def has_voted(cnic):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT candidate FROM votes WHERE cnic=?", (cnic,))
    row = c.fetchone()
    conn.close()
    return row is not None


# ---------------------------
# SAVE A NEW VOTE
# ---------------------------
def save_vote(cnic, candidate):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO votes (cnic, candidate, timestamp) VALUES (?, ?, ?)",
        (cnic, candidate, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
