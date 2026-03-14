"""
Direct Vercel App Entry Point
"""
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and create app
from legacy_app import app

# Direct handler for Vercel
def handler(request):
    """Handle Vercel requests"""
    return app(request.environ, lambda status, headers: None)

# Export for Vercel
app_handler = handler
