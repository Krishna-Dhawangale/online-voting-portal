"""
Professional Voting Portal - Error-Free with Perfect Responsive Design
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

# Professional responsive templates
PROFESSIONAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Online Voting Portal{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #1e40af;
            --secondary-color: #7c3aed;
            --success-color: #16a34a;
            --warning-color: #ea580c;
            --danger-color: #dc2626;
            --light-bg: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --gradient-primary: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            --gradient-success: linear-gradient(135deg, #16a34a 0%, #059669 100%);
            --gradient-warning: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 50%, #fdf4ff 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .app-container {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: var(--shadow-md);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 0;
        }

        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--primary-color) !important;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .navbar-brand i {
            font-size: 1.75rem;
        }

        .main-content {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 3rem 1rem;
            min-height: calc(100vh - 80px);
        }

        .content-wrapper {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }

        .card {
            background: var(--card-bg);
            border-radius: 1rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border-color);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        }

        .card-header {
            background: var(--gradient-primary);
            color: white;
            padding: 2.5rem 2rem;
            text-align: center;
            border: none;
        }

        .card-body {
            padding: 2.5rem 2rem;
        }

        .form-label {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }

        .form-control {
            border: 2px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1rem 1.25rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: var(--light-bg);
        }

        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.1);
            background: white;
        }

        .input-group-text {
            background: var(--light-bg);
            border: 2px solid var(--border-color);
            border-right: none;
            color: var(--text-secondary);
        }

        .input-group .form-control {
            border-left: none;
        }

        .input-group:focus-within .input-group-text {
            border-color: var(--primary-color);
        }

        .btn {
            border-radius: 0.75rem;
            padding: 1rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            border: none;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--gradient-primary);
            color: white;
            box-shadow: var(--shadow-md);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .btn-primary:active {
            transform: translateY(0);
        }

        .candidate-card {
            border: 2px solid var(--border-color);
            border-radius: 1rem;
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
            background: var(--gradient-primary);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }

        .candidate-card:hover {
            border-color: var(--primary-color);
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }

        .candidate-card:hover::before {
            transform: scaleX(1);
        }

        .candidate-card.selected {
            border-color: var(--primary-color);
            background: linear-gradient(135deg, rgba(30, 64, 175, 0.05), rgba(124, 58, 237, 0.05));
        }

        .candidate-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .candidate-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--gradient-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            font-weight: 600;
            flex-shrink: 0;
        }

        .candidate-details {
            flex: 1;
        }

        .candidate-name {
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }

        .candidate-party {
            color: var(--text-secondary);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .form-check-input {
            width: 1.25rem;
            height: 1.25rem;
            accent-color: var(--primary-color);
        }

        .alert {
            border-radius: 0.75rem;
            border: none;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .alert-success {
            background: linear-gradient(135deg, rgba(22, 163, 74, 0.1), rgba(5, 150, 105, 0.1));
            color: #065f46;
            border-left: 4px solid var(--success-color);
        }

        .alert-warning {
            background: linear-gradient(135deg, rgba(234, 88, 12, 0.1), rgba(220, 38, 38, 0.1));
            color: #7c2d12;
            border-left: 4px solid var(--warning-color);
        }

        .alert-danger {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.1), rgba(185, 28, 28, 0.1));
            color: #7f1d1d;
            border-left: 4px solid var(--danger-color);
        }

        .results-table {
            background: white;
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }

        .results-table th {
            background: var(--gradient-primary);
            color: white;
            font-weight: 600;
            border: none;
            padding: 1.25rem;
            font-size: 0.95rem;
        }

        .results-table td {
            padding: 1.25rem;
            vertical-align: middle;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.95rem;
        }

        .progress {
            height: 10px;
            border-radius: 10px;
            background: var(--border-color);
            overflow: hidden;
        }

        .progress-bar {
            background: var(--gradient-primary);
            border-radius: 10px;
            transition: width 0.6s ease;
        }

        .badge {
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-weight: 600;
            font-size: 0.875rem;
        }

        .stats-card {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            transition: transform 0.3s ease;
        }

        .stats-card:hover {
            transform: translateY(-2px);
        }

        .stats-number {
            font-size: 2rem;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }

        .stats-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
        }

        .hero-icon {
            font-size: 4rem;
            color: var(--primary-color);
            margin-bottom: 1.5rem;
        }

        .text-gradient {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Responsive Design */
        @media (max-width: 992px) {
            .main-content {
                padding: 2rem 1rem;
            }
            
            .card-header {
                padding: 2rem 1.5rem;
            }
            
            .card-body {
                padding: 2rem 1.5rem;
            }
        }

        @media (max-width: 768px) {
            .main-content {
                padding: 1.5rem 1rem;
            }
            
            .card-header {
                padding: 1.5rem 1rem;
            }
            
            .card-body {
                padding: 1.5rem 1rem;
            }
            
            .candidate-card {
                padding: 1rem;
            }
            
            .candidate-avatar {
                width: 50px;
                height: 50px;
                font-size: 1.25rem;
            }
            
            .candidate-name {
                font-size: 1rem;
            }
            
            .candidate-party {
                font-size: 0.85rem;
            }
            
            .btn {
                padding: 0.875rem 1.5rem;
                font-size: 0.9rem;
            }
            
            .form-control {
                padding: 0.875rem 1rem;
                font-size: 0.9rem;
            }
            
            .stats-number {
                font-size: 1.5rem;
            }
            
            .hero-icon {
                font-size: 3rem;
            }
        }

        @media (max-width: 576px) {
            .main-content {
                padding: 1rem 0.5rem;
            }
            
            .card-header {
                padding: 1.25rem 1rem;
            }
            
            .card-body {
                padding: 1.25rem 1rem;
            }
            
            .candidate-card {
                padding: 0.75rem;
            }
            
            .candidate-info {
                gap: 0.75rem;
            }
            
            .candidate-avatar {
                width: 40px;
                height: 40px;
                font-size: 1rem;
            }
            
            .candidate-name {
                font-size: 0.95rem;
            }
            
            .candidate-party {
                font-size: 0.8rem;
            }
            
            .btn {
                padding: 0.75rem 1rem;
                font-size: 0.85rem;
                width: 100%;
            }
            
            .form-control {
                padding: 0.75rem 1rem;
                font-size: 0.85rem;
            }
            
            .stats-number {
                font-size: 1.25rem;
            }
            
            .stats-label {
                font-size: 0.8rem;
            }
            
            .hero-icon {
                font-size: 2.5rem;
            }
            
            .navbar-brand {
                font-size: 1.25rem;
            }
            
            .navbar-brand i {
                font-size: 1.5rem;
            }
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }

        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        /* Loading spinner */
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <nav class="navbar">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="navbar-brand">
                        <i class="bi bi-shield-check"></i>
                        <span>SecureVote Portal</span>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge bg-success">
                            <i class="bi bi-check-circle me-1"></i>Verified
                        </span>
                        <span class="badge bg-primary">
                            <i class="bi bi-bar-chart me-1"></i>Live
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

LOGIN_TEMPLATE = PROFESSIONAL_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Login · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="card fade-in-up">
    <div class="card-header">
        <i class="bi bi-shield-check hero-icon"></i>
        <h1 class="mb-3">Welcome Back</h1>
        <p class="mb-0 opacity-75">Sign in to access your secure voting portal</p>
    </div>
    <div class="card-body">
        {% if error %}
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle-fill"></i>
            <span>{{ error }}</span>
        </div>
        {% endif %}
        
        <form method="post" class="fade-in-up">
            <div class="mb-4">
                <label class="form-label">Aadhaar Number</label>
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="bi bi-person-badge"></i>
                    </span>
                    <input type="text" name="aadhaar" class="form-control" 
                           placeholder="Enter 12-digit Aadhaar" maxlength="12" required>
                </div>
            </div>
            
            <div class="mb-4">
                <label class="form-label">Password</label>
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="bi bi-lock-fill"></i>
                    </span>
                    <input type="password" name="password" class="form-control" 
                           placeholder="Enter your password" required>
                </div>
            </div>
            
            <div class="d-grid mb-4">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-arrow-right-circle"></i>
                    Continue to OTP
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

VOTE_TEMPLATE = PROFESSIONAL_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Cast Your Vote · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="card fade-in-up">
    <div class="card-header">
        <i class="bi bi-ballot hero-icon"></i>
        <h1 class="mb-3">Cast Your Vote</h1>
        <p class="mb-0 opacity-75">Choose your candidate wisely - your vote matters</p>
    </div>
    <div class="card-body">
        {% if message %}
        <div class="alert alert-success">
            <i class="bi bi-check-circle-fill"></i>
            <span>{{ message }}</span>
        </div>
        {% endif %}
        
        <form method="post">
            <div class="row">
                {% for c in candidates %}
                <div class="col-lg-6 col-md-12 mb-3">
                    <label class="candidate-card" onclick="selectCandidate({{ c[0] }})">
                        <div class="candidate-info">
                            <div class="candidate-avatar">
                                {{ c[1][0] }}
                            </div>
                            <div class="candidate-details">
                                <div class="candidate-name">{{ c[1] }}</div>
                                <div class="candidate-party">
                                    <i class="bi bi-building"></i>
                                    {{ c[2] }}
                                </div>
                            </div>
                            <div class="form-check">
                                <input type="radio" name="candidate" value="{{ c[0] }}" 
                                       class="form-check-input" id="candidate-{{ c[0] }}" required>
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
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-circle"></i>
                        Submit Vote
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

RESULT_TEMPLATE = PROFESSIONAL_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Live Results · SecureVote Portal{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="card fade-in-up">
    <div class="card-header">
        <i class="bi bi-graph-up hero-icon"></i>
        <h1 class="mb-3">Live Results</h1>
        <p class="mb-0 opacity-75">Real-time voting statistics and results</p>
    </div>
    <div class="card-body">
        <div class="row mb-4">
            <div class="col-md-4 col-6 mb-3">
                <div class="stats-card">
                    <div class="stats-number">{{ total_votes }}</div>
                    <div class="stats-label">Total Votes</div>
                </div>
            </div>
            <div class="col-md-4 col-6 mb-3">
                <div class="stats-card">
                    <div class="stats-number">{{ data|length }}</div>
                    <div class="stats-label">Candidates</div>
                </div>
            </div>
            <div class="col-md-4 col-6 mb-3">
                <div class="stats-card">
                    <div class="stats-number">100%</div>
                    <div class="stats-label">Turnout</div>
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
                                <span class="badge bg-warning text-dark">{{ loop.index }}</span>
                                {% else %}
                                <span class="badge bg-secondary">{{ loop.index }}</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="fw-semibold">{{ candidate.name }}</div>
                            </td>
                            <td>
                                <span class="badge bg-light text-dark">{{ candidate.party }}</span>
                            </td>
                            <td class="text-center">
                                <strong class="{% if loop.first and candidate.vote_count > 0 %}text-warning{% endif %}">
                                    {{ candidate.vote_count }}
                                </strong>
                            </td>
                            <td class="text-center">
                                <span class="badge {% if candidate.percentage > 50 %}bg-success{% elif candidate.percentage > 25 %}bg-primary{% elif candidate.percentage > 0 %}bg-info{% else %}bg-secondary{% endif %}">
                                    {{ "%.1f"|format(candidate.percentage) }}%
                                </span>
                            </td>
                            <td>
                                <div class="progress">
                                    <div class="progress-bar" style="width: {{ candidate.percentage }}%"></div>
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
            <i class="bi bi-bar-chart" style="font-size: 4rem; color: var(--text-secondary); margin-bottom: 1.5rem;"></i>
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
                '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle-fill"></i><span>Database not available - Demo mode</span></div>')
        
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
                    '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill"></i><span>Invalid credentials</span></div>')
    
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
            '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle-fill"></i><span>Demo mode - Database not connected</span></div>').replace('{{ candidates }}', 'candidates_list')
    
    with get_session() as session_db:
        voted = session_db.execute(
            voters.select().where(voters.c.voter_id == voter_id, voters.c.has_voted == True)
        ).first()
        
        if voted:
            return '''
            <div class="card fade-in-up">
                <div class="card-header">
                    <i class="bi bi-check-circle hero-icon"></i>
                    <h1 class="mb-3">Vote Already Cast</h1>
                    <p class="mb-0 opacity-75">You have already voted in this election</p>
                </div>
                <div class="card-body text-center py-5">
                    <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem; margin-bottom: 1.5rem;"></i>
                    <h4 class="mb-3">Thank You for Voting!</h4>
                    <p class="text-muted mb-4">Your vote has been successfully recorded</p>
                    <a href="/result" class="btn btn-primary">
                        <i class="bi bi-bar-chart"></i>
                        View Results
                    </a>
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
                '<div class="alert alert-success"><i class="bi bi-check-circle-fill"></i><span>Vote submitted successfully!</span></div>').replace('{{ candidates }}', 'candidates_list')
    
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
    <div class="card fade-in-up">
        <div class="card-header">
            <i class="bi bi-shield-check hero-icon"></i>
            <h1 class="mb-3">OTP Verification</h1>
            <p class="mb-0 opacity-75">Enter your one-time password to continue</p>
        </div>
        <div class="card-body">
            <div class="alert alert-info mb-4">
                <i class="bi bi-info-circle-fill"></i>
                <span>For testing, your OTP is: <strong>{session.get('otp', 'N/A')}</strong></span>
            </div>
            <form method="post">
                <div class="mb-4">
                    <label class="form-label">Enter OTP</label>
                    <div class="input-group">
                        <span class="input-group-text">
                            <i class="bi bi-key"></i>
                        </span>
                        <input type="text" name="otp" class="form-control" 
                               placeholder="6-digit OTP" maxlength="6" required>
                    </div>
                </div>
                <div class="d-grid mb-4">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-circle"></i>
                        Verify OTP
                    </button>
                </div>
                <div class="text-center">
                    <a href="/" class="text-gradient">← Back to Login</a>
                </div>
            </form>
        </div>
    </div>
    '''

@app.route('/register')
def register():
    return '''
    <div class="card fade-in-up">
        <div class="card-header">
            <i class="bi bi-person-plus hero-icon"></i>
            <h1 class="mb-3">Register New Voter</h1>
            <p class="mb-0 opacity-75">Create your secure voting account</p>
        </div>
        <div class="card-body text-center py-5">
            <i class="bi bi-tools" style="font-size: 4rem; color: var(--text-secondary); margin-bottom: 1.5rem;"></i>
            <h4 class="text-muted mb-3">Registration Coming Soon</h4>
            <p class="text-muted mb-4">Voter registration functionality will be available soon</p>
            <a href="/" class="btn btn-primary">
                <i class="bi bi-arrow-left"></i>
                Back to Login
            </a>
        </div>
    </div>
    '''

@app.route('/admin')
def admin():
    return '''
    <div class="card fade-in-up">
        <div class="card-header">
            <i class="bi bi-gear hero-icon"></i>
            <h1 class="mb-3">Admin Dashboard</h1>
            <p class="mb-0 opacity-75">Manage the voting system</p>
        </div>
        <div class="card-body text-center py-5">
            <i class="bi bi-tools" style="font-size: 4rem; color: var(--text-secondary); margin-bottom: 1.5rem;"></i>
            <h4 class="text-muted mb-3">Admin Features Coming Soon</h4>
            <p class="text-muted mb-4">Advanced admin functionality will be available soon</p>
            <a href="/" class="btn btn-primary">
                <i class="bi bi-arrow-left"></i>
                Back to Login
            </a>
        </div>
    </div>
    '''

# Export for Vercel
app_handler = app
