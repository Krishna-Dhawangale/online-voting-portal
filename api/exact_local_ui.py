"""
Exact Localhost UI for Vercel - Uses Original Templates
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, redirect, session, render_template_string
import random

app = Flask(__name__, template_folder='.', static_folder=None)
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

# Original base template from localhost
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

        .app-navbar .navbar-brand span.badge {
            border-radius: 999px;
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
            max-width: 960px;
        }

        .card-surface {
            background: radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 60%),
                        radial-gradient(circle at bottom right, rgba(16, 185, 129, 0.08), transparent 60%),
                        #ffffff;
            border-radius: 1.25rem;
            border: 1px solid rgba(148, 163, 184, 0.35);
            box-shadow:
                0 22px 60px rgba(15, 23, 42, 0.35),
                0 0 0 1px rgba(148, 163, 184, 0.15);
            overflow: hidden;
        }

        .card-accent {
            position: relative;
            background: radial-gradient(circle at 10% 0, rgba(56, 189, 248, 0.4), transparent 55%),
                        radial-gradient(circle at 90% 100%, rgba(52, 211, 153, 0.35), transparent 55%),
                        linear-gradient(135deg, #0f172a, #020617);
            color: #e5e7eb;
        }

        .badge-pill {
            border-radius: 999px;
        }

        .field-label {
            font-weight: 500;
            font-size: 0.9rem;
            color: #4b5563;
        }

        .form-control-lg {
            border-radius: 0.9rem;
            border-color: #d1d5db;
            padding: 0.65rem 0.9rem;
        }

        .form-control-lg:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.35);
        }

        .btn-primary {
            border-radius: 999px;
            font-weight: 600;
            letter-spacing: 0.02em;
            box-shadow: 0 16px 35px rgba(37, 99, 235, 0.45);
        }

        .btn-outline-light {
            border-radius: 999px;
        }

        .subtle-link {
            color: #6b7280;
            font-size: 0.9rem;
        }

        .subtle-link a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }

        .subtle-link a:hover {
            text-decoration: underline;
        }

        .results-badge {
            border-radius: 999px;
        }

        .footer-muted {
            color: rgba(148, 163, 184, 0.9);
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="app-shell">
        <nav class="navbar navbar-expand-lg navbar-dark app-navbar shadow-sm">
            <div class="container">
                <a class="navbar-brand fw-semibold d-flex align-items-center gap-2" href="/">
                    <span class="badge bg-light text-primary fw-bold px-2 py-1 badge-pill">OV</span>
                    <span class="d-none d-sm-inline">Online Voting Portal</span>
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="/">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/register">Register</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/vote">Vote</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/result">Results</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/admin">Admin</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <main class="app-main">
            <div class="container">
                {% block content %}{% endblock %}
            </div>
        </main>

        <footer class="py-3">
            <div class="container d-flex flex-column flex-sm-row justify-content-between align-items-center gap-2">
                <span class="footer-muted">© 2025 Online Voting Portal</span>
                <span class="footer-muted">Secure digital voting experience</span>
            </div>
        </footer>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Original login template from localhost
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
      {% if success %}
      <div class="alert alert-success">{{ success }}</div>
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

# Original register template
REGISTER_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Register · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="auth-layout mx-auto">
  <div class="row g-0 card-surface">
    <div class="col-lg-5 card-accent p-4 p-lg-5 d-flex flex-column justify-content-between">
      <div>
        <span class="badge bg-emerald-500 bg-opacity-75 text-white text-uppercase mb-3 badge-pill">
          New Registration
        </span>
        <h1 class="h3 fw-semibold mb-2">Create voting account</h1>
        <p class="mb-0 text-light opacity-75 small">
          Register to vote in the upcoming election. Your vote matters for democracy.
        </p>
      </div>
      <div class="mt-4 small text-light opacity-75">
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-info bg-opacity-75 badge-pill">Verified voting</span>
          <span>Secure and transparent</span>
        </div>
      </div>
    </div>
    <div class="col-lg-7 p-4 p-lg-5 bg-white">
      <div class="mb-3">
        <h2 class="h4 fw-semibold mb-1">Register new voter</h2>
        <p class="text-muted mb-0 small">
          Fill in your details to create your secure voting account.
        </p>
      </div>
      {% if error %}
      <div class="alert alert-danger">{{ error }}</div>
      {% endif %}
      {% if success %}
      <div class="alert alert-success">{{ success }}</div>
      {% endif %}
      <form method="post" novalidate>
        <div class="mb-3">
          <label class="field-label mb-1">Full name</label>
          <input
            type="text"
            name="name"
            class="form-control form-control-lg"
            placeholder="Enter your full name"
            required
          >
        </div>
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
          <label class="field-label mb-1">Mobile number</label>
          <input
            type="text"
            name="mobile"
            class="form-control form-control-lg"
            placeholder="10-digit mobile"
            minlength="10"
            maxlength="10"
            required
          >
        </div>
        <div class="mb-3">
          <label class="field-label mb-1">Password</label>
          <input
            type="password"
            name="password"
            class="form-control form-control-lg"
            placeholder="Create a strong password"
            required
          >
        </div>
        <div class="d-grid mb-3">
          <button type="submit" class="btn btn-primary btn-lg">
            Create voting account
          </button>
        </div>
        <p class="subtle-link text-center mb-0">
          Already have an account?
          <a href="/">Sign in here</a>
        </p>
      </form>
    </div>
  </div>
</div>
'''
)

# Original OTP template
OTP_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}OTP Verification · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="auth-layout mx-auto">
  <div class="row g-0 card-surface">
    <div class="col-lg-5 card-accent p-4 p-lg-5 d-flex flex-column justify-content-between">
      <div>
        <span class="badge bg-purple-500 bg-opacity-75 text-white text-uppercase mb-3 badge-pill">
          OTP Verification
        </span>
        <h1 class="h3 fw-semibold mb-2">Verify your identity</h1>
        <p class="mb-0 text-light opacity-75 small">
          Enter the one-time password sent to your registered mobile number.
        </p>
      </div>
      <div class="mt-4 small text-light opacity-75">
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-warning bg-opacity-75 badge-pill">Time-sensitive</span>
          <span>OTP expires in 10 minutes</span>
        </div>
      </div>
    </div>
    <div class="col-lg-7 p-4 p-lg-5 bg-white">
      <div class="mb-3">
        <h2 class="h4 fw-semibold mb-1">Enter OTP</h2>
        <p class="text-muted mb-0 small">
          For testing, your OTP is displayed below.
        </p>
      </div>
      <div class="alert alert-info">
        <i class="bi bi-info-circle me-2"></i>
        Your OTP is: <strong>{{ otp }}</strong>
      </div>
      {% if error %}
      <div class="alert alert-danger">{{ error }}</div>
      {% endif %}
      <form method="post" novalidate>
        <div class="mb-3">
          <label class="field-label mb-1">One-time password</label>
          <input
            type="text"
            name="otp"
            class="form-control form-control-lg"
            placeholder="6-digit OTP"
            maxlength="6"
            required
          >
        </div>
        <div class="d-grid mb-3">
          <button type="submit" class="btn btn-primary btn-lg">
            Verify and continue
          </button>
        </div>
        <p class="subtle-link text-center mb-0">
          <a href="/">← Back to login</a>
        </p>
      </form>
    </div>
  </div>
</div>
'''
)

# Original vote template
VOTE_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Cast Your Vote · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="content-card mx-auto">
  <div class="card-surface p-4 p-lg-5">
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
    <div class="alert alert-success">{{ message }}</div>
    {% endif %}
    {% if error %}
    <div class="alert alert-danger">{{ error }}</div>
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

<style>
.candidate-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border-color: #e5e7eb;
}

.candidate-card:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.candidate-card input[type="radio"]:checked + .form-check-label {
  color: #3b82f6;
}
</style>
'''
)

# Original results template
RESULTS_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Live Results · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="content-card mx-auto">
  <div class="card-surface p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 align-items-start mb-4">
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

# Vote success template
VOTE_SUCCESS_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Vote Successful · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="content-card mx-auto">
  <div class="card-surface p-4 p-lg-5 text-center">
    <div class="mb-4">
      <i class="bi bi-check-circle text-success" style="font-size: 4rem;"></i>
    </div>
    <h1 class="h4 fw-semibold mb-3">Vote Submitted Successfully!</h1>
    <p class="text-muted mb-4">
      Your vote has been securely recorded and will be counted in the final results.
    </p>
    <div class="d-grid gap-2 d-md-flex justify-content-center">
      <a href="/result" class="btn btn-primary btn-lg">View Results</a>
      <a href="/" class="btn btn-outline-secondary btn-lg">Logout</a>
    </div>
  </div>
</div>
'''
)

# Admin dashboard template (matching localhost admin.html)
ADMIN_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Admin Dashboard · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="content-card mx-auto">
  <div class="card-surface p-4 p-lg-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h4 fw-semibold mb-1">Admin Dashboard</h1>
        <p class="text-muted mb-0 small">
          Manage voting system and view statistics
        </p>
      </div>
      <div class="text-end">
        <span class="badge bg-danger bg-opacity-75 text-white results-badge px-3 py-2 small">
          Admin Access
        </span>
      </div>
    </div>

    {% if message %}
    <div class="alert alert-success">{{ message }}</div>
    {% endif %}

    <div class="row mb-4">
      <div class="col-md-4 mb-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title text-primary">{{ total_voters }}</h5>
            <p class="card-text text-muted small">Total Voters</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title text-success">{{ voted_count }}</h5>
            <p class="card-text text-muted small">Voted</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title text-info">{{ candidates|length }}</h5>
            <p class="card-text text-muted small">Candidates</p>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-6 mb-4">
        <h4 class="h5 fw-semibold mb-3">Add New Candidate</h4>
        <form method="post">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="field-label mb-1">Candidate Name</label>
              <input type="text" name="name" class="form-control" placeholder="Enter candidate name" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="field-label mb-1">Party Name</label>
              <input type="text" name="party" class="form-control" placeholder="Enter party name" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Add Candidate
          </button>
        </form>
      </div>
      
      <div class="col-lg-6 mb-4">
        <h4 class="h5 fw-semibold mb-3">Quick Actions</h4>
        <div class="d-grid gap-2">
          <a href="/admin-logout" class="btn btn-outline-secondary">
            <i class="bi bi-box-arrow-right me-2"></i>Logout Admin
          </a>
          <a href="/" class="btn btn-outline-primary">
            <i class="bi bi-house me-2"></i>Go to Voter Portal
          </a>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <h4 class="h5 fw-semibold mb-3">Voter Records</h4>
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
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
                    <span class="badge bg-success">Voted</span>
                  {% else %}
                    <span class="badge bg-warning">Pending</span>
                  {% endif %}
                </td>
                <td>{{ voter.voted_for or '-' }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>
'''
)
ADMIN_LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Online Voting Portal{% endblock %}', '{% block title %}Admin Login · Online Voting{% endblock %}').replace(
    '{% block content %}{% endblock %}', '''
<div class="auth-layout mx-auto">
  <div class="row g-0 card-surface">
    <div class="col-lg-5 card-accent p-4 p-lg-5 d-flex flex-column justify-content-between">
      <div>
        <span class="badge bg-red-500 bg-opacity-75 text-white text-uppercase mb-3 badge-pill">
          Admin Access
        </span>
        <h1 class="h3 fw-semibold mb-2">Admin Dashboard</h1>
        <p class="mb-0 text-light opacity-75 small">
          Access administrative controls and voting system management.
        </p>
      </div>
      <div class="mt-4 small text-light opacity-75">
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-danger bg-opacity-75 badge-pill">Restricted</span>
          <span>Authorized personnel only</span>
        </div>
      </div>
    </div>
    <div class="col-lg-7 p-4 p-lg-5 bg-white">
      <div class="mb-3">
        <h2 class="h4 fw-semibold mb-1">Admin Login</h2>
        <p class="text-muted mb-0 small">
          Enter your admin credentials to access the dashboard.
        </p>
      </div>
      {% if error %}
      <div class="alert alert-danger">{{ error }}</div>
      {% endif %}
      <form method="post" novalidate>
        <div class="mb-3">
          <label class="field-label mb-1">Admin Username</label>
          <input
            type="text"
            name="username"
            class="form-control form-control-lg"
            placeholder="Enter admin username"
            required
          >
        </div>
        <div class="mb-3">
          <label class="field-label mb-1">Admin Password</label>
          <input
            type="password"
            name="password"
            class="form-control form-control-lg"
            placeholder="Enter admin password"
            required
          >
        </div>
        <div class="d-grid mb-3">
          <button type="submit" class="btn btn-primary btn-lg">
            Access Admin Dashboard
          </button>
        </div>
        <p class="subtle-link text-center mb-0">
          <a href="/">← Back to voter portal</a>
        </p>
      </form>
    </div>
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
            return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials. Please check your Aadhaar and password.")
    
    return render_template_string(LOGIN_TEMPLATE)

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
            return render_template_string(OTP_TEMPLATE, otp=session.get('otp', 'N/A'), error="Invalid OTP. Please try again.")
    
    return render_template_string(OTP_TEMPLATE, otp=session.get('otp', 'N/A'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        aadhaar = request.form['aadhaar']
        mobile = request.form['mobile']
        password = request.form['password']
        
        # Validate inputs
        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return render_template_string(REGISTER_TEMPLATE, error="Aadhaar must be 12 digits.")
        
        if len(mobile) != 10 or not mobile.isdigit():
            return render_template_string(REGISTER_TEMPLATE, error="Mobile must be 10 digits.")
        
        if aadhaar in voters_db:
            return render_template_string(REGISTER_TEMPLATE, error="Aadhaar already registered.")
        
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
        
        return render_template_string(REGISTER_TEMPLATE, success=f"Registration successful! Your Voter ID is {voter_id}. Please login to continue.")
    
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    voter_id = session.get('voter_id')
    if not voter_id:
        return redirect('/')
    
    # Check if already voted
    for aadhaar, voter_data in voters_db.items():
        if voter_data['voter_id'] == voter_id and voter_data['has_voted']:
            return render_template_string(VOTE_TEMPLATE, 
                candidates=candidates_db, 
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
        
        return render_template_string(VOTE_SUCCESS_TEMPLATE)
    
    return render_template_string(VOTE_TEMPLATE, candidates=candidates_db)

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
    
    return render_template_string(RESULTS_TEMPLATE, data=sorted_results, total_votes=total_votes)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Check if admin is logged in
    if not session.get('admin_logged_in'):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                # Prepare data for admin dashboard
                voters_list = [{
                    'voter_id': v['voter_id'],
                    'name': v['name'],
                    'aadhaar': v['aadhaar'],
                    'has_voted': v['has_voted'],
                    'voted_for': v.get('voted_for', '-')
                } for v in voters_db.values()]
                
                return render_template_string(ADMIN_TEMPLATE, 
                    total_voters=len(voters_db),
                    voted_count=len(votes_db),
                    candidates=candidates_db,
                    voters=voters_list)
            else:
                return render_template_string(ADMIN_LOGIN_TEMPLATE, error="Invalid admin credentials")
        
        return render_template_string(ADMIN_LOGIN_TEMPLATE)
    
    # Admin is logged in, handle admin dashboard
    if request.method == 'POST':
        name = request.form['name']
        party = request.form['party']
        
        # Add new candidate
        candidate_id = max(c[0] for c in candidates_db) + 1
        candidates_db.append((candidate_id, name, party))
        
        # Prepare data for admin dashboard
        voters_list = [{
            'voter_id': v['voter_id'],
            'name': v['name'],
            'aadhaar': v['aadhaar'],
            'has_voted': v['has_voted'],
            'voted_for': v.get('voted_for', '-')
        } for v in voters_db.values()]
        
        return render_template_string(ADMIN_TEMPLATE, 
            message=f"Candidate '{name}' from '{party}' added successfully!",
            total_voters=len(voters_db),
            voted_count=len(votes_db),
            candidates=candidates_db,
            voters=voters_list)
    
    # Prepare data for admin dashboard
    voters_list = [{
        'voter_id': v['voter_id'],
        'name': v['name'],
        'aadhaar': v['aadhaar'],
        'has_voted': v['has_voted'],
        'voted_for': v.get('voted_for', '-')
    } for v in voters_db.values()]
    
    return render_template_string(ADMIN_TEMPLATE, 
        total_voters=len(voters_db),
        voted_count=len(votes_db),
        candidates=candidates_db,
        voters=voters_list)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/')

# Export for Vercel
app_handler = app
