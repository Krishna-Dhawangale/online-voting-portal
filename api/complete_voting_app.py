"""
Complete Standalone Voting App with All Styles Embedded
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

# Complete standalone templates with all styles
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Online Voting Portal{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body {
            font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at top left, #e0f2fe 0, transparent 55%),
                        radial-gradient(circle at bottom right, #fef3c7 0, transparent 55%),
                        #0f172a;
            min-height: 100vh;
            color: #0f172a;
        }

        .app-shell {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .app-navbar {
            background: rgba(15, 23, 42, 0.96);
            backdrop-filter: blur(18px);
        }

        .app-main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem 3rem;
        }

        @media (min-width: 992px) {
            .app-main {
                padding-top: 3rem;
            }
        }

        .auth-layout,
        .content-card {
            width: 100%;
            max-width: 480px;
        }

        @media (min-width: 768px) {
            .content-card {
                max-width: 680px;
            }
        }

        @media (min-width: 992px) {
            .content-card {
                max-width: 880px;
            }
        }

        .card-surface {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 1rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .card-accent {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
        }

        .field-label {
            font-weight: 500;
            font-size: 0.875rem;
            color: #374151;
            margin-bottom: 0.5rem;
        }

        .subtle-link {
            font-size: 0.875rem;
            color: #6b7280;
        }

        .subtle-link a {
            color: #3b82f6;
            text-decoration: none;
            font-weight: 500;
        }

        .subtle-link a:hover {
            text-decoration: underline;
        }

        .candidate-card {
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }

        .candidate-card:hover {
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .candidate-card input[type="radio"]:checked + .form-check-label {
            color: #3b82f6;
        }

        .results-badge {
            font-size: 0.75rem;
            border-radius: 9999px;
        }

        .progress {
            background-color: #e5e7eb;
        }

        .progress-bar {
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="app-shell">
        <nav class="app-navbar navbar navbar-dark">
            <div class="container">
                <span class="navbar-brand mb-0 h1">
                    <i class="bi bi-shield-check me-2"></i>
                    <span class="badge bg-success bg-opacity-75 text-white">Online Voting Portal</span>
                </span>
            </div>
        </nav>

        <main class="app-main">
            {% block content %}{% endblock %}
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Login · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="auth-layout mx-auto">
  <div class="row g-0 card-surface">
    <div class="col-lg-5 card-accent p-4 p-lg-5 d-flex flex-column justify-content-between">
      <div>
        <span class="badge bg-sky-500 bg-opacity-75 text-white text-uppercase mb-3 badge-pill">
          Secure Access
        </span>
        <h1 class="h3 fw-semibold mb-2">Welcome back, voter</h1>
        <p class="mb-0 text-light opacity-75 small">
          Sign in with your Aadhaar and password to continue to OTP verification and cast your vote.
        </p>
      </div>
      <div class="mt-4 small text-light opacity-75">
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-success bg-opacity-75 badge-pill">End-to-end secured</span>
          <span>One vote per verified citizen</span>
        </div>
      </div>
    </div>
    <div class="col-lg-7 p-4 p-lg-5 bg-white">
      <div class="mb-3">
        <h2 class="h4 fw-semibold mb-1">Login to voting portal</h2>
        <p class="text-muted mb-0 small">
          Enter your registered credentials to receive a one-time password (OTP).
        </p>
      </div>
      {% if error %}
      <div class="alert alert-danger">{{ error }}</div>
      {% endif %}
      <form method="post" novalidate>
        <div class="mb-3">
          <label class="field-label mb-1">Aadhaar number</label>
          <input
            type="text"
            name="aadhaar"
            class="form-control form-control-lg"
            placeholder="12-digit Aadhaar"
            minlength="12"
            maxlength="12"
            required
          >
        </div>
        <div class="mb-3">
          <label class="field-label mb-1">Password</label>
          <input
            type="password"
            name="password"
            class="form-control form-control-lg"
            placeholder="Your secure password"
            required
          >
        </div>
        <div class="d-flex justify-content-between align-items-center mb-4 small text-muted">
          <span>Do not share your credentials with anyone.</span>
        </div>
        <div class="d-grid mb-3">
          <button type="submit" class="btn btn-primary btn-lg">
            Continue to OTP verification
          </button>
        </div>
        <p class="subtle-link text-center mb-0">
          New voter?
          <a href="/register">Create your voting account</a>
        </p>
      </form>
    </div>
  </div>
</div>
'''
)

VOTE_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Cast Your Vote · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="content-card mx-auto">
  <div class="card-surface p-4 p-lg-5 bg-white">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 align-items-start mb-4">
      <div>
        <h1 class="h4 fw-semibold mb-1">Select your candidate</h1>
        <p class="text-muted small mb-0">
          Review the candidates carefully and choose one option. Your vote will be recorded securely and counted once.
        </p>
      </div>
      <div class="text-end">
        <span class="badge bg-success bg-opacity-75 text-white results-badge px-3 py-2 small">
          Verified voter session
        </span>
      </div>
    </div>

    {% if message %}
    <div class="alert alert-info">{{ message }}</div>
    {% endif %}

    <form method="post" novalidate>
      <div class="row g-3 mb-4">
        {% for c in candidates %}
        <div class="col-12 col-md-6">
          <label class="border rounded-4 p-3 h-100 w-100 d-flex flex-column justify-content-between candidate-card">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div>
                <div class="form-check mb-1">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="candidate"
                    value="{{ c[0] }}"
                    id="candidate-{{ c[0] }}"
                    required
                  >
                  <label class="form-check-label fw-semibold" for="candidate-{{ c[0] }}">
                    {{ c[1] }}
                  </label>
                </div>
                <div class="text-muted small">
                  Party: {{ c[2] }}
                </div>
              </div>
            </div>
          </label>
        </div>
        {% endfor %}
      </div>

      <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center gap-3">
        <p class="subtle-link mb-0">
          Once submitted, your vote cannot be changed.
        </p>
        <button type="submit" class="btn btn-primary btn-lg px-4">
          Submit my vote
        </button>
      </div>
    </form>
  </div>
</div>
'''
)

RESULT_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Live Results · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="content-card mx-auto">
  <div class="card-surface p-4 p-lg-5 bg-white">
    <div class="d-flex flex-column flex-lg-row justify-content-between align-items-start gap-3 mb-4">
      <div>
        <h1 class="h4 fw-semibold mb-1">Election Results</h1>
        <p class="text-muted small mb-0">
          Live voting statistics by candidate and party. Refresh for latest updates.
        </p>
      </div>
      <div class="text-end">
        <div class="badge bg-primary bg-opacity-80 text-white results-badge px-3 py-2 small mb-2">
          Total Votes: <strong>{{ total_votes }}</strong>
        </div>
        <div class="badge bg-success bg-opacity-75 text-white results-badge px-3 py-2 small">
          Live Results
        </div>
      </div>
    </div>

    {% if data %}
    <div class="table-responsive">
      <table class="table align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th scope="col">Rank</th>
            <th scope="col">Candidate</th>
            <th scope="col">Party</th>
            <th scope="col" class="text-center">Votes</th>
            <th scope="col" class="text-center">Percentage</th>
            <th scope="col">Visual</th>
          </tr>
        </thead>
        <tbody>
          {% for candidate in data %}
          <tr class="{% if loop.first and candidate.vote_count > 0 %}table-warning{% endif %}">
            <td>
              {% if candidate.vote_count > 0 %}
                <span class="badge bg-{{ 'warning' if loop.first else 'secondary' }} rounded-pill">
                  {{ loop.index }}
                </span>
              {% else %}
                <span class="text-muted">{{ loop.index }}</span>
              {% endif %}
            </td>
            <td>
              <div class="fw-semibold">{{ candidate.name }}</div>
            </td>
            <td>
              <span class="badge bg-light text-dark">{{ candidate.party }}</span>
            </td>
            <td class="text-center">
              <strong class="{{ 'text-warning' if loop.first and candidate.vote_count > 0 else '' }}">
                {{ candidate.vote_count }}
              </strong>
            </td>
            <td class="text-center">
              <span class="badge bg-{{ 'success' if candidate.percentage > 50 else 'primary' if candidate.percentage > 25 else 'secondary' if candidate.percentage > 0 else 'light' }} rounded-pill">
                {{ candidate.percentage }}%
              </span>
            </td>
            <td>
              <div class="progress" style="height: 20px;">
                <div class="progress-bar bg-{{ 'warning' if loop.first and candidate.vote_count > 0 else 'primary' }}" 
                     role="progressbar" 
                     style="width: {{ candidate.percentage }}%"
                     aria-valuenow="{{ candidate.percentage }}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                  {% if candidate.percentage > 5 %}{{ candidate.percentage }}%{% endif %}
                </div>
              </div>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <div class="text-center py-5">
      <i class="bi bi-bar-chart text-muted" style="font-size: 3rem;"></i>
      <h5 class="mt-3 text-muted">No votes recorded yet</h5>
      <p class="text-muted">Voting hasn't started or no votes have been cast yet.</p>
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
            return LOGIN_TEMPLATE.replace('{% if error %}{{ error }}{% endif %}', '<div class="alert alert-warning">Database not available - Demo mode</div>')
        
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
                return LOGIN_TEMPLATE.replace('{% if error %}{{ error }}{% endif %}', '<div class="alert alert-danger">Invalid credentials</div>')
    
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
        return VOTE_TEMPLATE.replace('{% if message %}{{ message }}{% endif %}', '<div class="alert alert-warning">Demo mode - Database not connected</div>').replace('{{ candidates }}', 'candidates_list')
    
    with get_session() as session_db:
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
            return VOTE_TEMPLATE.replace('{% if message %}{{ message }}{% endif %}', '<div class="alert alert-success">Vote submitted successfully!</div>').replace('{{ candidates }}', 'candidates_list')
    
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
    <div style="max-width: 400px; margin: 100px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2>OTP Verification</h2>
        <p>Your OTP is: <strong>{session.get('otp', 'N/A')}</strong></p>
        <form method="post">
            <input type="text" name="otp" placeholder="Enter OTP" required style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;">
            <button type="submit" style="width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Verify</button>
        </form>
        <a href="/" style="display: block; text-align: center; margin-top: 10px; color: #007bff;">Back to Login</a>
    </div>
    '''

@app.route('/register')
def register():
    return '''
    <div style="max-width: 400px; margin: 100px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2>Register New Voter</h2>
        <p>Registration functionality coming soon!</p>
        <a href="/" style="display: block; text-align: center; margin-top: 10px; color: #007bff;">Back to Login</a>
    </div>
    '''

@app.route('/admin')
def admin():
    return '''
    <div style="max-width: 400px; margin: 100px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2>Admin Dashboard</h2>
        <p>Admin functionality coming soon!</p>
        <a href="/" style="display: block; text-align: center; margin-top: 10px; color: #007bff;">Back to Login</a>
    </div>
    '''

# Export for Vercel
app_handler = app
