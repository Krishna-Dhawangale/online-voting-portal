"""
Most basic Flask app for Vercel
"""

# Try the most basic Flask app
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return '<h1>Basic Flask Working!</h1><p>Flask app is running on Vercel.</p>'
    
    # Vercel handler
    def handler(event, context):
        return app(event, context)
    
    print("Flask app created successfully")
    
except ImportError as e:
    print(f"Flask import error: {e}")
    
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': f'Flask import error: {e}'
        }
