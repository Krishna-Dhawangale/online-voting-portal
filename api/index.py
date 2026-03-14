from legacy_app import app

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

# Alternative handler for Vercel
app_handler = app.as_wsgi_app()

