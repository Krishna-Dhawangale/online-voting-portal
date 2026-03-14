"""
Beautiful Voting App with Original UI and Database Connection for Vercel
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, redirect, session, render_template
import random

app = Flask(__name__)
app.secret_key = "secretkey"

# Database connection
try:
    from db import candidates, get_session, get_voter_by_credentials, init_db, voters, votes
    print("Database connected successfully!")
    DB_AVAILABLE = True
except ImportError as e:
    print(f"Database import error: {e}")
    DB_AVAILABLE = False

# Initialize database if available
if DB_AVAILABLE:
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database init error: {e}")

# Routes with original templates
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not DB_AVAILABLE:
            return render_template('login.html', error="Database not available")
        
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
                session['otp'] = otp
                return redirect('/verify')
            else:
                return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        otp = request.form['otp']
        aadhaar = session.get('aadhaar')
        
        if not DB_AVAILABLE:
            return render_template('otp.html', error="Database not available")
        
        with get_session() as session_db:
            result = session_db.execute(
                voters.select().where(voters.c.aadhaar == aadhaar, voters.c.otp == otp)
            ).first()
            
            if result:
                session['voter_id'] = result.voter_id
                return redirect('/vote')
            else:
                return render_template('otp.html', error="Invalid OTP")
    
    return render_template('otp.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    voter_id = session.get('voter_id')
    
    if not voter_id:
        return redirect('/')
    
    if not DB_AVAILABLE:
        # Show mock candidates if database not available
        candidates_list = [
            (1, 'Narendra Modi', 'BJP'),
            (2, 'Rahul Gandhi', 'Congress'),
            (3, 'Eknath Shinde', 'Shiv Sena'),
            (4, 'naren', 'Independent')
        ]
        return render_template('vote.html', candidates=candidates_list, message="Demo mode - Database not connected")
    
    with get_session() as session_db:
        # Check if already voted
        voted = session_db.execute(
            voters.select().where(voters.c.voter_id == voter_id, voters.c.has_voted == True)
        ).first()
        
        if voted:
            return "You have already voted!"
        
        candidates_list = list(session_db.execute(candidates.select()).all())
        
        if request.method == 'POST':
            candidate_id = int(request.form['candidate'])
            session_db.execute(votes.insert().values(voter_id=voter_id, candidate_id=candidate_id))
            session_db.execute(voters.update().where(voters.c.voter_id == voter_id).values(has_voted=True))
            session_db.commit()
            return render_template('vote_success.html')
    
    return render_template('vote.html', candidates=candidates_list)

@app.route('/result')
def result():
    if not DB_AVAILABLE:
        # Show mock results
        data = [
            ('Narendra Modi', 'BJP', 1, 100.0),
            ('Rahul Gandhi', 'Congress', 0, 0.0),
            ('Eknath Shinde', 'Shiv Sena', 0, 0.0),
            ('naren', 'Independent', 0, 0.0)
        ]
        return render_template('result.html', data=data, total_votes=1)
    
    # Get real results
    from sqlalchemy import func as sa_func
    from sqlalchemy import select as sa_select
    
    with get_session() as session_db:
        stmt = (
            sa_select(
                candidates.c.candidate_id,
                candidates.c.name,
                candidates.c.party,
                sa_func.count(votes.c.vote_id).label('vote_count'),
            )
            .select_from(candidates.outerjoin(votes, candidates.c.candidate_id == votes.c.candidate_id))
            .group_by(candidates.c.candidate_id, candidates.c.name, candidates.c.party)
            .order_by(sa_func.count(votes.c.vote_id).desc())
        )
        rows = session_db.execute(stmt).all()
        
        total_votes = sum(row.vote_count or 0 for row in rows)
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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if not DB_AVAILABLE:
            return render_template('admin.html', error="Database not available")
        
        name = request.form['name']
        party = request.form['party']
        
        with get_session() as session_db:
            session_db.execute(candidates.insert().values(name=name, party=party))
            session_db.commit()
    
    if not DB_AVAILABLE:
        return render_template('admin.html', voters=[])
    
    # Get detailed voting information for admin
    with get_session() as session_db:
        from sqlalchemy import func as sa_func
        from sqlalchemy import select as sa_select
        
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

# Export for Vercel
app_handler = app
