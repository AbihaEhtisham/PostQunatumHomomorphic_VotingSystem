from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

# Correct DB path
DB_PATH = os.path.abspath(r"../PostQunatumHomomorphic_VotingSystem/polling_ui/votes.db")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/verify_vote')
def verify_vote():
    return render_template('verify_vote.html')

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
