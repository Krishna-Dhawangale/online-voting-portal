"""
Complete Voting Portal - All Pages Fully Functional
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, redirect, session, render_template_string
import random
from datetime import datetime

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

# Base template
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SecureVote Portal{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .main-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .app-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 100%;
            overflow: hidden;
        }
        .app-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .app-body {
            padding: 40px 30px;
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 15px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        .alert {
            border-radius: 10px;
            border: none;
            margin-bottom: 20px;
        }
        .icon-large {
            font-size: 3rem;
            margin-bottom: 20px;
        }
        .candidate-card {
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: white;
        }
        .candidate-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .candidate-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
            margin-right: 15px;
        }
        .progress {
            height: 8px;
            border-radius: 10px;
        }
        .stats-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        .stats-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .results-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px;
        }
        .results-table td {
            padding: 15px;
            vertical-align: middle;
            border-bottom: 1px solid #e0e0e0;
        }
        .admin-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px;
            font-size: 14px;
        }
        .admin-table td {
            padding: 12px;
            vertical-align: middle;
            border-bottom: 1px solid #e0e0e0;
            font-size: 14px;
        }
        .badge-success {
            background: #28a745;
        }
        .badge-warning {
            background: #ffc107;
            color: #000;
        }
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar-brand {
            font-weight: 700;
            color: #667eea !important;
        }
        @media (max-width: 768px) {
            .app-card {
                margin: 10px;
                max-width: 100%;
            }
            .app-header, .app-body {
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-shield-check me-2"></i>SecureVote Portal
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Login</a>
                <a class="nav-link" href="/register">Register</a>
                <a class="nav-link" href="/result">Results</a>
            </div>
        </div>
    </nav>
    <div class="main-container">
        <div class="app-card">
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
'''

# Login page
LOGIN_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}Login · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-shield-check icon-large"></i>
        <h2>Welcome Back</h2>
        <p>Sign in to access your secure voting portal</p>
    </div>
    <div class="app-body">
        {% if error %}
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
        {% endif %}
        {% if success %}
        <div class="alert alert-success">
            <i class="bi bi-check-circle me-2"></i>{{ success }}
        </div>
        {% endif %}
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
            <button type="submit" class="btn btn-primary mb-3">
                <i class="bi bi-arrow-right-circle me-2"></i>Continue to OTP
            </button>
            <div class="text-center">
                <small class="text-muted">New voter? <a href="/register">Create Account</a></small>
            </div>
        </form>
    </div>
    '''
)

# OTP page
OTP_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}OTP Verification · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-shield-check icon-large"></i>
        <h2>OTP Verification</h2>
        <p>Enter your one-time password to continue</p>
    </div>
    <div class="app-body">
        <div class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>
            For testing, your OTP is: <strong>{{ otp }}</strong>
        </div>
        {% if error %}
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
        {% endif %}
        <form method="post">
            <div class="mb-4">
                <label class="form-label fw-semibold">Enter OTP</label>
                <input type="text" name="otp" class="form-control" 
                       placeholder="6-digit OTP" maxlength="6" required>
            </div>
            <button type="submit" class="btn btn-primary mb-3">
                <i class="bi bi-check-circle me-2"></i>Verify OTP
            </button>
            <div class="text-center">
                <small><a href="/" class="text-decoration-none">← Back to Login</a></small>
            </div>
        </form>
    </div>
    '''
)

# Register page
REGISTER_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}Register · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-person-plus icon-large"></i>
        <h2>Create New Account</h2>
        <p>Register to become a verified voter</p>
    </div>
    <div class="app-body">
        {% if error %}
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
        {% endif %}
        {% if success %}
        <div class="alert alert-success">
            <i class="bi bi-check-circle me-2"></i>{{ success }}
        </div>
        {% endif %}
        <form method="post">
            <div class="mb-3">
                <label class="form-label fw-semibold">Full Name</label>
                <input type="text" name="name" class="form-control" 
                       placeholder="Enter your full name" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-semibold">Aadhaar Number</label>
                <input type="text" name="aadhaar" class="form-control" 
                       placeholder="Enter 12-digit Aadhaar" maxlength="12" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-semibold">Mobile Number</label>
                <input type="text" name="mobile" class="form-control" 
                       placeholder="Enter 10-digit mobile" maxlength="10" required>
            </div>
            <div class="mb-4">
                <label class="form-label fw-semibold">Password</label>
                <input type="password" name="password" class="form-control" 
                       placeholder="Create a strong password" required>
            </div>
            <button type="submit" class="btn btn-primary mb-3">
                <i class="bi bi-person-plus me-2"></i>Create Account
            </button>
            <div class="text-center">
                <small class="text-muted">Already have an account? <a href="/">Login</a></small>
            </div>
        </form>
    </div>
    '''
)

# Vote page
VOTE_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}Cast Your Vote · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-ballot icon-large"></i>
        <h2>Cast Your Vote</h2>
        <p>Choose your candidate wisely - your vote matters</p>
    </div>
    <div class="app-body">
        <div class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>
            Welcome, <strong>{{ voter_name }}</strong>! You are about to cast your vote.
        </div>
        {% if message %}
        <div class="alert alert-success">
            <i class="bi bi-check-circle me-2"></i>{{ message }}
        </div>
        {% endif %}
        {% if error %}
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
        {% endif %}
        <form method="post">
            {% for candidate in candidates %}
            <div class="candidate-card" onclick="selectCandidate({{ candidate[0] }})">
                <div class="d-flex align-items-center">
                    <div class="candidate-avatar">{{ candidate[1][0] }}</div>
                    <div class="flex-grow-1">
                        <div class="fw-semibold">{{ candidate[1] }}</div>
                        <div class="text-muted"><i class="bi bi-building me-1"></i>{{ candidate[2] }}</div>
                    </div>
                    <input type="radio" name="candidate" value="{{ candidate[0] }}" id="candidate-{{ candidate[0] }}" required>
                </div>
            </div>
            {% endfor %}
            <div class="text-center mt-4">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle me-2"></i>Submit Vote
                </button>
            </div>
        </form>
        <div class="text-center mt-3">
            <small><a href="/result" class="text-decoration-none">View Results</a></small>
        </div>
    </div>
    <script>
    function selectCandidate(id) {
        document.getElementById('candidate-' + id).checked = true;
        document.querySelectorAll('.candidate-card').forEach(card => {
            card.style.borderColor = '#e0e0e0';
        });
        event.currentTarget.style.borderColor = '#667eea';
    }
    </script>
    '''
)

# Results page
RESULTS_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}Live Results · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-graph-up icon-large"></i>
        <h2>Live Results</h2>
        <p>Real-time voting statistics and results</p>
    </div>
    <div class="app-body">
        <div class="row mb-4">
            <div class="col-4">
                <div class="stats-card">
                    <div class="stats-number">{{ total_votes }}</div>
                    <div class="text-muted">Total Votes</div>
                </div>
            </div>
            <div class="col-4">
                <div class="stats-card">
                    <div class="stats-number">{{ data|length }}</div>
                    <div class="text-muted">Candidates</div>
                </div>
            </div>
            <div class="col-4">
                <div class="stats-card">
                    <div class="stats-number">{{ turnout }}%</div>
                    <div class="text-muted">Turnout</div>
                </div>
            </div>
        </div>
        
        <div class="table-responsive">
            <table class="table results-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Candidate</th>
                        <th>Party</th>
                        <th class="text-center">Votes</th>
                        <th class="text-center">%</th>
                    </tr>
                </thead>
                <tbody>
                    {% for candidate in data %}
                    <tr>
                        <td><span class="badge bg-primary">{{ loop.index }}</span></td>
                        <td><strong>{{ candidate.name }}</strong></td>
                        <td><span class="badge bg-light text-dark">{{ candidate.party }}</span></td>
                        <td class="text-center"><strong>{{ candidate.vote_count }}</strong></td>
                        <td class="text-center">
                            <span class="badge bg-success">{{ "%.1f"|format(candidate.percentage) }}%</span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="text-center mt-4">
            <small><a href="/" class="text-decoration-none">← Back to Login</a></small>
        </div>
    </div>
    '''
)

# Admin page
ADMIN_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}Admin Dashboard · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-gear icon-large"></i>
        <h2>Admin Dashboard</h2>
        <p>Manage the voting system</p>
    </div>
    <div class="app-body">
        <div class="row mb-4">
            <div class="col-6">
                <div class="stats-card">
                    <div class="stats-number">{{ total_voters }}</div>
                    <div class="text-muted">Total Voters</div>
                </div>
            </div>
            <div class="col-6">
                <div class="stats-card">
                    <div class="stats-number">{{ voted_count }}</div>
                    <div class="text-muted">Voted</div>
                </div>
            </div>
        </div>

        <h4 class="mb-3">Add New Candidate</h4>
        {% if message %}
        <div class="alert alert-success">
            <i class="bi bi-check-circle me-2"></i>{{ message }}
        </div>
        {% endif %}
        <form method="post" class="mb-5">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label fw-semibold">Candidate Name</label>
                    <input type="text" name="name" class="form-control" placeholder="Enter candidate name" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label fw-semibold">Party Name</label>
                    <input type="text" name="party" class="form-control" placeholder="Enter party name" required>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-plus-circle me-2"></i>Add Candidate
            </button>
        </form>

        <h4 class="mb-3">Voter Records</h4>
        <div class="table-responsive">
            <table class="table admin-table">
                <thead>
                    <tr>
                        <th>Voter ID</th>
                        <th>Name</th>
                        <th>Aadhaar</th>
                        <th>Status</th>
                        <th>Voted For</th>
                    </tr>
                </thead>
                <tbody>
                    {% for voter in voters %}
                    <tr>
                        <td>{{ voter.voter_id }}</td>
                        <td>{{ voter.name }}</td>
                        <td>{{ voter.aadhaar }}</td>
                        <td>
                            {% if voter.has_voted %}
                                <span class="badge badge-success">Voted</span>
                            {% else %}
                                <span class="badge badge-warning">Pending</span>
                            {% endif %}
                        </td>
                        <td>{{ voter.voted_for or '-' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="text-center mt-4">
            <small><a href="/admin-logout" class="text-decoration-none">← Logout Admin</a></small>
        </div>
    </div>
    '''
)

# Admin login page
ADMIN_LOGIN_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}Admin Login · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-shield-lock icon-large"></i>
        <h2>Admin Login</h2>
        <p>Access the administrative dashboard</p>
    </div>
    <div class="app-body">
        {% if error %}
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
        {% endif %}
        <form method="post">
            <div class="mb-3">
                <label class="form-label fw-semibold">Admin Username</label>
                <input type="text" name="username" class="form-control" 
                       placeholder="Enter admin username" required>
            </div>
            <div class="mb-4">
                <label class="form-label fw-semibold">Admin Password</label>
                <input type="password" name="password" class="form-control" 
                       placeholder="Enter admin password" required>
            </div>
            <button type="submit" class="btn btn-primary mb-3">
                <i class="bi bi-shield-check me-2"></i>Login to Admin
            </button>
            <div class="text-center">
                <small><a href="/" class="text-decoration-none">← Back to Voter Portal</a></small>
            </div>
        </form>
    </div>
    '''
)

# Vote success page
VOTE_SUCCESS_PAGE = BASE_TEMPLATE.replace('{% block title %}SecureVote Portal{% endblock %}', '{% block title %}Vote Successful · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
    <div class="app-header">
        <i class="bi bi-check-circle icon-large"></i>
        <h2>Vote Successful!</h2>
        <p>Thank you for participating in the democratic process</p>
    </div>
    <div class="app-body text-center">
        <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem; margin-bottom: 20px;"></i>
        <h4>Your Vote Has Been Cast</h4>
        <p class="text-muted">Your vote has been securely recorded and will be counted</p>
        <div class="d-grid gap-2 mt-4">
            <a href="/result" class="btn btn-primary">View Live Results</a>
            <a href="/" class="btn btn-secondary">Logout</a>
        </div>
    </div>
    '''
)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# In-memory storage for demo
voters_db = {}
candidates_db = [
    (1, 'Narendra Modi', 'BJP'),
    (2, 'Rahul Gandhi', 'Congress'),
    (3, 'Eknath Shinde', 'Shiv Sena'),
    (4, 'naren', 'Independent')
]
votes_db = {}

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        password = request.form['password']
        
        # Check if voter exists
        if aadhaar in voters_db and voters_db[aadhaar]['password'] == password:
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            session['aadhaar'] = aadhaar
            session['otp'] = otp
            session['voter_name'] = voters_db[aadhaar]['name']
            print(f"Generated OTP: {otp} for {aadhaar}")
            return redirect('/verify')
        else:
            return render_template_string(LOGIN_PAGE, error="Invalid credentials. Please check your Aadhaar and password.")
    
    return render_template_string(LOGIN_PAGE)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        stored_otp = session.get('otp')
        
        if entered_otp == stored_otp:
            aadhaar = session.get('aadhaar')
            session['voter_id'] = voters_db[aadhaar]['voter_id']
            return redirect('/vote')
        else:
            return render_template_string(OTP_PAGE, otp=session.get('otp', 'N/A'), error="Invalid OTP. Please try again.")
    
    return render_template_string(OTP_PAGE, otp=session.get('otp', 'N/A'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        aadhaar = request.form['aadhaar']
        mobile = request.form['mobile']
        password = request.form['password']
        
        # Validate inputs
        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return render_template_string(REGISTER_PAGE, error="Aadhaar must be 12 digits.")
        
        if len(mobile) != 10 or not mobile.isdigit():
            return render_template_string(REGISTER_PAGE, error="Mobile must be 10 digits.")
        
        if aadhaar in voters_db:
            return render_template_string(REGISTER_PAGE, error="Aadhaar already registered.")
        
        # Register voter
        voter_id = len(voters_db) + 1
        voters_db[aadhaar] = {
            'voter_id': voter_id,
            'name': name,
            'aadhaar': aadhaar,
            'mobile': mobile,
            'password': password,
            'has_voted': False
        }
        
        return render_template_string(REGISTER_PAGE, success=f"Registration successful! Your Voter ID is {voter_id}. Please login to continue.")
    
    return render_template_string(REGISTER_PAGE)

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    voter_id = session.get('voter_id')
    if not voter_id:
        return redirect('/')
    
    # Check if already voted
    for aadhaar, voter_data in voters_db.items():
        if voter_data['voter_id'] == voter_id and voter_data['has_voted']:
            return render_template_string(VOTE_PAGE, 
                candidates=candidates_db, 
                voter_name=session.get('voter_name'),
                error="You have already voted.")
    
    if request.method == 'POST':
        candidate_id = int(request.form['candidate'])
        
        # Record vote
        votes_db[voter_id] = candidate_id
        
        # Update voter status
        for aadhaar, voter_data in voters_db.items():
            if voter_data['voter_id'] == voter_id:
                voter_data['has_voted'] = True
                # Find candidate name
                for candidate in candidates_db:
                    if candidate[0] == candidate_id:
                        voter_data['voted_for'] = candidate[1]
                        break
                break
        
        return render_template_string(VOTE_SUCCESS_PAGE)
    
    return render_template_string(VOTE_PAGE, candidates=candidates_db, voter_name=session.get('voter_name'))

@app.route('/result')
def result():
    # Calculate results
    results = {}
    for candidate in candidates_db:
        results[candidate[0]] = {
            'name': candidate[1],
            'party': candidate[2],
            'vote_count': 0,
            'percentage': 0
        }
    
    total_votes = len(votes_db)
    for voter_id, candidate_id in votes_db.items():
        results[candidate_id]['vote_count'] += 1
    
    # Calculate percentages
    for candidate_id, result in results.items():
        if total_votes > 0:
            result['percentage'] = (result['vote_count'] / total_votes) * 100
    
    # Sort by vote count
    sorted_results = sorted(results.values(), key=lambda x: x['vote_count'], reverse=True)
    
    # Calculate turnout
    total_voters = len(voters_db)
    turnout = (len(votes_db) / total_voters * 100) if total_voters > 0 else 0
    
    return render_template_string(RESULTS_PAGE, data=sorted_results, total_votes=total_votes, turnout=f"{turnout:.1f}")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Check if admin is logged in
    if not session.get('admin_logged_in'):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                # Prepare voter data for admin dashboard
                voters_list = [{
                    'voter_id': v['voter_id'],
                    'name': v['name'],
                    'aadhaar': v['aadhaar'],
                    'has_voted': v['has_voted'],
                    'voted_for': v.get('voted_for', '-')
                } for v in voters_db.values()]
                
                return render_template_string(ADMIN_PAGE, 
                    total_voters=len(voters_db),
                    voted_count=len(votes_db),
                    voters=voters_list)
            else:
                return render_template_string(ADMIN_LOGIN_PAGE, error="Invalid admin credentials")
        
        return render_template_string(ADMIN_LOGIN_PAGE)
    
    # Admin is logged in, handle admin dashboard
    if request.method == 'POST':
        name = request.form['name']
        party = request.form['party']
        
        # Add new candidate
        candidate_id = max(c[0] for c in candidates_db) + 1
        candidates_db.append((candidate_id, name, party))
        
        # Prepare voter data
        voters_list = [{
            'voter_id': v['voter_id'],
            'name': v['name'],
            'aadhaar': v['aadhaar'],
            'has_voted': v['has_voted'],
            'voted_for': v.get('voted_for', '-')
        } for v in voters_db.values()]
        
        return render_template_string(ADMIN_PAGE, 
            message=f"Candidate '{name}' from '{party}' added successfully!",
            total_voters=len(voters_db),
            voted_count=len(votes_db),
            voters=voters_list)
    
    # Prepare voter data
    voters_list = [{
        'voter_id': v['voter_id'],
        'name': v['name'],
        'aadhaar': v['aadhaar'],
        'has_voted': v['has_voted'],
        'voted_for': v.get('voted_for', '-')
    } for v in voters_db.values()]
    
    return render_template_string(ADMIN_PAGE, 
        total_voters=len(voters_db),
        voted_count=len(votes_db),
        voters=voters_list)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/')

# Export for Vercel
app_handler = app
