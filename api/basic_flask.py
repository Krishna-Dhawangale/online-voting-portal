"""
Most basic Flask app for Vercel
"""

# Try the most basic Flask app
try:
    from flask import Flask, request
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return '<h1>Basic Flask Working!</h1><p>Flask app is running on Vercel.</p>'
    
    # Vercel handler - fixed for proper Vercel format
    def handler(event, context):
        """Proper Vercel handler for Flask"""
        # Convert Vercel event to WSGI format
        environ = {
            'REQUEST_METHOD': event.get('httpMethod', 'GET'),
            'PATH_INFO': event.get('path', '/'),
            'QUERY_STRING': event.get('queryString', ''),
            'SERVER_NAME': 'vercel.app',
            'SERVER_PORT': '443',
            'wsgi.url_scheme': 'https',
            'wsgi.input': event.get('body', ''),
            'CONTENT_LENGTH': str(len(event.get('body', ''))),
            'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
        }
        
        # Add headers
        for key, value in event.get('headers', {}).items():
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
        
        # Start response
        response = {}
        
        def start_response(status, headers):
            response['status'] = status
            response['headers'] = dict(headers)
        
        # Get Flask response
        app_response = app(environ, start_response)
        body = b''.join(app_response) if isinstance(app_response, list) else app_response
        
        return {
            'statusCode': int(response['status'].split()[0]),
            'headers': response['headers'],
            'body': body.decode('utf-8') if isinstance(body, bytes) else body
        }
    
    print("Flask app created successfully")
    
except ImportError as e:
    print(f"Flask import error: {e}")
    
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': f'Flask import error: {e}'
        }
