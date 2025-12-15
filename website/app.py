from flask import Flask, render_template, jsonify, request
import sqlite3
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "polling_ui"))  # add polling_ui folder

from bfv import load_or_create_bfv_context

bfv_ctx = load_or_create_bfv_context()


app = Flask(__name__)

# Path to votes.db in polling_ui folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "polling_ui", "voters.db")

import json
from datetime import datetime

CONFIG_FILE = "config.json"  # path relative to app.py

@app.route('/')
def index():
    # Read config
    with open(CONFIG_FILE, 'r') as f:
        cfg = json.load(f)

    start_time = datetime.fromisoformat(cfg['start_time'])
    end_time = datetime.fromisoformat(cfg['end_time'])

    start_hour = start_time.hour
    start_minute = start_time.minute
    end_hour = end_time.hour
    end_minute = end_time.minute

    return render_template(
        "index.html",
        start_hour=start_hour,
        start_minute=start_minute,
        end_hour=end_hour,
        end_minute=end_minute
    )


@app.route('/verify_vote', methods=['GET', 'POST'])
def verify_vote():
    result = None
    all_receipts = []

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch all receipt hashes for display
    c.execute("SELECT receipt_hash FROM votes")
    all_receipts = [row[0] for row in c.fetchall()]

    if request.method == 'POST':
        receipt_hash = request.form.get('receipt_hash', '').strip()
        c.execute("SELECT 1 FROM votes WHERE receipt_hash = ?", (receipt_hash,))
        row = c.fetchone()
        result = bool(row)  # True if found, False if not

    conn.close()
    return render_template('verify_vote.html', result=result, all_receipts=all_receipts)


@app.route('/api/live_votes')
def api_live_votes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM votes")
    total_votes = c.fetchone()[0]
    conn.close()

    return jsonify({"total_votes_cast": total_votes})

NUM_CANDIDATES = 4  # total candidates
candidate_names = ["Mian Ali Raza", "Ayesha Khan", "Farooq Siddiqui", "Sadaf Rehman"]

@app.route('/api/final_results')
def api_final_results():
    import tenseal as ts
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bfv_cipher FROM votes")
    votes = c.fetchall()
    conn.close()

    if not votes:
        return jsonify([0, 0, 0, 0])

    enc_sum = ts.bfv_vector_from(bfv_ctx, votes[0][0])

    for v in votes[1:]:
        enc_sum += ts.bfv_vector_from(bfv_ctx, v[0])

    # ✅ NOW THIS WORKS
    final_totals = enc_sum.decrypt()

    return jsonify(final_totals)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
