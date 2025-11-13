# app.py
import os
import sqlite3
import base64
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

# pqcrypto stubs (replace with real implementations later)
from pqcrypto.kyber_dilithium_stub import (
    get_kyber_public_bytes,
    kyber_decapsulate_bytes,
    dilithium_verify_bytes,
)
from pqcrypto.bfv_stub import (
    bfv_encrypt_vote_proto,
    bfv_add_and_decrypt_all_proto,
    bfv_init_proto,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'voters.db')

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'dev-secret-key-change-this'  # change in production

# ---- DB helpers ----
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cnic TEXT UNIQUE,
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

init_db()
bfv_init_proto()  # initialize BFV prototype (stub or real)

# ---- Simple registration helper (for testing) ----
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return """
        <h3>Dev register (use only during development)</h3>
        <form method="post">
            CNIC: <input name="cnic"><br>
            Password: <input name="password" type="password"><br>
            <button>Register</button>
        </form>
        """
    cnic = request.form.get('cnic').strip()
    password = request.form.get('password')
    if not (cnic and password):
        return "Missing fields", 400

    # For prototype, store empty Dilithium pubkey (replace later)
    dilithium_pk = b''

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO voters (cnic, password_hash, dilithium_pubkey) VALUES (?, ?, ?)',
                  (cnic, generate_password_hash(password), dilithium_pk))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "CNIC already registered", 409
    conn.close()
    return f"Registered {cnic}. You can now log in."

# ---- Routes: pages ----
@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/vote', methods=['GET'])
def vote_page():
    if 'cnic' not in session:
        return redirect(url_for('login_page'))
    return render_template('vote.html')

@app.route('/results', methods=['GET'])
def results_page():
    tally = bfv_add_and_decrypt_all_proto()
    return render_template('results.html', tally=tally)

# ---- AJAX endpoints ----
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
    if not row:
        return jsonify({'message':'CNIC not registered'}), 400
    pw_hash = row[0]
    if not check_password_hash(pw_hash, password):
        return jsonify({'message':'Incorrect password'}), 401

    # Directly authenticate user (no face verification)
    session['cnic'] = cnic
    return jsonify({'success': True, 'message': 'Login successful'})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return ('', 204)

# ---- PQC endpoints & vote submission ----
@app.route('/pqc/kyber_pub', methods=['GET'])
def get_kyber_pk():
    pk_bytes = get_kyber_public_bytes()
    return jsonify({'kyber_pk': base64.b64encode(pk_bytes).decode()})

@app.route('/vote', methods=['POST'])
def submit_vote():
    if 'cnic' not in session:
        return jsonify({'message':'Not authenticated'}), 403

    if request.is_json:
        data = request.get_json()
        kem = data.get('kem_ciphertext')
        enc_payload = data.get('enc_payload')
        signature = data.get('signature')

        if not (kem and enc_payload and signature):
            # plaintext fallback
            candidate = data.get('candidate')
            if not candidate:
                return jsonify({'message':'No vote provided'}), 400
            bfv_cipher = bfv_encrypt_vote_proto(candidate, voter=session['cnic'])
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO votes (bfv_cipher, voter_cnic, signature) VALUES (?, ?, ?)',
                      (bfv_cipher, session['cnic'], b''))
            conn.commit()
            conn.close()
            return jsonify({'message':'Vote stored (plaintext prototype).'}), 200

        # decode base64
        try:
            kem_b = base64.b64decode(kem)
            enc_b = base64.b64decode(enc_payload)
            sig_b = base64.b64decode(signature)
        except Exception:
            return jsonify({'message':'Malformed base64 fields'}), 400

        # Verify signature (Dilithium)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT dilithium_pubkey FROM voters WHERE cnic=?', (session['cnic'],))
        row = c.fetchone()
        conn.close()
        dilithium_pk = row[0] if row else b''
        if not dilithium_verify_bytes(dilithium_pk, kem_b + enc_b, sig_b):
            return jsonify({'message':'Signature verification failed'}), 401

        # decapsulate Kyber & re-encrypt under BFV
        try:
            plaintext = kyber_decapsulate_bytes(kem_b, enc_b)
        except Exception as e:
            return jsonify({'message':'Decapsulation failed', 'err': str(e)}), 400

        bfv_cipher = bfv_encrypt_vote_proto(plaintext.decode(), voter=session['cnic'])
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO votes (bfv_cipher, voter_cnic, signature) VALUES (?, ?, ?)',
                  (bfv_cipher, session['cnic'], sig_b))
        conn.commit()
        conn.close()
        return jsonify({'message':'Vote stored (PQC path).'}), 200

    return jsonify({'message':'Unsupported media type'}), 415

# ---- admin API to fetch JSON results (decrypted) ----
@app.route('/api/results', methods=['GET'])
def api_results():
    tally = bfv_add_and_decrypt_all_proto()
    return jsonify({'tally': tally})

# ---- STATIC / simple health ----
@app.route('/static/<path:fp>')
def static_proxy(fp):
    return send_from_directory('static', fp)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    data = request.get_json()
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

    # check CNIC + Name in DB (voters table)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM voters WHERE cnic=? AND password_hash IS NULL', (cnic,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'message':'CNIC not valid or already registered'}), 400

    # update the record with email and hashed password
    c.execute('UPDATE voters SET password_hash=?, face_path=NULL WHERE cnic=?',
              (generate_password_hash(password), cnic))
    conn.commit()
    conn.close()
    return jsonify({'message':'Signup successful! You can now log in.'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
