"""
Responsive Voting App with Optimized UI for Desktop and Mobile
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

# Responsive templates with optimized layout
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Online Voting Portal{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #2d3748;
            line-height: 1.6;
        }

        .app-container {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .navbar-custom {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            color: #4a5568 !important;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .main-content {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem;
            min-height: calc(100vh - 80px);
        }

        .content-wrapper {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }

        .card-custom {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .card-header-custom {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        .card-body-custom {
            padding: 2rem;
        }

        .form-control-custom {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f8fafc;
        }

        .form-control-custom:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: white;
        }

        .btn-custom {
            border-radius: 12px;
            padding: 1rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-primary-custom {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .btn-primary-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .candidate-card {
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            cursor: pointer;
            background: white;
            position: relative;
            overflow: hidden;
        }

        .candidate-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }

        .candidate-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .candidate-card:hover::before {
            transform: scaleX(1);
        }

        .candidate-card.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        }

        .candidate-name {
            font-weight: 600;
            font-size: 1.1rem;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }

        .candidate-party {
            color: #718096;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .radio-custom {
            width: 20px;
            height: 20px;
            accent-color: #667eea;
        }

        .alert-custom {
            border-radius: 12px;
            border: none;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
        }

        .alert-success-custom {
            background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(56, 161, 105, 0.1));
            color: #22543d;
            border-left: 4px solid #48bb78;
        }

        .alert-warning-custom {
            background: linear-gradient(135deg, rgba(237, 137, 54, 0.1), rgba(221, 107, 32, 0.1));
            color: #744210;
            border-left: 4px solid #ed8936;
        }

        .alert-danger-custom {
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.1), rgba(229, 62, 62, 0.1));
            color: #742a2a;
            border-left: 4px solid #f56565;
        }

        .results-table {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        }

        .results-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            border: none;
            padding: 1rem;
        }

        .results-table td {
            padding: 1rem;
            vertical-align: middle;
            border-bottom: 1px solid #e2e8f0;
        }

        .progress-custom {
            height: 8px;
            border-radius: 10px;
            background: #e2e8f0;
            overflow: hidden;
        }

        .progress-bar-custom {
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
            transition: width 0.3s ease;
        }

        .badge-custom {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.875rem;
        }

        .text-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Mobile Responsive */
        @media (max-width: 768px) {
            .main-content {
                padding: 1rem;
            }

            .card-body-custom {
                padding: 1.5rem;
            }

            .card-header-custom {
                padding: 1.5rem;
            }

            .candidate-card {
                padding: 1rem;
            }

            .btn-custom {
                padding: 0.875rem 1.5rem;
                font-size: 0.9rem;
            }

            .form-control-custom {
                padding: 0.875rem;
                font-size: 0.9rem;
            }

            h1 {
                font-size: 1.5rem;
            }

            h2 {
                font-size: 1.25rem;
            }

            .navbar-brand {
                font-size: 1.25rem;
            }
        }

        @media (max-width: 576px) {
            .main-content {
                padding: 0.5rem;
            }

            .card-body-custom {
                padding: 1rem;
            }

            .card-header-custom {
                padding: 1rem;
            }

            .candidate-card {
                padding: 0.75rem;
            }

            .btn-custom {
                padding: 0.75rem 1rem;
                font-size: 0.875rem;
            }

            .form-control-custom {
                padding: 0.75rem;
                font-size: 0.875rem;
            }

            h1 {
                font-size: 1.25rem;
            }

            h2 {
                font-size: 1.1rem;
            }

            .navbar-brand {
                font-size: 1rem;
            }
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }

        @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }

        .slide-in {
            animation: slideIn 0.3s ease-out;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <nav class="navbar-custom">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="navbar-brand">
                        <i class="bi bi-shield-check text-gradient"></i>
                        <span class="text-gradient">Online Voting Portal</span>
                    </div>
                    <div class="d-flex align-items-center gap-3">
                        <span class="badge-custom bg-success">
                            <i class="bi bi-check-circle me-1"></i>Secure
                        </span>
                        <span class="badge-custom bg-primary">
                            <i class="bi bi-database me-1"></i>Live
                        </span>
                    </div>
                </div>
            </div>
        </nav>

        <main class="main-content">
            <div class="content-wrapper">
                {% block content %}{% endblock %}
            </div>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Login · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="card-custom fade-in">
    <div class="card-header-custom">
        <div class="text-center">
            <i class="bi bi-shield-check" style="font-size: 3rem; margin-bottom: 1rem;"></i>
            <h1 class="mb-2">Welcome Back</h1>
            <p class="mb-0 opacity-75">Sign in to access your voting portal</p>
        </div>
    </div>
    <div class="card-body-custom">
        {% if error %}
        <div class="alert alert-danger-custom alert-custom">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
        {% endif %}
        
        <form method="post" class="fade-in">
            <div class="mb-4">
                <label class="form-label fw-semibold">Aadhaar Number</label>
                <div class="input-group">
                    <span class="input-group-text bg-light border-0">
                        <i class="bi bi-person-badge"></i>
                    </span>
                    <input type="text" name="aadhaar" class="form-control form-control-custom border-start-0" 
                           placeholder="Enter 12-digit Aadhaar" maxlength="12" required>
                </div>
            </div>
            
            <div class="mb-4">
                <label class="form-label fw-semibold">Password</label>
                <div class="input-group">
                    <span class="input-group-text bg-light border-0">
                        <i class="bi bi-lock"></i>
                    </span>
                    <input type="password" name="password" class="form-control form-control-custom border-start-0" 
                           placeholder="Enter your password" required>
                </div>
            </div>
            
            <div class="d-grid mb-4">
                <button type="submit" class="btn btn-primary-custom btn-custom">
                    <i class="bi bi-arrow-right-circle me-2"></i>Continue to OTP
                </button>
            </div>
            
            <div class="text-center">
                <p class="mb-0">
                    <small class="text-muted">New voter? </small>
                    <a href="/register" class="text-gradient fw-semibold">Create Account</a>
                </p>
            </div>
        </form>
    </div>
</div>
'''
)

VOTE_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Cast Your Vote · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="card-custom fade-in">
    <div class="card-header-custom">
        <div class="text-center">
            <i class="bi bi-ballot" style="font-size: 3rem; margin-bottom: 1rem;"></i>
            <h1 class="mb-2">Cast Your Vote</h1>
            <p class="mb-0 opacity-75">Choose your candidate wisely</p>
        </div>
    </div>
    <div class="card-body-custom">
        {% if message %}
        <div class="alert alert-success-custom alert-custom">
            <i class="bi bi-check-circle me-2"></i>{{ message }}
        </div>
        {% endif %}
        
        <form method="post">
            <div class="row">
                {% for c in candidates %}
                <div class="col-lg-6 col-md-12 mb-3">
                    <label class="candidate-card" onclick="selectCandidate({{ c[0] }})">
                        <div class="d-flex align-items-center">
                            <input type="radio" name="candidate" value="{{ c[0] }}" 
                                   class="radio-custom me-3" id="candidate-{{ c[0] }}" required>
                            <div class="flex-grow-1">
                                <div class="candidate-name">{{ c[1] }}</div>
                                <div class="candidate-party">
                                    <i class="bi bi-building me-1"></i>{{ c[2] }}
                                </div>
                            </div>
                            <div class="text-end">
                                <i class="bi bi-person-circle" style="font-size: 2rem; color: #667eea;"></i>
                            </div>
                        </div>
                    </label>
                </div>
                {% endfor %}
            </div>
            
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-center gap-3 mt-4">
                <div class="text-muted">
                    <small><i class="bi bi-info-circle me-1"></i>Once submitted, your vote cannot be changed</small>
                </div>
                <div class="d-grid">
                    <button type="submit" class="btn btn-primary-custom btn-custom">
                        <i class="bi bi-check-circle me-2"></i>Submit Vote
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>

<script>
function selectCandidate(id) {
    document.getElementById('candidate-' + id).checked = true;
    document.querySelectorAll('.candidate-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}
</script>
'''
)

RESULT_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Live Results · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="card-custom fade-in">
    <div class="card-header-custom">
        <div class="text-center">
            <i class="bi bi-graph-up" style="font-size: 3rem; margin-bottom: 1rem;"></i>
            <h1 class="mb-2">Live Results</h1>
            <p class="mb-0 opacity-75">Real-time voting statistics</p>
        </div>
    </div>
    <div class="card-body-custom">
        <div class="row mb-4">
            <div class="col-md-4 col-6 mb-3">
                <div class="text-center p-3 bg-light rounded-3">
                    <div class="h4 text-gradient mb-1">{{ total_votes }}</div>
                    <div class="small text-muted">Total Votes</div>
                </div>
            </div>
            <div class="col-md-4 col-6 mb-3">
                <div class="text-center p-3 bg-light rounded-3">
                    <div class="h4 text-gradient mb-1">{{ data|length }}</div>
                    <div class="small text-muted">Candidates</div>
                </div>
            </div>
            <div class="col-md-4 col-6 mb-3">
                <div class="text-center p-3 bg-light rounded-3">
                    <div class="h4 text-gradient mb-1">100%</div>
                    <div class="small text-muted">Turnout</div>
                </div>
            </div>
        </div>

        {% if data %}
        <div class="results-table">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr>
                            <th scope="col">Rank</th>
                            <th scope="col">Candidate</th>
                            <th scope="col">Party</th>
                            <th scope="col" class="text-center">Votes</th>
                            <th scope="col" class="text-center">Percentage</th>
                            <th scope="col">Progress</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for candidate in data %}
                        <tr class="{% if loop.first and candidate.vote_count > 0 %}table-warning{% endif %}">
                            <td>
                                {% if candidate.vote_count > 0 %}
                                <span class="badge-custom bg-warning text-dark">{{ loop.index }}</span>
                                {% else %}
                                <span class="badge-custom bg-secondary">{{ loop.index }}</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="fw-semibold">{{ candidate.name }}</div>
                            </td>
                            <td>
                                <span class="badge-custom bg-light text-dark">{{ candidate.party }}</span>
                            </td>
                            <td class="text-center">
                                <strong class="{% if loop.first and candidate.vote_count > 0 %}text-warning{% endif %}">
                                    {{ candidate.vote_count }}
                                </strong>
                            </td>
                            <td class="text-center">
                                <span class="badge-custom {% if candidate.percentage > 50 %}bg-success{% elif candidate.percentage > 25 %}bg-primary{% elif candidate.percentage > 0 %}bg-info{% else %}bg-secondary{% endif %}">
                                    {{ "%.1f"|format(candidate.percentage) }}%
                                </span>
                            </td>
                            <td>
                                <div class="progress-custom">
                                    <div class="progress-bar-custom" style="width: {{ candidate.percentage }}%"></div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% else %}
        <div class="text-center py-5">
            <i class="bi bi-bar-chart" style="font-size: 4rem; color: #cbd5e0; margin-bottom: 1rem;"></i>
            <h4 class="text-muted">No votes recorded yet</h4>
            <p class="text-muted">Voting hasn't started or no votes have been cast</p>
        </div>
        {% endif %}
    </div>
</div>
'''
)

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not DB_AVAILABLE:
            return LOGIN_TEMPLATE.replace('{% if error %}{{ error }}{% endif %}', 
                '<div class="alert alert-warning-custom alert-custom"><i class="bi bi-exclamation-triangle me-2"></i>Database not available - Demo mode</div>')
        
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
                return LOGIN_TEMPLATE.replace('{% if error %}{{ error }}{% endif %}', 
                    '<div class="alert alert-danger-custom alert-custom"><i class="bi bi-exclamation-triangle me-2"></i>Invalid credentials</div>')
    
    return LOGIN_TEMPLATE.replace('{% if error %}{{ error }}{% endif %}', '')

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
        return VOTE_TEMPLATE.replace('{% if message %}{{ message }}{% endif %}', 
            '<div class="alert alert-warning-custom alert-custom"><i class="bi bi-exclamation-triangle me-2"></i>Demo mode - Database not connected</div>').replace('{{ candidates }}', 'candidates_list')
    
    with get_session() as session_db:
        voted = session_db.execute(
            voters.select().where(voters.c.voter_id == voter_id, voters.c.has_voted == True)
        ).first()
        
        if voted:
            return '''
            <div class="card-custom fade-in">
                <div class="card-body-custom text-center py-5">
                    <i class="bi bi-check-circle text-success" style="font-size: 4rem; margin-bottom: 1rem;"></i>
                    <h3 class="mb-3">Vote Already Cast</h3>
                    <p class="text-muted mb-4">You have already voted in this election</p>
                    <a href="/result" class="btn btn-primary-custom btn-custom">View Results</a>
                </div>
            </div>
            '''
        
        candidates_list = list(session_db.execute(candidates.select()).all())
        
        if request.method == 'POST':
            candidate_id = int(request.form['candidate'])
            session_db.execute(votes.insert().values(voter_id=voter_id, candidate_id=candidate_id))
            session_db.execute(voters.update().where(voters.c.voter_id == voter_id).values(has_voted=True))
            session_db.commit()
            return VOTE_TEMPLATE.replace('{% if message %}{{ message }}{% endif %}', 
                '<div class="alert alert-success-custom alert-custom"><i class="bi bi-check-circle me-2"></i>Vote submitted successfully!</div>').replace('{{ candidates }}', 'candidates_list')
    
    return VOTE_TEMPLATE.replace('{% if message %}{{ message }}{% endif %}', '').replace('{{ candidates }}', 'candidates_list')

@app.route('/result')
def result():
    if not DB_AVAILABLE:
        data = [
            {'candidate_id': 1, 'name': 'Narendra Modi', 'party': 'BJP', 'vote_count': 1, 'percentage': 100.0},
            {'candidate_id': 2, 'name': 'Rahul Gandhi', 'party': 'Congress', 'vote_count': 0, 'percentage': 0.0},
            {'candidate_id': 3, 'name': 'Eknath Shinde', 'party': 'Shiv Sena', 'vote_count': 0, 'percentage': 0.0},
            {'candidate_id': 4, 'name': 'naren', 'party': 'Independent', 'vote_count': 0, 'percentage': 0.0}
        ]
        return RESULT_TEMPLATE.replace('{{ data }}', 'data').replace('{{ total_votes }}', '1')
    
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
    
    return RESULT_TEMPLATE.replace('{{ data }}', 'data').replace('{{ total_votes }}', str(total_votes))

@app.route('/verify')
def verify():
    return f'''
    <div class="card-custom fade-in">
        <div class="card-header-custom">
            <div class="text-center">
                <i class="bi bi-shield-check" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h1 class="mb-2">OTP Verification</h1>
                <p class="mb-0 opacity-75">Enter your one-time password</p>
            </div>
        </div>
        <div class="card-body-custom">
            <div class="alert alert-info-custom alert-custom mb-4">
                <i class="bi bi-info-circle me-2"></i>
                For testing, your OTP is: <strong>{session.get('otp', 'N/A')}</strong>
            </div>
            <form method="post">
                <div class="mb-4">
                    <label class="form-label fw-semibold">Enter OTP</label>
                    <div class="input-group">
                        <span class="input-group-text bg-light border-0">
                            <i class="bi bi-key"></i>
                        </span>
                        <input type="text" name="otp" class="form-control form-control-custom border-start-0" 
                               placeholder="6-digit OTP" maxlength="6" required>
                    </div>
                </div>
                <div class="d-grid">
                    <button type="submit" class="btn btn-primary-custom btn-custom">
                        <i class="bi bi-check-circle me-2"></i>Verify OTP
                    </button>
                </div>
            </form>
            <div class="text-center mt-3">
                <a href="/" class="text-gradient">← Back to Login</a>
            </div>
        </div>
    </div>
    '''

@app.route('/register')
def register():
    return '''
    <div class="card-custom fade-in">
        <div class="card-header-custom">
            <div class="text-center">
                <i class="bi bi-person-plus" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h1 class="mb-2">Register New Voter</h1>
                <p class="mb-0 opacity-75">Create your voting account</p>
            </div>
        </div>
        <div class="card-body-custom text-center py-5">
            <i class="bi bi-tools text-muted" style="font-size: 4rem; margin-bottom: 1rem;"></i>
            <h4 class="text-muted mb-3">Registration Coming Soon</h4>
            <p class="text-muted mb-4">Voter registration functionality will be available soon</p>
            <a href="/" class="btn btn-primary-custom btn-custom">Back to Login</a>
        </div>
    </div>
    '''

@app.route('/admin')
def admin():
    return '''
    <div class="card-custom fade-in">
        <div class="card-header-custom">
            <div class="text-center">
                <i class="bi bi-gear" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h1 class="mb-2">Admin Dashboard</h1>
                <p class="mb-0 opacity-75">Manage voting system</p>
            </div>
        </div>
        <div class="card-body-custom text-center py-5">
            <i class="bi bi-tools text-muted" style="font-size: 4rem; margin-bottom: 1rem;"></i>
            <h4 class="text-muted mb-3">Admin Features Coming Soon</h4>
            <p class="text-muted mb-4">Advanced admin functionality will be available soon</p>
            <a href="/" class="btn btn-primary-custom btn-custom">Back to Login</a>
        </div>
    </div>
    '''

# Export for Vercel
app_handler = app
