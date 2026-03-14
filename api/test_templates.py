"""
Test Templates for Vercel
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, redirect, session
import random

app = Flask(__name__)
app.secret_key = "secretkey"

# Test basic HTML responses first
@app.route('/')
def login():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Login - Voting Portal</title></head>
    <body>
        <h1>Online Voting Portal</h1>
        <h2>Login</h2>
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

@app.route('/register')
def register():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Register - Voting Portal</title></head>
    <body>
        <h1>Online Voting Portal</h1>
        <h2>Register New Voter</h2>
        <form method="post">
            <label>Name: <input type="text" name="name" required></label><br><br>
            <label>Aadhaar: <input type="text" name="aadhaar" required></label><br><br>
            <label>Mobile: <input type="text" name="mobile" required></label><br><br>
            <label>Password: <input type="password" name="password" required></label><br><br>
            <button type="submit">Register</button>
        </form>
        <p><a href="/">Back to Login</a></p>
    </body>
    </html>
    '''

@app.route('/vote')
def vote():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Vote - Voting Portal</title></head>
    <body>
        <h1>Online Voting Portal</h1>
        <h2>Cast Your Vote</h2>
        <form method="post">
            <h3>Select your candidate:</h3>
            <input type="radio" name="candidate" value="1" required> Narendra Modi - BJP<br>
            <input type="radio" name="candidate" value="2" required> Rahul Gandhi - Congress<br>
            <input type="radio" name="candidate" value="3" required> Eknath Shinde - Shiv Sena<br>
            <input type="radio" name="candidate" value="4" required> naren - Independent<br><br>
            <button type="submit">Submit Vote</button>
        </form>
        <p><a href="/result">View Results</a></p>
        <p><a href="/">Back to Login</a></p>
    </body>
    </html>
    '''

@app.route('/result')
def result():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Results - Voting Portal</title></head>
    <body>
        <h1>Online Voting Portal</h1>
        <h2>Election Results</h2>
        <table border="1">
            <tr><th>Candidate</th><th>Party</th><th>Votes</th></tr>
            <tr><td>Narendra Modi</td><td>BJP</td><td>1</td></tr>
            <tr><td>Rahul Gandhi</td><td>Congress</td><td>0</td></tr>
            <tr><td>Eknath Shinde</td><td>Shiv Sena</td><td>0</td></tr>
            <tr><td>naren</td><td>Independent</td><td>0</td></tr>
        </table>
        <p><a href="/vote">Back to Voting</a></p>
        <p><a href="/">Back to Login</a></p>
    </body>
    </html>
    '''

@app.route('/admin')
def admin():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Admin - Voting Portal</title></head>
    <body>
        <h1>Online Voting Portal</h1>
        <h2>Admin Dashboard</h2>
        <h3>Add New Candidate</h3>
        <form method="post">
            <label>Name: <input type="text" name="name" required></label><br><br>
            <label>Party: <input type="text" name="party" required></label><br><br>
            <button type="submit">Add Candidate</button>
        </form>
        <p><a href="/result">View Results</a></p>
        <p><a href="/">Back to Login</a></p>
    </body>
    </html>
    '''

@app.route('/verify')
def verify():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>OTP Verification - Voting Portal</title></head>
    <body>
        <h1>Online Voting Portal</h1>
        <h2>Enter OTP</h2>
        <form method="post">
            <label>OTP: <input type="text" name="otp" required></label><br><br>
            <button type="submit">Verify OTP</button>
        </form>
        <p><a href="/">Back to Login</a></p>
    </body>
    </html>
    '''

# Export for Vercel
app_handler = app
