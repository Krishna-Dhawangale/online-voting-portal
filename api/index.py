"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from legacy_app import app

# Vercel serverless function handler
def handler(event, context):
    """Vercel serverless function handler"""
    return app(event, context)

# Export the handler for Vercel
app_handler = handler

