"""
Simple Flask app for Vercel using standard format
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Simple Flask Working!</h1><p>Basic Flask app on Vercel.</p>'

# Export the app for Vercel
app_handler = app
