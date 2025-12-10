import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from utils import BASE_DIR, verify_agent_key, is_voting_open
import sqlite3
import cv2
import numpy as np
from face_model import verify_face
from vote_manager import init_votes_db
from bfv import encrypt_vote, load_or_create_bfv_context, decrypt_vote
from dilithium import sign_bytes, receipt_hash, generate_keys
from threshold import combine_shares
import builtins
builtins.long = int

import os
import tenseal as ts
print(os.path.exists(os.path.join(BASE_DIR, 'templates', 'receipt.html')))

app = Flask(__name__)
app.secret_key = 'your-secret-key'
# initialize or load BFV context used for encryption/decryption
bfv_ctx = load_or_create_bfv_context()


DB_PATH = os.path.join(BASE_DIR, 'voters.db')
init_votes_db()

# ---- DB helpers ----

def has_voted(cnic):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM votes WHERE voter_cnic=? LIMIT 1", (cnic,))
    result = c.fetchone()
    conn.close()
    return result is not None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cnic TEXT UNIQUE,
        dilithium_pubkey BLOB,
        dilithium_privkey BLOB
      )
    ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bfv_cipher BLOB,
        voter_cnic TEXT,
        signature BLOB,
        receipt_hash TEXT,
        timestamp INTEGER DEFAULT (strftime('%s','now'))
      )
    ''')
    conn.commit()
    conn.close()

init_db()
# ---------------------------
# AGENT LOGIN
# ---------------------------
@app.route('/agent_login', methods=['GET','POST'])
def agent_login():
    if request.method == 'POST':
        station_id = request.form.get('station_id')
        agent_key = request.form.get('agent_key')

        if verify_agent_key(station_id, agent_key):
            session['station_id'] = station_id
            return redirect(url_for('voter_validation'))
        else:
            flash('Invalid key or station ID!')
            return redirect(url_for('agent_login'))

    return render_template('agent_login.html')


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

from threshold import combine_shares

# Store partial decryptions (in memory or DB)
# partial_decryptions = {}  # {vote_id: [share1, share2]}

# --------------------------------------------
# AGENT PAGE – partial decryption
# --------------------------------------------
@app.route("/agent/<agent_id>")
def agent(agent_id):
    return render_template("agent.html", agent=agent_id)

# ---------------------------
# LIVE VOTES PAGE
# ---------------------------
@app.route('/live_votes')
def live_votes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bfv_cipher FROM votes")
    encrypted_votes = [row[0] for row in c.fetchall()]
    conn.close()

    # Decrypt votes using BFV context
    decrypted_sums = [0] * 4  # Assuming 4 candidates
    for enc_bytes in encrypted_votes:
        try:
            vote_vec = decrypt_vote(bfv_ctx, enc_bytes)  # decrypt_vote returns list
            for i in range(len(vote_vec)):
                decrypted_sums[i] += vote_vec[i]
        except Exception as e:
            print("Decryption error:", e)

    candidate_names = ["Mian Ali Raza", "Ayesha Khan", "Farooq Siddiqui", "Sadaf Rehman"]
    votes_display = list(zip(candidate_names, decrypted_sums))

    return render_template("live_votes.html", votes=votes_display)

"""@app.route('/results', methods=['GET', 'POST'])
def results():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bfv_cipher FROM votes")
    encrypted_votes = [row[0] for row in c.fetchall()]
    conn.close()

    if not encrypted_votes:
        return "No votes yet"

    if request.method == 'POST':
        # Receive partial decryptions from agents
        partials = request.form.getlist("partial")
        final_sum = combine_shares(partials)
        return render_template("results.html", tally=final_sum)

    return render_template("results.html", tally=None, encrypted_votes=encrypted_votes)"""


# ---------------------------
# VOTER NAME + CNIC VALIDATION
# ---------------------------
@app.route('/voter_validation', methods=['GET', 'POST'])
def voter_validation():
    error = None

    if request.method == 'GET':
        if request.args.get('face_failed') == '1':
            error = "Voter not recognized. Cannot proceed to voting."
        return render_template("voter_verify.html", error=error)

    name = (request.form.get('name') or '').strip()
    cnic = (request.form.get('cnic') or '').strip()

    if not name or not cnic:
        return render_template("voter_verify.html", error="Name and CNIC are required.")

    conn = sqlite3.connect('nadra.db')
    c = conn.cursor()
    c.execute("SELECT * FROM voters WHERE name=? AND cnic=?", (name, cnic))
    voter = c.fetchone()
    conn.close()

    if voter:
        session['voter_name'] = name
        session['voter_cnic'] = cnic
        session['face_verified'] = False
        return redirect(url_for('verify_face_page'))
    else:
        return render_template("voter_verify.html", error="Voter not found in NADRA database.")

# ---------------------------
# FACE VERIFICATION PAGE
# ---------------------------
@app.route('/verify_face')
def verify_face_page():
    if 'voter_cnic' not in session:
        flash("Please verify voter information first.")
        return redirect(url_for('voter_validation'))
    return render_template('verify_face.html')

# ---------------------------
# FACE STREAM PROCESSING (WEBCAM)
# ---------------------------
@app.route('/verify_face_stream', methods=['POST'])
def verify_face_stream():
    cnic = session.get('voter_cnic')
    if not cnic:
        # Bad client state; send 400
        return jsonify({"status": "error", "message": "No voter in session."}), 400

    data = request.get_json(silent=True) or {}
    image_data = data.get("image")

    if not image_data:
        # No frame sent, but don't crash
        return jsonify({"status": "error", "message": "Empty frame"}), 200

    try:
        # Handle data URL "data:image/jpeg;base64,..."
        if "," in image_data:
            _, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        import base64
        img_bytes = base64.b64decode(encoded or "")
        if not img_bytes:
            # Empty buffer -> just tell frontend to retry
            print("Face error: empty image buffer")
            return jsonify({"status": "error", "message": "Empty image buffer"}), 200

        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            print("Face error: could not decode frame")
            return jsonify({"status": "error", "message": "Image decode failed"}), 200

        ok = verify_face(cnic, frame)

        if ok:
            session['face_verified'] = True
            conn = sqlite3.connect(DB_PATH)
            
            c = conn.cursor()

            # If voter not already in voters.db → insert and generate keys
            c.execute("SELECT id FROM voters WHERE cnic=?", (session['voter_cnic'],))
            exists = c.fetchone()

            if not exists:          # generate keys
                pub, priv = generate_keys()

                c.execute("""
                INSERT INTO voters (name, cnic, dilithium_pubkey, dilithium_privkey)
                VALUES (?, ?, ?, ?)
                """, (session['voter_name'], session['voter_cnic'], pub, priv))

                conn.commit()
            conn.close()
            return jsonify({"status": "verified", "redirect": url_for("vote_page")})
        
        else:
            # Not verified (either low similarity or no face detected)
            return jsonify({"status": "unverified"}), 200

    except Exception as e:
        # Catch *all* DeepFace / OpenCV weirdness, never crash
        print("Face error:", e)
        return jsonify({"status": "error", "message": "Internal error during face verification."}), 200

# ---------------------------
# VOTING PAGE
# ---------------------------
@app.route('/vote')
def vote_page():
    if not session.get('face_verified'):
        flash("Face verification required.")
        return redirect(url_for('voter_validation'))

    cnic = session.get('voter_cnic')

    #  Prevent already-voted voters
    if has_voted(cnic):
        return render_template("already_voted.html", cnic=cnic)

    if not is_voting_open():
        return render_template('voting_closed.html')

    return render_template('vote.html')


# ---------------------------
# SUBMIT VOTE
# ---------------------------
@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if not session.get('face_verified'):
        return "Error: Face not verified.", 403
    
    cnic = session.get("voter_cnic")

    # ⭐ Block double voting
    if has_voted(cnic):
        return "Error: This voter has already cast a vote.", 403

    candidate = request.form.get("candidate")
    if candidate is None:
        return "No candidate selected", 400

    cnic = session.get("voter_cnic")

    candidate_names = ["Mian Ali Raza", "Ayesha Khan", "Farooq Siddiqui", "Sadaf Rehman"]
    try:
        candidate_index = int(candidate)
        vote_vec = [0] * len(candidate_names)
        vote_vec[candidate_index] = 1
    except ValueError:
        return "Invalid candidate", 400

    # ---- ENCRYPTION & SIGNATURE ----
    enc_bytes = encrypt_vote(bfv_ctx, vote_vec)

    # Load voter's Dilithium keys from DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT dilithium_privkey, dilithium_pubkey FROM voters WHERE cnic=?", (cnic,))
    row = c.fetchone()
    if not row:
        conn.close()
        return "Voter not found", 404
    privkey, pubkey = row

    sig = sign_bytes(privkey, enc_bytes)
    receipt = receipt_hash(enc_bytes, sig)
    print(os.path.exists(os.path.join(BASE_DIR, 'static', 'style.css')))
    print("Receipt:", receipt)

    # ---- STORE VOTE ----
    c.execute('''INSERT INTO votes (voter_cnic, bfv_cipher, signature, receipt_hash)
                 VALUES (?, ?, ?, ?)''',
              (cnic, sqlite3.Binary(enc_bytes), sqlite3.Binary(sig), receipt))
    conn.commit()
    conn.close()

    return render_template("receipt.html", receipt_hash=receipt)


@app.route('/')
def index():
    return redirect(url_for('agent_login'))

# ---------------------------
# THRESHOLD UI ROUTES
# ---------------------------

# Store shares temporarily (RAM only)
"""threshold_shares = {"agent1": None, "agent2": None}

@app.route('/threshold', methods=['GET'])
def threshold_home():
    return render_template(
        'threshold.html',
        a1=threshold_shares["agent1"] is not None,
        a2=threshold_shares["agent2"] is not None
    )

@app.route('/submit_agent_share', methods=['POST'])
def submit_agent_share():
    agent = request.form.get('agent')  # agent1 or agent2
    share = request.form.get('share')

    if agent not in ["agent1", "agent2"]:
        return "Invalid agent!", 400

    threshold_shares[agent] = share  # store in memory

    flash(f"Share received from {agent}.")
    return redirect(url_for('threshold_home'))

@app.route('/decrypt_tally', methods=['POST'])
def decrypt_tally():
    # Check that both shares exist
    if not threshold_shares["agent1"] or not threshold_shares["agent2"]:
        flash("Both agent shares are required!")
        return redirect(url_for('threshold_home'))

    # Reconstruct secret key
    combined_hex = combine_shares([threshold_shares["agent1"], threshold_shares["agent2"]])
    recovered_bytes = bytes.fromhex(combined_hex)
    recovered_ctx = ts.context_from(recovered_bytes)

    # Decrypt all votes
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bfv_cipher FROM votes")
    votes = c.fetchall()

    tally = [0, 0, 0, 0]  # four candidates
    for (enc,) in votes:
        vec = decrypt_vote(recovered_ctx, enc)
        for i in range(len(vec)):
            tally[i] += vec[i]

    conn.close()

    # Clear shares after decrypt
    threshold_shares["agent1"] = None
    threshold_shares["agent2"] = None

    return render_template("tally.html", tally=tally)"""


@app.after_request
def add_security_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



if __name__ == '__main__':
    app.run(debug=True, port=5000)
