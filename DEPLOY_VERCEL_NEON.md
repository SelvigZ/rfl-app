# Deploy RFL App to Vercel + Neon

## Why This Setup

This app is now prepared for:

- Vercel hosting
- Neon Postgres

Reason:

- Vercel Hobby is free for a small personal app
- Neon Free is enough for this tiny dataset
- this avoids paying monthly just to host a simple tracker

## Current App Shape

The app now works in two modes:

### Local mode

- local SQLite file
- used when `DATABASE_URL` is not set

### Hosted mode

- Postgres via `DATABASE_URL`
- used automatically when `DATABASE_URL` is present

## Important Tradeoff

This is the fast path, not the most enterprise-clean path.

Likely future rework or limitations:

- Vercel is serverless, so this is not the same as a traditional always-on Flask host
- if the app grows meaningfully, a more conventional app host may become more comfortable
- if you later want more advanced auth, background jobs, or richer backend behavior, the stack may need another cleanup pass

For this personal app, that is acceptable.

## Before Deploying

If the tracker data changes and you want the hosted seed to match it, run:

```powershell
python scripts/sync_seed_from_rfl_tracker.py
```

That refreshes:

- `data/seed_measurements.csv`

## Step 1: Create a Neon Database

1. Go to Neon and create a free project.
2. Create or use the default database.
3. Copy the connection string.

You want the full Postgres connection string.

It will look roughly like:

```text
postgresql://user:password@host/dbname?sslmode=require
```

## Step 2: Create a Git Repo for RFL App

The app should live in its own repo, not inside the finance repo.

Suggested repo name:

- `rfl-app`

Push the contents of:

- `C:\Users\zacha\OneDrive\Desktop\RFL App`

## Step 3: Import the Repo into Vercel

1. Create a new Vercel project.
2. Connect the `rfl-app` repo.
3. Let Vercel detect the Python app.

The app entrypoint is already prepared:

- `app.py`

Static assets are already prepared in:

- `public/`

## Step 4: Set Environment Variables in Vercel

Set:

- `DATABASE_URL`
- `SECRET_KEY`

### DATABASE_URL

Paste the Neon connection string.

### SECRET_KEY

Use any strong random string.

Example:

```text
RFL_APP_SECRET_2026_LOCALISH_BUT_HOSTED
```

Use something better than that in practice.

## Step 5: Deploy

Deploy the project.

On first deploy:

- the app will create the `measurements` table
- if the table is empty, it will seed from `data/seed_measurements.csv`

That means your current two starter entries should appear automatically.

## Step 6: Verify

After deploy, verify:

1. dashboard loads
2. cards show current data
3. chart renders
4. add measurement works
5. edit measurement works
6. delete measurement works

## Expected Hosted Behavior

Once hosted:

- no need to keep Python running on your computer
- usable from phone directly by URL
- can be added to iPhone home screen

## Recommended Cutover

Once the hosted app is working:

1. use the hosted app as the primary interface
2. stop relying on the `RFL Tracker` inbox flow for normal entry
3. keep `RFL Tracker` only as a prototype/archive until you are confident
4. then retire the old workflow

## If Seeding Needs a Refresh Before Deploy

Use:

```powershell
python scripts/sync_seed_from_rfl_tracker.py
```

That updates the bundled seed file from the existing tracker CSV.

## Files That Matter for Deploy

- `app.py`
- `requirements.txt`
- `vercel.json`
- `.python-version`
- `templates/`
- `public/`
- `data/seed_measurements.csv`

## Summary

Recommended practical path:

- keep the app lightweight
- deploy to Vercel
- use Neon free for Postgres
- accept the small migration rework now
- retire the file-based workflow once the hosted version proves itself
