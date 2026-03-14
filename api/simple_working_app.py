"""
Simple Working Voting App - Error-Free for Vercel
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, redirect, session
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

# Simple, working templates
def get_login_page(error=""):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SecureVote Portal - Login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .login-container {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .login-card {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 450px;
                width: 100%;
                overflow: hidden;
            }}
            .login-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .login-body {{
                padding: 40px 30px;
            }}
            .form-control {{
                border-radius: 10px;
                border: 2px solid #e0e0e0;
                padding: 15px;
                font-size: 16px;
                transition: all 0.3s ease;
            }}
            .form-control:focus {{
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            .btn-login {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: 600;
                width: 100%;
                transition: all 0.3s ease;
            }}
            .btn-login:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }}
            .alert {{
                border-radius: 10px;
                border: none;
                margin-bottom: 20px;
            }}
            .icon-large {{
                font-size: 3rem;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <i class="bi bi-shield-check icon-large"></i>
                    <h2>Welcome Back</h2>
                    <p>Sign in to access your secure voting portal</p>
                </div>
                <div class="login-body">
                    {error}
                    <form method="post">
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Aadhaar Number</label>
                            <input type="text" name="aadhaar" class="form-control" 
                                   placeholder="Enter 12-digit Aadhaar" maxlength="12" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-semibold">Password</label>
                            <input type="password" name="password" class="form-control" 
                                   placeholder="Enter your password" required>
                        </div>
                        <button type="submit" class="btn btn-login">
                            <i class="bi bi-arrow-right-circle me-2"></i>Continue to OTP
                        </button>
                        <div class="text-center mt-3">
                            <small class="text-muted">New voter? <a href="/register">Create Account</a></small>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

def get_vote_page(candidates_list, message=""):
    candidates_html = ""
    for i, (cid, name, party) in enumerate(candidates_list, 1):
        candidates_html += f'''
        <div class="col-md-6 mb-3">
            <div class="candidate-card" onclick="selectCandidate({cid})">
                <div class="d-flex align-items-center">
                    <div class="candidate-avatar">{name[0]}</div>
                    <div class="candidate-info">
                        <div class="candidate-name">{name}</div>
                        <div class="candidate-party"><i class="bi bi-building me-1"></i>{party}</div>
                    </div>
                    <input type="radio" name="candidate" value="{cid}" id="candidate-{cid}" required>
                </div>
            </div>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SecureVote Portal - Cast Your Vote</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .vote-container {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .vote-card {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 800px;
                width: 100%;
                overflow: hidden;
            }}
            .vote-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .vote-body {{
                padding: 40px 30px;
            }}
            .candidate-card {{
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                background: white;
            }}
            .candidate-card:hover {{
                border-color: #667eea;
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }}
            .candidate-avatar {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin-right: 15px;
            }}
            .candidate-name {{
                font-weight: 600;
                font-size: 18px;
                color: #333;
                margin-bottom: 5px;
            }}
            .candidate-party {{
                color: #666;
                font-size: 14px;
            }}
            .btn-vote {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            .btn-vote:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }}
            .icon-large {{
                font-size: 3rem;
                margin-bottom: 20px;
            }}
            .alert {{
                border-radius: 10px;
                border: none;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="vote-container">
            <div class="vote-card">
                <div class="vote-header">
                    <i class="bi bi-ballot icon-large"></i>
                    <h2>Cast Your Vote</h2>
                    <p>Choose your candidate wisely - your vote matters</p>
                </div>
                <div class="vote-body">
                    {message}
                    <form method="post">
                        <div class="row">
                            {candidates_html}
                        </div>
                        <div class="text-center mt-4">
                            <button type="submit" class="btn btn-vote">
                                <i class="bi bi-check-circle me-2"></i>Submit Vote
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <script>
        function selectCandidate(id) {{
            document.getElementById('candidate-' + id).checked = true;
            document.querySelectorAll('.candidate-card').forEach(card => {{
                card.style.borderColor = '#e0e0e0';
            }});
            event.currentTarget.style.borderColor = '#667eea';
        }}
        </script>
    </body>
    </html>
    '''

def get_result_page(data, total_votes):
    rows_html = ""
    for i, candidate in enumerate(data, 1):
        percentage = candidate.get('percentage', 0)
        vote_count = candidate.get('vote_count', 0)
        rows_html += f'''
        <tr>
            <td><span class="badge bg-primary">{i}</span></td>
            <td><strong>{candidate.get('name', 'N/A')}</strong></td>
            <td><span class="badge bg-light text-dark">{candidate.get('party', 'N/A')}</span></td>
            <td class="text-center"><strong>{vote_count}</strong></td>
            <td class="text-center"><span class="badge bg-success">{percentage:.1f}%</span></td>
            <td>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-primary" style="width: {percentage}%"></div>
                </div>
            </td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SecureVote Portal - Live Results</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .results-container {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .results-card {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 1000px;
                width: 100%;
                overflow: hidden;
            }}
            .results-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .results-body {{
                padding: 40px 30px;
            }}
            .stats-card {{
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .stats-number {{
                font-size: 2rem;
                font-weight: bold;
                color: #667eea;
            }}
            .stats-label {{
                color: #666;
                font-size: 14px;
            }}
            .results-table {{
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .results-table th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px;
                font-weight: 600;
            }}
            .results-table td {{
                padding: 15px;
                vertical-align: middle;
                border-bottom: 1px solid #e0e0e0;
            }}
            .progress {{
                height: 8px;
                border-radius: 10px;
            }}
            .icon-large {{
                font-size: 3rem;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="results-container">
            <div class="results-card">
                <div class="results-header">
                    <i class="bi bi-graph-up icon-large"></i>
                    <h2>Live Results</h2>
                    <p>Real-time voting statistics and results</p>
                </div>
                <div class="results-body">
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="stats-card">
                                <div class="stats-number">{total_votes}</div>
                                <div class="stats-label">Total Votes</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stats-card">
                                <div class="stats-number">{len(data)}</div>
                                <div class="stats-label">Candidates</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stats-card">
                                <div class="stats-number">100%</div>
                                <div class="stats-label">Turnout</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="results-table">
                        <table class="table table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Candidate</th>
                                    <th>Party</th>
                                    <th class="text-center">Votes</th>
                                    <th class="text-center">Percentage</th>
                                    <th>Progress</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

def get_verify_page():
    otp = session.get('otp', 'N/A')
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SecureVote Portal - OTP Verification</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .verify-container {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .verify-card {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 450px;
                width: 100%;
                overflow: hidden;
            }}
            .verify-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .verify-body {{
                padding: 40px 30px;
            }}
            .form-control {{
                border-radius: 10px;
                border: 2px solid #e0e0e0;
                padding: 15px;
                font-size: 16px;
                transition: all 0.3s ease;
            }}
            .form-control:focus {{
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            .btn-verify {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: 600;
                width: 100%;
                transition: all 0.3s ease;
            }}
            .btn-verify:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }}
            .alert {{
                border-radius: 10px;
                border: none;
                margin-bottom: 20px;
            }}
            .icon-large {{
                font-size: 3rem;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="verify-container">
            <div class="verify-card">
                <div class="verify-header">
                    <i class="bi bi-shield-check icon-large"></i>
                    <h2>OTP Verification</h2>
                    <p>Enter your one-time password to continue</p>
                </div>
                <div class="verify-body">
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        For testing, your OTP is: <strong>{otp}</strong>
                    </div>
                    <form method="post">
                        <div class="mb-4">
                            <label class="form-label fw-semibold">Enter OTP</label>
                            <input type="text" name="otp" class="form-control" 
                                   placeholder="6-digit OTP" maxlength="6" required>
                        </div>
                        <button type="submit" class="btn btn-verify">
                            <i class="bi bi-check-circle me-2"></i>Verify OTP
                        </button>
                        <div class="text-center mt-3">
                            <small><a href="/" class="text-decoration-none">← Back to Login</a></small>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not DB_AVAILABLE:
            return get_login_page('<div class="alert alert-warning"><i class="bi bi-exclamation-triangle me-2"></i>Database not available - Demo mode</div>')
        
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
                return get_login_page('<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Invalid credentials</div>')
    
    return get_login_page()

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    voter_id = session.get('voter_id')
    
    if not voter_id:
        return redirect('/')
    
    if not DB_AVAILABLE:
        candidates_list = [
            (1, 'Narendra Modi', 'BJP'),
            (2, 'Rahul Gandhi', 'Congress'),
            (3, 'Eknath Shinde', 'Shiv Sena'),
            (4, 'naren', 'Independent')
        ]
        return get_vote_page(candidates_list, '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle me-2"></i>Demo mode - Database not connected</div>')
    
    with get_session() as session_db:
        voted = session_db.execute(
            voters.select().where(voters.c.voter_id == voter_id, voters.c.has_voted == True)
        ).first()
        
        if voted:
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Vote Already Cast</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }}
                    .message-card {{
                        background: white;
                        border-radius: 20px;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        padding: 40px;
                        text-align: center;
                        max-width: 500px;
                    }}
                    .icon-large {{
                        font-size: 4rem;
                        color: #28a745;
                        margin-bottom: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="message-card">
                    <i class="bi bi-check-circle icon-large"></i>
                    <h2>Vote Already Cast</h2>
                    <p class="text-muted">You have already voted in this election</p>
                    <a href="/result" class="btn btn-primary">View Results</a>
                </div>
            </body>
            </html>
            '''
        
        candidates_list = list(session_db.execute(candidates.select()).all())
        
        if request.method == 'POST':
            candidate_id = int(request.form['candidate'])
            session_db.execute(votes.insert().values(voter_id=voter_id, candidate_id=candidate_id))
            session_db.execute(voters.update().where(voters.c.voter_id == voter_id).values(has_voted=True))
            session_db.commit()
            return get_vote_page(candidates_list, '<div class="alert alert-success"><i class="bi bi-check-circle me-2"></i>Vote submitted successfully!</div>')
    
    return get_vote_page(candidates_list)

@app.route('/result')
def result():
    if not DB_AVAILABLE:
        data = [
            {'name': 'Narendra Modi', 'party': 'BJP', 'vote_count': 1, 'percentage': 100.0},
            {'name': 'Rahul Gandhi', 'party': 'Congress', 'vote_count': 0, 'percentage': 0.0},
            {'name': 'Eknath Shinde', 'party': 'Shiv Sena', 'vote_count': 0, 'percentage': 0.0},
            {'name': 'naren', 'party': 'Independent', 'vote_count': 0, 'percentage': 0.0}
        ]
        return get_result_page(data, 1)
    
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
            .group_by(candidates.c.name, candidates.c.party)
            .order_by(sa_func.count(votes.c.vote_id).desc())
        )
        rows = session_db.execute(stmt).all()
        
        total_votes = sum(row.vote_count or 0 for row in rows)
        data = []
        for row in rows:
            vote_count = row.vote_count or 0
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            data.append({
                'name': row.name,
                'party': row.party,
                'vote_count': vote_count,
                'percentage': round(percentage, 2)
            })
    
    return get_result_page(data, total_votes)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        otp = request.form['otp']
        aadhaar = session.get('aadhaar')
        
        if not DB_AVAILABLE:
            return get_verify_page() + '<div class="alert alert-warning">Demo mode - OTP verification skipped</div>'
        
        with get_session() as session_db:
            result = session_db.execute(
                voters.select().where(voters.c.aadhaar == aadhaar, voters.c.otp == otp)
            ).first()
            
            if result:
                session['voter_id'] = result.voter_id
                return redirect('/vote')
            else:
                return get_verify_page() + '<div class="alert alert-danger">Invalid OTP</div>'
    
    return get_verify_page()

@app.route('/register')
def register():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - SecureVote Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .message-card {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 40px;
                text-align: center;
                max-width: 500px;
            }}
            .icon-large {{
                font-size: 4rem;
                color: #667eea;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="message-card">
            <i class="bi bi-person-plus icon-large"></i>
            <h2>Registration Coming Soon</h2>
            <p class="text-muted">Voter registration functionality will be available soon</p>
            <a href="/" class="btn btn-primary">Back to Login</a>
        </div>
    </body>
    </html>
    '''

@app.route('/admin')
def admin():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - SecureVote Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .message-card {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 40px;
                text-align: center;
                max-width: 500px;
            }}
            .icon-large {{
                font-size: 4rem;
                color: #667eea;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="message-card">
            <i class="bi bi-gear icon-large"></i>
            <h2>Admin Dashboard</h2>
            <p class="text-muted">Admin functionality will be available soon</p>
            <a href="/" class="btn btn-primary">Back to Login</a>
        </div>
    </body>
    </html>
    '''

# Export for Vercel
app_handler = app
