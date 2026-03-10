print("Script started.")
from flask import Flask, render_template, request, redirect, session
import random

from db import candidates, get_session, get_voter_by_credentials, init_db, voters, votes

app = Flask(__name__)
app.secret_key = "secretkey"
print("Flask app initialized.")

# Initialize database schema (works for Postgres or SQLite via DATABASE_URL)
try:
    init_db()
    print("Database initialized successfully.")
except Exception as e:
    print(f"Error initializing database: {e}")


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        aadhaar = request.form['aadhaar']
        mobile = request.form['mobile']
        password = request.form['password']

        with get_session() as session_db:
            session_db.execute(
                voters.insert().values(
                    name=name,
                    aadhaar=aadhaar,
                    mobile=mobile,
                    password=password,
                )
            )
            session_db.commit()
        return "Registration Successful"
    return render_template('register.html')


# ---------------- LOGIN + OTP ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        password = request.form['password']

        with get_session() as session_db:
            user = get_voter_by_credentials(session_db, aadhaar, password)

            if user:
                otp = str(random.randint(100000, 999999))
                session_db.execute(
                    voters.update()
                    .where(voters.c.aadhaar == aadhaar)
                    .values(otp=otp)
                )
                session_db.commit()
                session['aadhaar'] = aadhaar
                return f"OTP (Simulation): <b>{otp}</b> <br><a href='/verify'>Verify OTP</a>"
            else:
                return "Invalid Login"
    return render_template('login.html')


# ---------------- OTP VERIFY ----------------
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        otp = request.form['otp']
        aadhaar = session['aadhaar']

        with get_session() as session_db:
            result = session_db.execute(
                voters.select().where(
                    voters.c.aadhaar == aadhaar,
                    voters.c.otp == otp,
                )
            ).mappings().first()

            if result:
                session['voter_id'] = result['voter_id']
                return redirect('/vote')
            else:
                return "Invalid OTP"
    return render_template('otp.html')


# ---------------- VOTING ----------------
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    voter_id = session.get('voter_id')

    with get_session() as session_db:
        voted_row = session_db.execute(
            voters.select()
            .with_only_columns(voters.c.has_voted)
            .where(voters.c.voter_id == voter_id)
        ).first()

        if voted_row and voted_row[0]:
            return "You have already voted!"

        candidates_list = list(
            session_db.execute(candidates.select()).mappings().all()
        )

        if request.method == 'POST':
            cid = int(request.form['candidate'])
            session_db.execute(
                votes.insert().values(voter_id=voter_id, candidate_id=cid)
            )
            session_db.execute(
                voters.update()
                .where(voters.c.voter_id == voter_id)
                .values(has_voted=True)
            )
            session_db.commit()
            return "Vote Submitted Successfully"

    return render_template('vote.html', candidates=candidates_list)


# ---------------- ADMIN ----------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        party = request.form['party']
        with get_session() as session_db:
            session_db.execute(
                candidates.insert().values(
                    name=name,
                    party=party,
                )
            )
            session_db.commit()
    return render_template('admin.html')


# ---------------- RESULT ----------------
@app.route('/result')
def result():
    from sqlalchemy import func as sa_func
    from sqlalchemy import select as sa_select

    with get_session() as session_db:
        stmt = (
            sa_select(
                candidates.c.name,
                sa_func.count(votes.c.vote_id),
            )
            .select_from(
                candidates.outerjoin(
                    votes, candidates.c.candidate_id == votes.c.candidate_id
                )
            )
            .group_by(candidates.c.candidate_id)
        )
        rows = session_db.execute(stmt).all()
        data = [(row[0], row[1]) for row in rows]
    return render_template('result.html', data=data)


if __name__ == '__main__':
    print("Entering main block.")
    app.run(debug=True)
    print("Flask app running at: http://127.0.0.1:5000/")

