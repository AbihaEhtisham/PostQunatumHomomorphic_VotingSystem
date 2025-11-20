from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils import verify_agent_key
from utils import is_voting_open
from flask import render_template
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'



@app.route('/voter_validation', methods=['GET', 'POST'])
def voter_validation():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        cnic = request.form.get('cnic').strip()

        conn = sqlite3.connect('nadra.db')
        c = conn.cursor()
        c.execute("SELECT * FROM voters WHERE name=? AND cnic=?", (name, cnic))
        voter = c.fetchone()
        conn.close()

        if voter:
            # Save voter for next step (face recognition)
            session['voter_name'] = name
            session['voter_cnic'] = cnic
            return redirect(url_for('verify_face'))
        else:
            return render_template("voter_verify.html", error="Voter not found in NADRA database.")

    return render_template("voter_verify.html")

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

@app.route('/')
def index():
    return redirect(url_for('agent_login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

