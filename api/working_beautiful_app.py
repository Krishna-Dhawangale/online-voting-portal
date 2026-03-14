"""
Working Beautiful Voting App with Embedded Templates for Vercel
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

# Beautiful embedded templates
LOGIN_TEMPLATE = '''
{% extends "base.html" %}

{% block title %}Login · Online Voting{% endblock %}

{% block content %}
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
{% endblock %}
'''

VOTE_TEMPLATE = '''
{% extends "base.html" %}

{% block title %}Cast Your Vote · Online Voting{% endblock %}

{% block content %}
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
{% endblock %}
'''

RESULT_TEMPLATE = '''
{% extends "base.html" %}

{% block title %}Live Results · Online Voting{% endblock %}

{% block content %}
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
    <!-- Detailed Results Table -->
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
{% endblock %}
'''

# Routes with embedded templates
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not DB_AVAILABLE:
            return from_string(LOGIN_TEMPLATE).render(error="Database not available")
        
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
                return from_string(LOGIN_TEMPLATE).render(error="Invalid credentials")
    
    return from_string(LOGIN_TEMPLATE).render()

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
        return from_string(VOTE_TEMPLATE).render(candidates=candidates_list, message="Demo mode - Database not connected")
    
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
            return from_string(VOTE_TEMPLATE).render(candidates=candidates_list, message="Vote submitted successfully!")
    
    return from_string(VOTE_TEMPLATE).render(candidates=candidates_list)

@app.route('/result')
def result():
    if not DB_AVAILABLE:
        data = [
            {'candidate_id': 1, 'name': 'Narendra Modi', 'party': 'BJP', 'vote_count': 1, 'percentage': 100.0},
            {'candidate_id': 2, 'name': 'Rahul Gandhi', 'party': 'Congress', 'vote_count': 0, 'percentage': 0.0},
            {'candidate_id': 3, 'name': 'Eknath Shinde', 'party': 'Shiv Sena', 'vote_count': 0, 'percentage': 0.0},
            {'candidate_id': 4, 'name': 'naren', 'party': 'Independent', 'vote_count': 0, 'percentage': 0.0}
        ]
        return from_string(RESULT_TEMPLATE).render(data=data, total_votes=1)
    
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
    
    return from_string(RESULT_TEMPLATE).render(data=data, total_votes=total_votes)

# Helper function
from jinja2 import Template
def from_string(template_str):
    return Template(template_str)

# Export for Vercel
app_handler = app
