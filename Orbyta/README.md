# ORBYTA — PCOS Prediction & Awareness Platform

This version shifts Orbyta from a regular period tracker into a **PCOS-focused screening, awareness and wellness companion**.

## What changed

- **Open App → Login / Sign up** with local email + password.
- Passwords are stored as salted PBKDF2 hashes, not plain text.
- Each account has its own profile and data.
- On first sign-in, Orbyta asks for **name, age, height and weight**.
- **BMI is calculated automatically** from height and weight.
- Removed **Try Demo** and all automatic fictional Aisha data.
- Added a guided, animated Amie onboarding screen after profile setup.
- Choose one of **3 Amie avatars** (bear, bunny, cat) and give the assistant a custom name.
- PCOS-focused screening uses cycle regularity, missed periods, acne, hair changes, skin changes, weight change, fatigue and lifestyle signals.
- Screening result is shown as a **large percentage**, level, progress visual and explanatory cards.
- Added contributing patterns, general PCOS risk factors, causes explanation, lifestyle actions and clinician follow-up guidance.
- Dashboard now reads the **current signed-in user's real database data**.
- Dashboard risk chart uses saved screening results rather than fake check-in-derived values.
- Report page is now a proper visual report with a large risk number and graph.
- Cycle and symptom pages are framed as **PCOS-associated signals**, not the central product.
- Added light/dark theme setting.
- Added sign out and JSON backup.
- Resources are PCOS-focused and point to trusted health sources.
- Rebuilt Amie as a broader **women’s reproductive-health assistant** covering PCOS, periods, fertility basics, contraception, pregnancy questions, sexual/reproductive health, menopause, nutrition, exercise, sleep/stress and when to seek care.
- Added safety-first urgent-symptom triage and clearer non-diagnostic boundaries.
- Added a colourful responsive visual system with cards, gradients, badges, progress rings, trend graphs, symptom pie charts and wellness bar charts.
- Added a more app-like responsive mobile layout, polished onboarding, quick Amie prompts and an installable web-app manifest.
- Dashboard now includes the full saved screening-history trend instead of only the latest screening point.

## Important: reset the old SQLite database once

The original project used a different `users` table. Because SQLAlchemy's `create_all()` does not migrate existing columns, delete the old database **once** before first running this version:

`backend/orbyta.db`

Do this only if you do not need the old demo data.

## Run on Windows

Double-click `START_ORBYTA.bat`, or run manually:

### Terminal 1 — backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — frontend

```powershell
cd frontend
npm install
npm run dev
```

Open:

`http://127.0.0.1:5173`

## Routes

- `/` — landing page
- `/login` — sign in / sign up
- `/onboarding` — profile + Amie setup
- `/dashboard` — current-user PCOS dashboard
- `/screening` — PCOS screening
- `/cycle` — cycle pattern logging
- `/symptoms` — PCOS-associated symptom logging
- `/insights` — PCOS explanations and personalized observations
- `/amie` — women’s reproductive-health AI-style assistant (local, deterministic, no API key required)
- `/resources` — trusted PCOS resources
- `/report` — visual screening report
- `/settings` — profile, BMI, theme, Amie, sign out, backup

## Google sign-in

The **Continue with Google** button is present in the UI, but a real Google OAuth flow cannot be completed without a Google Cloud OAuth client ID, redirect URI and production/local OAuth configuration. The local email/password authentication is fully implemented. For a real deployment, connect the button to Firebase Auth, Auth0, Clerk, Supabase Auth, or Google Identity Services.

## PCOS / medical scope

Orbyta is a hackathon/educational screening and awareness prototype. A percentage is **not a clinically validated diagnosis or clinical probability**. PCOS can have several causes and presentations, and diagnosis requires a qualified healthcare professional. The lifestyle guidance is general wellness information, not individualized medical treatment.

There is also no guaranteed lifestyle method to prevent PCOS itself. The app therefore uses safer language such as **support metabolic health, reduce symptom burden and maintain healthy routines** rather than claiming PCOS can be prevented.

## Manual VS Code checklist

If you want to reproduce the changes yourself instead of using the updated ZIP, these are the files that were changed:

1. `frontend/src/App.jsx`
   - authentication screens
   - onboarding
   - Amie selector/name
   - dashboard
   - PCOS screening
   - visual report
   - settings/theme/backup/sign out
   - removed Try Demo
2. `frontend/src/api.js`
   - keep the existing API helper; it now automatically sends the stored session token.
3. `frontend/src/index.css`
   - dark/light theme classes
   - reusable input styles
   - print-friendly report styling
4. `backend/app/main.py`
   - authentication
   - per-user database filtering
   - profile/settings APIs
   - current-user dashboard
   - backup API
   - report API
   - no demo endpoint
5. `backend/app/models.py`
   - email/password hash
   - Amie settings
   - per-user records
   - stored screening inputs
6. `backend/app/schemas.py`
   - auth/profile/settings validation
   - BMI is no longer entered by the screening form
7. `backend/app/services/ml_service.py`
   - PCOS-focused contributing factors
   - risk-factor and lifestyle explanations
   - clinician follow-up flag
   - safer non-diagnostic wording
8. `backend/app/services/amie.py`
   - PCOS-focused assistant responses
9. `backend/requirements.txt`
   - added `email-validator`

## Production note

For a real healthcare product, do not use the local demo authentication/session design as-is. Use a managed identity provider, secure server-side sessions/JWT handling, encrypted transport/storage, proper consent and privacy controls, audit logging, validated clinical models, clinical review, and applicable regulatory/privacy compliance.
