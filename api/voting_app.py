"""
Working Voting App for Vercel
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, session
import random

app = Flask(__name__)
app.secret_key = "secretkey"

# Basic routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/vote')
def vote():
    # Mock candidates for now
    candidates = [
        (1, 'Narendra Modi', 'BJP'),
        (2, 'Rahul Gandhi', 'Congress'),
        (3, 'Eknath Shinde', 'Shiv Sena'),
        (4, 'naren', 'Independent')
    ]
    return render_template('vote.html', candidates=candidates)

@app.route('/result')
def result():
    # Mock results for now
    data = [
        ('Narendra Modi', 1),
        ('Rahul Gandhi', 0),
        ('Eknath Shinde', 0),
        ('naren', 0)
    ]
    return render_template('result.html', data=data)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/verify')
def verify():
    return render_template('otp.html')

# Export for Vercel
app_handler = app
