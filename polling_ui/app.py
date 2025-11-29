from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from utils import verify_agent_key, is_voting_open
import sqlite3
import base64
import cv2
import numpy as np
from face_model import verify_face

app = Flask(__name__)
app.secret_key = 'your-secret-key'


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
        return jsonify({"status": "error", "message": "No voter in session."})

    data = request.get_json(silent=True) or {}
    image_data = data.get("image")

    if not image_data:
        return jsonify({"status": "error", "message": "Empty frame"})

    try:
        if "," in image_data:
            _, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Image decode failed"})

        ok = verify_face(cnic, frame)

        if ok:
            session['face_verified'] = True
            return jsonify({"status": "verified", "redirect": url_for("vote_page")})
        else:
            return jsonify({"status": "unverified"})

    except Exception as e:
        print("Face error:", e)
        return jsonify({"status": "error", "message": "Internal error"})


# ---------------------------
# VOTING PAGE
# ---------------------------
@app.route('/vote')
def vote_page():
    if not session.get('face_verified'):
        flash("Face verification required.")
        return redirect(url_for('voter_validation'))

    if not is_voting_open():
        return render_template('voting_closed.html')

    return render_template('vote.html')



# ---------------------------
# SUBMIT VOTE
# ---------------------------
@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if not session.get('face_verified'):
        return "Error: Face not verified."

    candidate = request.form.get("candidate")

    # TODO: Save to votes.db
    return "Your vote has been submitted successfully!"



@app.route('/')
def index():
    return redirect(url_for('agent_login'))



if __name__ == '__main__':
    app.run(debug=True, port=5000)
