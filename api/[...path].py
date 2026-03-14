from legacy_app import app

# Vercel serverless function handler for all routes
handler = app.as_wsgi_app()

