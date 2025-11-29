from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils import verify_agent_key
from utils import is_voting_open
from flask import render_template
import sqlite3
from flask import request, jsonify
from face_model import verify_face
import base64
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = 'your-secret-key'





@app.route('/voter_validation', methods=['GET', 'POST'])
def voter_validation():
    error = None

    # ---------- GET REQUEST ----------
    # Show the form and optionally an error message (e.g. after face timeout)
    if request.method == 'GET':
        # If face verification failed or timed out, show a clear message
        if request.args.get('face_failed') == '1':
            error = "Voter not recognized. Cannot proceed to voting."
        return render_template("voter_verify.html", error=error)

    # ---------- POST REQUEST ----------
    # This happens when the agent submits name + CNIC
    name = (request.form.get('name') or '').strip()
    cnic = (request.form.get('cnic') or '').strip()

    if not name or not cnic:
        error = "Name and CNIC are required."
        return render_template("voter_verify.html", error=error)

    conn = sqlite3.connect('nadra.db')
    c = conn.cursor()
    c.execute("SELECT * FROM voters WHERE name=? AND cnic=?", (name, cnic))
    voter = c.fetchone()
    conn.close()

    if voter:
        # Save voter for next step (face recognition)
        session['voter_name'] = name
        session['voter_cnic'] = cnic
        session['face_verified'] = False  # reset for each voter
        return redirect(url_for('verify_face_page'))
    else:
        error = "Voter not found in NADRA database."
        return render_template("voter_verify.html", error=error)


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


@app.route('/vote')
def vote_page():
    if not is_voting_open():
        return render_template('voting_closed.html')
    return render_template('vote.html')

@app.route('/verify_face')
def verify_face_page():
    # Make sure we have a voter selected from NADRA validation
    if 'voter_cnic' not in session or 'voter_name' not in session:
        flash("Please verify voter details (name + CNIC) first.")
        return redirect(url_for('voter_validation'))

    return render_template('verify_face.html')

@app.route('/')
def index():
    return redirect(url_for('agent_login'))

@app.route('/verify_face_stream', methods=['POST'])
def verify_face_stream():
    cnic = session.get('voter_cnic')
    if not cnic:
        return jsonify({"status": "error", "message": "No voter in session."}), 400

    data = request.get_json(silent=True) or {}
    image_data = data.get("image")
    if not image_data:
        return jsonify({"status": "error", "message": "No image provided."}), 200

    try:
        # split data URL
        if "," in image_data:
            _, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        img_bytes = base64.b64decode(encoded)
        if not img_bytes:
            # instead of crashing OpenCV, just say "no frame"
            return jsonify({"status": "error", "message": "Empty image buffer."}), 200

        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"status": "error", "message": "Could not decode frame."}), 200

        ok = verify_face(cnic, frame)

        if ok:
            session['face_verified'] = True
            return jsonify({"status": "verified"})
        else:
            return jsonify({"status": "unverified"})

    except Exception as e:
        print("Error in /verify_face_stream:", e)
        return jsonify({"status": "error", "message": "Internal error during face verification."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

