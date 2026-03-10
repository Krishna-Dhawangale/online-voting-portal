## Persisting database on Vercel (Hosted Postgres)

Vercel's filesystem is ephemeral, so **SQLite won't persist** reliably in production.
This project now supports a hosted database via **`DATABASE_URL`**.

### 1) Create a Postgres database (recommended)

Use any hosted Postgres provider:
- Neon
- Supabase
- Railway

Copy the connection string (it looks like `postgresql://user:pass@host/dbname?...`).

### 2) Set Vercel environment variable

In Vercel Project → Settings → Environment Variables:

- **Name**: `DATABASE_URL`
- **Value**: your Postgres connection string

Deploy again after saving.

### 3) First deploy initializes tables

On startup, the app creates tables if missing and seeds:
- default admin: `admin` / `admin123`
- default candidates (if none exist)

### Local development (still works)

If you do **not** set `DATABASE_URL`, the app uses local SQLite at `instance/online_voting.sqlite`.

