print("Script started.")
from flask import Flask, render_template, request, redirect, session
import random

from db import candidates, get_session, get_voter_by_credentials, init_db, voters, votes

app = Flask(__name__, template_folder='.', static_folder=None)
app.secret_key = "secretkey"
print("Flask app initialized.")

# Configure for Vercel deployment
import os
if os.environ.get('VERCEL'):
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize database schema (works for Postgres or SQLite via DATABASE_URL)
try:
    init_db()
    print("Database initialized successfully.")
    
    # Seed initial data if running on Vercel and no candidates exist
    if os.environ.get('VERCEL'):
        with get_session() as session_db:
            existing_candidates = session_db.execute(candidates.select()).first()
            if not existing_candidates:
                print("Seeding initial candidates for Vercel deployment...")
                session_db.execute(candidates.insert().values(name="Narendra Modi", party="BJP"))
                session_db.execute(candidates.insert().values(name="Rahul Gandhi", party="Congress"))
                session_db.execute(candidates.insert().values(name="Eknath Shinde", party="Shiv Sena"))
                session_db.execute(candidates.insert().values(name="naren", party="Independent"))
                session_db.commit()
                print("Initial candidates seeded successfully.")
                
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
                session['otp'] = otp  # Store OTP for verification
                return redirect('/verify')
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
    
    if not voter_id:
        return redirect('/')

    with get_session() as session_db:
        voted_row = session_db.execute(
            voters.select()
            .with_only_columns(voters.c.has_voted)
            .where(voters.c.voter_id == voter_id)
        ).first()

        if voted_row and voted_row[0]:
            return "You have already voted!"

        candidates_list = list(
            session_db.execute(candidates.select()).all()
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
            return render_template('vote_success.html')

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
    
    # Get detailed voting information for admin
    with get_session() as session_db:
        from sqlalchemy import func as sa_func
        from sqlalchemy import select as sa_select
        
        # Get voters with their voting details
        voters_query = (
            sa_select(
                voters.c.voter_id,
                voters.c.name,
                voters.c.aadhaar,
                voters.c.has_voted,
                candidates.c.name.label('candidate_name'),
                candidates.c.party.label('candidate_party'),
                votes.c.voted_at
            )
            .select_from(
                voters.outerjoin(votes, voters.c.voter_id == votes.c.voter_id)
                .outerjoin(candidates, votes.c.candidate_id == candidates.c.candidate_id)
            )
            .order_by(voters.c.voter_id)
        )
        voters_data = session_db.execute(voters_query).all()
        
        # Prepare voters list
        voters_list = []
        for row in voters_data:
            voters_list.append({
                'voter_id': row.voter_id,
                'name': row.name,
                'aadhaar': row.aadhaar,
                'has_voted': row.has_voted,
                'candidate_name': row.candidate_name,
                'candidate_party': row.candidate_party,
                'voted_at': row.voted_at
            })
    
    return render_template('admin.html', voters=voters_list)


# ---------------- RESULT ----------------
@app.route('/result')
def result():
    from sqlalchemy import func as sa_func
    from sqlalchemy import select as sa_select

    with get_session() as session_db:
        # Get detailed results with candidate info and vote counts
        stmt = (
            sa_select(
                candidates.c.candidate_id,
                candidates.c.name,
                candidates.c.party,
                sa_func.count(votes.c.vote_id).label('vote_count'),
            )
            .select_from(
                candidates.outerjoin(
                    votes, candidates.c.candidate_id == votes.c.candidate_id
                )
            )
            .group_by(candidates.c.candidate_id, candidates.c.name, candidates.c.party)
            .order_by(sa_func.count(votes.c.vote_id).desc())
        )
        rows = session_db.execute(stmt).all()
        
        # Calculate total votes for percentage
        total_votes = sum(row.vote_count or 0 for row in rows)
        
        # Prepare data with percentages
        data = []
        for row in rows:
            vote_count = row.vote_count or 0
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            data.append({
                'candidate_id': row.candidate_id,
                'name': row.name,
                'party': row.party,
                'vote_count': vote_count,
                'percentage': round(percentage, 2)
            })
    
    return render_template('result.html', data=data, total_votes=total_votes)


if __name__ == '__main__':
    print("Entering main block.")
    app.run(debug=True)
    print("Flask app running at: http://127.0.0.1:5000/")

