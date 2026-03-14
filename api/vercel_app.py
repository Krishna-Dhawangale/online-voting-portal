"""
Simplified Vercel Flask App
"""
import sys
import os

# Add root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask and create app
from flask import Flask, request

# Create minimal Flask app for testing
app = Flask(__name__)

@app.route('/')
def hello():
    """Simple hello route"""
    print("Hello route accessed")
    return """
    <h1>Hello from Vercel!</h1>
    <p>Your Flask app is working.</p>
    <p><a href="/test">Test Route</a></p>
    <p><a href="/full">Full Voting Portal</a></p>
    """

@app.route('/test')
def test():
    """Test route"""
    print("Test route accessed")
    return "<h1>Test Route Working!</h1>"

@app.route('/full')
def full_app():
    """Try to import and use the full app"""
    try:
        print("Attempting to import full app...")
        from legacy_app import app as full_app
        print("Full app imported successfully")
        return full_app(request.environ, lambda status, headers: None)
    except Exception as e:
        print(f"Error importing full app: {e}")
        import traceback
        return f"""
        <h1>Error importing full app</h1>
        <p>Error: {str(e)}</p>
        <pre>{traceback.format_exc()}</pre>
        """

# Vercel handler
def handler(event, context):
    """Vercel serverless function handler"""
    return app(event, context)

# Export for Vercel
app_handler = handler
