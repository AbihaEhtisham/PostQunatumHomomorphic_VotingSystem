from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Path to votes.db in polling_ui folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "polling_ui", "voters.db")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/verify_vote', methods=['GET', 'POST'])
def verify_vote():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT receipt_hash FROM votes")
    all_receipts = [row[0] for row in c.fetchall()]
    result = None

    if request.method == 'POST':
        search_hash = request.form.get('receipt_hash', '').strip()
        result = search_hash in all_receipts

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


if __name__ == '__main__':
    app.run(debug=True, port=8000)
