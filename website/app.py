from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

# Path to DB where votes are stored (from the offline laptop)
DB_PATH = os.path.abspath("../PostQunatumHomomorphic_VotingSystem\polling_ui\voters.db")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/verify_vote')
def verify_vote():
    return render_template('verify_vote.html')

@app.route('/live_votes', methods=['GET', 'POST'])
def live_votes():
    """Return current vote counts as JSON for live chart"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bfv_cipher FROM votes")
    encrypted_votes = [row[0] for row in c.fetchall()]
    conn.close()

    # For demonstration, return random counts or decrypt votes if available
    # Here just return placeholder counts
    counts = {
        "Mian Ali Raza": len(encrypted_votes),   # replace with real decryption logic
        "Ayesha Khan": len(encrypted_votes) // 2,
        "Farooq Siddiqui": len(encrypted_votes) // 3,
        "Sadaf Rehman": len(encrypted_votes) // 4,
    }
    return jsonify(counts)

if __name__ == '__main__':
    app.run(debug=True, port=8000)  # runs on port 8000
