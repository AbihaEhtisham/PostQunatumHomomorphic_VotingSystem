import sqlite3
import os
DBV_PATH = r"D:\PostQunatumHomomorphic_VotingSystem\polling_ui\votes.db"
conn = sqlite3.connect(DBV_PATH)
c = conn.cursor()
c.execute("SELECT id, cnic, candidate, bfv_cipher, timestamp FROM votes")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()
