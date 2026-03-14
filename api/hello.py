"""
Simplest possible Vercel Python app
"""

def handler(request):
    """Basic Vercel handler"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': '''
        <h1>Hello from Vercel Python!</h1>
        <p>This is a simple test app.</p>
        <p>If you see this, Python is working on Vercel.</p>
        '''
    }

# Alternative handler format
def hello(event, context):
    """Alternative handler format"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Hello World!</h1><p>Python is working!</p>'
    }
