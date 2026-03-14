"""
Final Voting App with Database Connection for Vercel
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, redirect, session, render_template_string
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

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Login - Voting Portal</title></head>
<body>
    <h1>Online Voting Portal</h1>
    <h2>Login</h2>
    {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
    <form method="post">
        <label>Aadhaar: <input type="text" name="aadhaar" required></label><br><br>
        <label>Password: <input type="password" name="password" required></label><br><br>
        <button type="submit">Login</button>
    </form>
    <p><a href="/register">New Voter? Register Here</a></p>
    <p><a href="/vote">Go to Voting (Demo)</a></p>
</body>
</html>
'''

VOTE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Vote - Voting Portal</title></head>
<body>
    <h1>Online Voting Portal</h1>
    <h2>Cast Your Vote</h2>
    {% if message %}<p style="color: green;">{{ message }}</p>{% endif %}
    <form method="post">
        <h3>Select your candidate:</h3>
        {% for candidate in candidates %}
        <input type="radio" name="candidate" value="{{ candidate[0] }}" required> 
        {{ candidate[1] }} - {{ candidate[2] }}<br>
        {% endfor %}
        <br><button type="submit">Submit Vote</button>
    </form>
    <p><a href="/result">View Results</a></p>
    <p><a href="/">Back to Login</a></p>
</body>
</html>
'''

RESULT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Results - Voting Portal</title></head>
<body>
    <h1>Online Voting Portal</h1>
    <h2>Election Results</h2>
    <table border="1">
        <tr><th>Candidate</th><th>Party</th><th>Votes</th><th>Percentage</th></tr>
        {% for row in data %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ "%.1f"|format(row[3]) }}%</td>
        </tr>
        {% endfor %}
    </table>
    <p><strong>Total Votes: {{ total_votes }}</strong></p>
    <p><a href="/vote">Back to Voting</a></p>
    <p><a href="/">Back to Login</a></p>
</body>
</html>
'''

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not DB_AVAILABLE:
            return render_template_string(LOGIN_TEMPLATE, error="Database not available")
        
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
                return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if not DB_AVAILABLE:
        # Show mock candidates if database not available
        candidates_list = [
            (1, 'Narendra Modi', 'BJP'),
            (2, 'Rahul Gandhi', 'Congress'),
            (3, 'Eknath Shinde', 'Shiv Sena'),
            (4, 'naren', 'Independent')
        ]
        return render_template_string(VOTE_TEMPLATE, candidates=candidates_list, message="Demo mode - Database not connected")
    
    candidates_list = list(get_session().execute(candidates.select()).all())
    
    if request.method == 'POST':
        voter_id = session.get('voter_id')
        if not voter_id:
            return redirect('/')
        
        with get_session() as session_db:
            # Check if already voted
            voted = session_db.execute(
                voters.select().where(voters.c.voter_id == voter_id, voters.c.has_voted == True)
            ).first()
            
            if voted:
                return render_template_string(VOTE_TEMPLATE, candidates=candidates_list, message="You have already voted!")
            
            # Record vote
            candidate_id = int(request.form['candidate'])
            session_db.execute(votes.insert().values(voter_id=voter_id, candidate_id=candidate_id))
            session_db.execute(voters.update().where(voters.c.voter_id == voter_id).values(has_voted=True))
            session_db.commit()
            
            return render_template_string(VOTE_TEMPLATE, candidates=candidates_list, message="Vote submitted successfully!")
    
    return render_template_string(VOTE_TEMPLATE, candidates=candidates_list)

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
        return render_template_string(RESULT_TEMPLATE, data=data, total_votes=1)
    
    # Get real results
    from sqlalchemy import func as sa_func
    from sqlalchemy import select as sa_select
    
    with get_session() as session_db:
        stmt = (
            sa_select(
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
            data.append((row.name, row.party, vote_count, percentage))
    
    return render_template_string(RESULT_TEMPLATE, data=data, total_votes=total_votes)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        otp = request.form['otp']
        aadhaar = session.get('aadhaar')
        
        if not DB_AVAILABLE:
            return f"OTP verification (Demo): {otp} - Database not available"
        
        with get_session() as session_db:
            result = session_db.execute(
                voters.select().where(voters.c.aadhaar == aadhaar, voters.c.otp == otp)
            ).first()
            
            if result:
                session['voter_id'] = result.voter_id
                return redirect('/vote')
            else:
                return "Invalid OTP"
    
    return f'''
    <h1>OTP Verification</h1>
    <p>Your OTP is: <strong>{session.get('otp', 'N/A')}</strong></p>
    <form method="post">
        <label>Enter OTP: <input type="text" name="otp" required></label><br><br>
        <button type="submit">Verify</button>
    </form>
    <p><a href="/">Back to Login</a></p>
    '''

@app.route('/register')
def register():
    return '''
    <h1>Register New Voter</h1>
    <p>Registration functionality coming soon!</p>
    <p><a href="/">Back to Login</a></p>
    '''

@app.route('/admin')
def admin():
    return '''
    <h1>Admin Dashboard</h1>
    <p>Admin functionality coming soon!</p>
    <p><a href="/">Back to Login</a></p>
    '''

# Export for Vercel
app_handler = app
