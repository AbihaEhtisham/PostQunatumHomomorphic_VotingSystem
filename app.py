# app.py
import os
import sqlite3
import base64
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from crypto import *
from crypto import load_or_create_bfv_context

bfv_ctx = load_or_create_bfv_context()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'voters.db')

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(16)


# ---- DB helpers ----
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cnic TEXT UNIQUE,
        email TEXT,
        password_hash TEXT,
        dilithium_pubkey BLOB
      )
    ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bfv_cipher BLOB,
        voter_cnic TEXT,
        signature BLOB,
        timestamp INTEGER DEFAULT (strftime('%s','now'))
      )
    ''')
    conn.commit()
    conn.close()

def update_votes_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE votes ADD COLUMN receipt_hash TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.commit()
    conn.close()

update_votes_table()

# ---- Routes ----

@app.route('/', endpoint='index')
def index():
    return render_template("index.html")

# ---- Routes: pages ----
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/vote', methods=['GET'])
def vote_page():
    if 'cnic' not in session:
        return redirect(url_for('login_page'))
    return render_template('vote.html')

@app.route('/results')
def results():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT bfv_cipher FROM votes')
    rows = c.fetchall()
    conn.close()
    if not rows:
        return "No votes yet"
    total = None                                 # Homomorphic sum
    for (enc_bytes,) in rows:
        vote_vec = ts.bfv_vector_from(bfv_ctx, enc_bytes)
        if total is None:
            total = vote_vec
        else:
            total += vote_vec
    tally = total.decrypt()[0]
    return render_template("results.html", tally=tally)

@app.route('/live_votes')
def live_votes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT bfv_cipher FROM votes')
    rows = c.fetchall()
    conn.close()

    if not rows:
        return "No votes yet"

    total = None
    for row in rows:
        cipher_blob = row[0]
        vote_vec = ts.bfv_vector_from(bfv_ctx, cipher_blob)
        total = vote_vec if total is None else total + vote_vec

    tally_vector = total.decrypt()

    candidate_names = ["Alice", "Bob", "Charlie"]
    results = {candidate_names[i]: tally_vector[i] for i in range(len(candidate_names))}

    return render_template("live_votes.html", results=results)

# ---- Login API ----
@app.route('/login', methods=['POST'])
def login_api():
    data = request.get_json()
    cnic = data.get('cnic','').strip()
    password = data.get('password','')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password_hash FROM voters WHERE cnic=?', (cnic,))
    row = c.fetchone()
    conn.close()
    if not row or row[0] is None:
        return jsonify({'message':'CNIC not registered'}), 400
    pw_hash = row[0]
    if not check_password_hash(pw_hash, password):
        return jsonify({'message':'Incorrect password'}), 401

    session['cnic'] = cnic
    return jsonify({'success': True, 'message': 'Login successful'})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return ('', 204)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if 'cnic' not in session:
        return "Not authenticated", 403

    candidate = request.form.get('candidate')
    if candidate is None:
        return "No candidate selected", 400

    try:
        candidate_index = int(candidate)
    except ValueError:
        return "Invalid candidate", 400
     
    candidate_names = ["Alice", "Bob", "Charlie"]  # same order as vote.html
    candidate_index = int(candidate)

    # dynamic 1-hot vector
    vote_vec = [0] * len(candidate_names)
    vote_vec[candidate_index] = 1

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM votes WHERE voter_cnic=?', (session['cnic'],))
        if c.fetchone():
            return "You have already voted!", 403

    # Encrypt one-hot vector
    enc_bytes = encrypt_vote(bfv_ctx, vote_vec)

    # Load keys
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT dilithium_privkey, dilithium_pubkey FROM voters WHERE cnic=?', (session['cnic'],))
        row = c.fetchone()

    if not row:
        return "Voter not found", 404

    privkey, pubkey = row

    sig = sign_bytes(privkey, enc_bytes)
    receipt = receipt_hash(enc_bytes, sig)

    # Store as BLOBs
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO votes (voter_cnic, bfv_cipher, signature, receipt_hash)
            VALUES (?, ?, ?, ?)
        ''', (
            session['cnic'],
            sqlite3.Binary(enc_bytes),
            sqlite3.Binary(sig),
            receipt
        ))
        conn.commit()

    return render_template("receipt.html", receipt_hash=receipt)

@app.route('/verify', methods=['GET','POST'])
def verify_vote():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT receipt_hash FROM votes')
        all_hashes = [row[0] for row in c.fetchall()]

    searched_hash = None
    found = False
    if request.method == 'POST':
        searched_hash = request.form.get('receipt', '').strip()
        if searched_hash in all_hashes:
            found = True

    return render_template("verify.html", all_hashes=all_hashes, searched_hash=searched_hash, found=found)

# ---- Signup route (single, working) ----
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    data = request.get_json()
    if not data:
        return jsonify({'message':'No data received'}), 400

    name = data.get('name','').strip()
    cnic = data.get('cnic','').strip()
    email = data.get('email','').strip()
    password = data.get('password','')

    if not (name and cnic and email and password):
        return jsonify({'message':'All fields are required'}), 400

    if not cnic.isdigit() or len(cnic) != 13:
        return jsonify({'message':'CNIC must be 13 digits'}), 400

    import re
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'message':'Invalid email'}), 400

    if len(password) < 10 or not re.search(r'[A-Z]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return jsonify({'message':'Password does not meet requirements'}), 400

    # Check pre-registered voter exists and password_hash is NULL
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM voters WHERE cnic=? AND name=? AND password_hash IS NULL', (cnic, name))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'message':'CNIC or Name not valid or already registered'}), 400

    voter_id = row[0]

    # Generate Dilithium keys
    pk, sk = generate_keys()

    # Update DB with hashed password, email, and generated keys
    c.execute('''
        UPDATE voters
        SET password_hash=?, email=?, dilithium_pubkey=?, dilithium_privkey=?
        WHERE id=?
    ''', (generate_password_hash(password), email, pk, sk, voter_id))
    conn.commit()
    conn.close()

    return jsonify({'message':'Signup successful! You can now log in.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
