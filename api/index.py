from legacy_app import app

# Vercel serverless function handler
handler = app.as_wsgi_app()

