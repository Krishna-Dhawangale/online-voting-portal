# Vercel Deployment Guide for Online Voting Portal

## Fixed Issues ✅

The following issues have been resolved:

1. **API Handler Missing**: Added proper Flask app handler for Vercel serverless functions
2. **Route Configuration**: Fixed vercel.json to properly route all requests
3. **Session Configuration**: Added Vercel-specific Flask session settings
4. **Database Seeding**: Automatic data seeding for new deployments

## Deployment Steps

### 1. Set Up Database (Required)

**Option A: Use Neon (Recommended)**
1. Go to [neon.tech](https://neon.tech)
2. Create a free account
3. Create a new database
4. Copy the connection string (looks like `postgresql://user:pass@host/dbname?...`)

**Option B: Use Supabase**
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings > Database
4. Copy the connection string

### 2. Configure Vercel Environment Variables

1. Push your code to GitHub
2. Import your repository to Vercel
3. In Vercel Project → Settings → Environment Variables:
   - **Name**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string
   - **Environments**: Production, Preview, Development

4. Add additional variables:
   - **Name**: `PYTHON_VERSION`
   - **Value**: `3.10`

### 3. Deploy

1. Commit and push your changes to GitHub
2. Vercel will automatically deploy
3. Wait for deployment to complete

## File Structure for Vercel

```
online_voting_python/
├── api/
│   ├── index.py          # Main API handler
│   └── [...path].py     # Catch-all handler
├── templates/            # HTML templates
├── static/              # CSS/JS files
├── legacy_app.py        # Flask application
├── db.py               # Database configuration
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── run.py             # Local development
```

## What Was Fixed

### 1. API Handler (`api/index.py`)
```python
from legacy_app import app

# Vercel serverless function handler
handler = app.as_wsgi_app()
```

### 2. Vercel Configuration (`vercel.json`)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.10"
  }
}
```

### 3. Flask Configuration
Added Vercel-specific session settings for serverless environment.

### 4. Database Seeding
Automatic candidate seeding for new deployments.

## Troubleshooting

### "Page Not Found" Error
- ✅ Fixed: Added proper API handlers
- ✅ Fixed: Updated route configuration

### Database Issues
- Ensure `DATABASE_URL` is set in Vercel environment variables
- Use PostgreSQL (SQLite won't work on Vercel)

### Session Issues
- ✅ Fixed: Added Vercel-specific session configuration

### Build Errors
- Check requirements.txt has all dependencies
- Ensure Python version is set to 3.10

## Testing After Deployment

1. Visit your Vercel URL
2. Try registering a new voter
3. Test login and OTP flow
4. Cast a vote
5. Check results page
6. Access admin panel

## Local Development

To run locally:
```bash
python run.py
```

This will use SQLite database at `online_voting.sqlite`.

## Production URL

After deployment, your app will be available at:
`https://your-project-name.vercel.app`

## Support

If you still encounter issues:

1. Check Vercel deployment logs
2. Verify environment variables
3. Ensure database is accessible
4. Check that all files are committed to Git

The deployment is now properly configured for Vercel serverless hosting!
