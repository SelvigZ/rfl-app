# RFL App

Mobile-friendly web app for tracking daily weight and waist measurements.

## What It Is

- Flask app
- local SQLite for development
- hosted Postgres-ready via `DATABASE_URL`
- mobile-first dashboard
- add/edit/delete measurements
- chart with selected-point details
- starter seed data included for first deploy

## Run

```powershell
python app.py
```

Or double-click:

- `C:\Users\zacha\OneDrive\Desktop\Open RFL App.cmd`

Then open:

- `http://127.0.0.1:5000/` on the desktop
- or `http://<your-computer-name-or-local-ip>:5000/` on your phone when on the same Wi-Fi

## Hosting Direction

Target hosted stack:

- Vercel
- Neon Postgres

Set `DATABASE_URL` in the environment for hosted use.

## Date Handling

The add-measurement form uses `public/js/local-date.js` to set the default entry date from the browser/device local date. The server still validates submitted `YYYY-MM-DD` values and provides a fallback date when JavaScript is unavailable.

Detailed deployment notes:

- `DEPLOY_VERCEL_NEON.md`

## Project Layout

```text
RFL App/
├─ app.py
├─ requirements.txt
├─ DEPLOY_VERCEL_NEON.md
├─ data/
│  ├─ rfl_app.db
│  └─ seed_measurements.csv
├─ public/
├─ templates/
└─ scripts/
```
