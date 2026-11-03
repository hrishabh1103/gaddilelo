# GaadiLelo.com — Deployment Verification Report & Safe Next Steps

**Audit Date**: November 3, 2026  
**Subject**: Critical Verification of Deployment Documents, Assumptions, Migration Tools, and Provider Compatibility  
**Target Environment**: Supabase Project `https://khgvmqfidpazfdjitkeb.supabase.co`  
**Verdict**: **VERIFICATION BLOCKED — REQUIRED SERVICES NOT CONFIGURED**

---

## 1. Executive Summary

This report performs a comprehensive, code-level verification of the five deployment documents previously prepared for GaadiLelo.com:
1. `FREE_DEPLOYMENT_PLAN.md`
2. `SUPABASE_MIGRATION_PLAN.md`
3. `FREE_TIER_COST_AND_LIMITS.md`
4. `DEPLOYMENT_RUNBOOK.md`
5. `PRODUCTION_READINESS_AUDIT.md`

### Key Findings
1. **Critical Discrepancies in Environment Variables**:
   The previous deployment plan and runbook specified `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`, and `EMAIL_FROM`. However, the actual application code in `backend/app/core/config.py` and `backend/app/services/email_service.py` requires `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_FROM_EMAIL`. Using the documented variable names would cause email delivery to silently fail.
2. **Migration Runner Limitations (`scripts/run_migrations.py`)**:
   - The `--dry-run` flag in `scripts/run_migrations.py` **does not connect to PostgreSQL** and does not parse or validate SQL against the target database. It only asserts that the 4 `.sql` files exist on the local disk.
   - Migrations are **not idempotent**: `001_initial_schema.sql` uses un-guarded `CREATE TYPE ... AS ENUM` statements. Running the script against an already partially-migrated database will crash with duplicate type errors.
   - There is no migration tracking table (e.g. `schema_migrations`), risking repeated or skipped migrations.
   - SQLAlchemy `create_async_engine` requires the `postgresql+asyncpg://` URI scheme. Standard Supabase URI strings start with `postgresql://` and will fail if passed unmodified.
3. **Vercel Hobby Plan Terms of Service Violation**:
   GaadiLelo is a commercial group-buying marketplace with dealer bids and customer acquisition. Deploying GaadiLelo on Vercel's Hobby tier violates Vercel's Terms of Service ("non-commercial personal projects only") and risks immediate account suspension. Cloudflare Pages or Netlify Free must be used instead.
4. **Resend Email Restrictions Without Verified Domain**:
   On Resend's Free tier, the default sender (`onboarding@resend.dev`) can only send emails to the **single registered account owner's email**. It cannot send verification or password reset emails to arbitrary prospective buyers or dealers until a custom domain with DNS records (SPF/DKIM/DMARC) is verified.
5. **Render Inactivity & Free Quotas**:
   Render Free Web Services spin down after 15 minutes of inactivity (causing 45s cold starts). Furthermore, Render's 750 free instance hours per month are shared across the account; hosting both frontend and backend on Render Free would exhaust the monthly quota in 15 days.

---

## 2. Verified Repository Facts vs. Codebase Reality

| Feature / Config | Documented Claim | Verified Codebase Reality | Status |
| :--- | :--- | :--- | :---: |
| **Backend Entrypoint** | `app.main:app` | `backend/app/main.py` defines `app = FastAPI(...)`. From `backend/` directory, the start command is `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. | **VERIFIED LOCALLY** |
| **Python Runtime** | Python 3.11–3.13 | Local environment runs Python 3.13.1. Requirements in `backend/requirements.txt` contain compatible asyncpg, sqlalchemy, pydantic-settings, passlib, python-jose. | **VERIFIED LOCALLY** |
| **Frontend Framework** | Next.js 15.1, React 19 | `frontend/package.json` specifies `"next": "^15.1.0"`, `"react": "^19.0.0"`. All 31 route pages declare `'use client'`. | **VERIFIED LOCALLY** |
| **Next.js Server Dependencies** | Potential SSR / API routes | **Zero Next.js API routes** (`route.ts`) and **zero middleware** (`middleware.ts`) in application code. All pages load data client-side via `apiFetch()` in `useEffect`. | **VERIFIED LOCALLY** |
| **Database Connection** | `postgresql+asyncpg://` | `backend/app/core/database.py` uses `create_async_engine(settings.DATABASE_URL)`. Passing standard `postgresql://` crashes with dialect error unless converted to `postgresql+asyncpg://`. | **CORRECTED** |
| **Email Settings** | `EMAIL_HOST`, `EMAIL_PORT`... | `backend/app/core/config.py` lines 42–47 define `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_USE_TLS`. | **CORRECTED** |
| **Background Scheduler** | Background worker needed | `backend/app/services/vehicle_intelligence/scheduler.py` runs inside the FastAPI lifespan and respects `ENABLE_BACKGROUND_SCHEDULER=false`. No separate worker process is mandatory for the pilot. | **VERIFIED LOCALLY** |
| **Rate Limiter** | Redis or In-memory | `backend/app/core/rate_limiter.py` safely falls back to thread-safe in-memory sliding window when `REDIS_URL` is omitted. | **VERIFIED LOCALLY** |

---

## 3. Official Provider Terms & Inactivity Realities

### 3.1 Supabase Free Tier
- **Official Terms**: 500 MB database storage, 2 active projects, 5 GB egress/month, 50,000 monthly active users.
- **Inactivity Policy**: Free tier projects are automatically **paused after 7 consecutive days of inactivity** (zero API requests, zero SQL queries, and zero dashboard logins).
- **Correction**: Pinging a local or Render `/health` endpoint does **not** guarantee Supabase stays active if Render is sleeping or if the health check does not execute a SQL query on Supabase. If paused, restoring requires a manual login to the Supabase dashboard.

### 3.2 Render Free Web Service
- **Official Terms**: 750 free instance hours per user per month, 512 MB RAM, 0.1 CPU core.
- **Inactivity Policy**: Spins down to sleep after **15 minutes** of no incoming HTTP requests.
- **Spin-up Latency**: 35 to 50 seconds cold-start delay on first incoming connection.
- **Limitation**: Free web services do not have persistent disk storage. Local logs and SQLite files are wiped upon restart.
- **Account-Wide Hour Pool**: 750 hours $\approx 31.25$ days of single-instance runtime. If the frontend was also hosted on Render, total hours would double ($1,460$ hrs), exhausting the free tier by day 15 of every month.

### 3.3 Vercel Hobby Plan
- **Official Terms**: Strictly for **personal, non-commercial use only**.
- **Commercial Prohibition**: GaadiLelo is an Indian vehicle group-buying marketplace designed for commercial transactions between car buyers and dealerships. Deploying GaadiLelo on Vercel Hobby directly violates Section 2 of Vercel’s Terms of Service and invites account suspension.
- **Correction**: Vercel Hobby is **rejected** for this commercial pilot. Recommended alternatives are **Cloudflare Pages** or **Netlify Free** (which permit commercial websites on their free tiers).

### 3.4 Resend Free Tier
- **Official Terms**: 3,000 emails/month, 100 emails/day.
- **Sender Restrictions**: Without a custom verified domain, Resend requires using `onboarding@resend.dev` and **only permits sending to the email address used to register the Resend account**.
- **Correction**: Resend cannot be used to verify arbitrary customer email addresses during a public pilot until the owner adds DNS TXT/MX records for a verified domain.
- **Pilot Alternative**: Gmail SMTP with an App Password or Brevo (free 300 emails/day with verified single-sender address) can send to any recipient without domain DNS.

---

## 4. Migration Runner Audit (`scripts/run_migrations.py`)

An in-depth code inspection of `scripts/run_migrations.py` revealed four critical safety defects:

1. **Non-Connecting Dry Run**:
   ```python
   if dry_run:
       print("\n[SUCCESS] Dry-run validated. All 4 migration files exist in proper sequence.")
       return
   ```
   The dry run only verifies file existence on disk. It performs **no connection test, no credential validation, no SSL check, and no SQL syntax analysis** against PostgreSQL.
2. **Lack of Idempotency**:
   In `001_initial_schema.sql`:
   ```sql
   CREATE TYPE user_role_enum AS ENUM ('BUYER', 'DEALER', 'ADMIN');
   ```
   PostgreSQL does not support `CREATE TYPE IF NOT EXISTS`. If this migration is interrupted or re-run on a database where `user_role_enum` already exists, PostgreSQL throws `duplicate type` and aborts the entire transaction.
3. **No Migration History Table**:
   The script does not record executed migrations in a `schema_migrations` table. It cannot determine if migration 001 was already executed.
4. **URI Scheme Incompatibility**:
   Supabase dashboard provides URIs in the format `postgresql://postgres:[password]@...`.
   SQLAlchemy's `create_async_engine` throws an error if given `postgresql://` instead of `postgresql+asyncpg://`.

---

## 5. Security & Risk Analysis

1. **Direct Database Credential Safety**:
   Database passwords, JWT secrets, and API keys must never be committed to Git or pasted into conversation transcripts.
2. **PgBouncer Port 6543 vs. Direct Port 5432**:
   - Supabase port 6543 uses PgBouncer in transaction pooling mode, which does **not** support PostgreSQL named prepared statements. Using `asyncpg` on port 6543 requires `statement_cache_size=0`.
   - Running DDL migrations should be done through direct port `5432` or via the Supabase Dashboard SQL Editor.
3. **CORS Configuration**:
   When deployed, `CORS_ORIGINS` on Render must include the exact HTTPS domain of the frontend (e.g. `https://gaadilelo.pages.dev`).

---

## 6. Corrected Environment Variables Checklist

### Backend Configuration (Render Environment Settings)
```ini
# Core Environment
ENVIRONMENT=production
SECRET_KEY=<64-char-random-hex-generated-by-owner>
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres

# Frontend & CORS
FRONTEND_URL=https://<your-frontend-subdomain>.pages.dev
CORS_ORIGINS=["https://<your-frontend-subdomain>.pages.dev"]

# Transactional Email (Resend SMTP or Gmail SMTP)
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=<your-resend-api-key>
SMTP_FROM_EMAIL=onboarding@resend.dev
SMTP_USE_TLS=true

# Background Operations
ENABLE_BACKGROUND_SCHEDULER=false
```

### Frontend Configuration (Cloudflare Pages / Netlify Settings)
```ini
NEXT_PUBLIC_APP_URL=https://<your-frontend-subdomain>.pages.dev
NEXT_PUBLIC_API_URL=https://<your-backend-subdomain>.onrender.com/api/v1
NEXT_PUBLIC_PILOT_CITY=Indore
NEXT_PUBLIC_BRAND_NAME=GaadiLelo
NEXT_PUBLIC_BRAND_TAGLINE=Buy Together. Save Together.
NEXT_PUBLIC_DEMO_MODE=false
```

---

## 7. Recommended Safe Hosting Architecture

1. **Database**: Supabase PostgreSQL (`khgvmqfidpazfdjitkeb`, Free Tier, 500 MB).
2. **Backend**: Render Free Web Service (FastAPI, 750 instance hours/month, auto HTTPS).
3. **Frontend**: Cloudflare Pages or Netlify Free (Complies with commercial terms of service, unlimited/generous bandwidth, auto HTTPS, zero cold starts for static client assets).
4. **Email**: 
   - *If testing only with owner account*: Resend Free (`onboarding@resend.dev`).
   - *If testing with real external buyer/dealer addresses*: Gmail SMTP (with Google Account App Password) or Brevo Free.
5. **Rate Limiting**: Single-instance in-memory sliding window fallback (active by default, ₹0 cost, zero quota risks).

---

## 8. Exact Step-by-Step Next Actions for Owner

### Action 1: Test Supabase Connectivity Locally (Safe Dry Run)
Run a local script to verify network connectivity and credentials against Supabase without modifying any data:
```bash
# Set your Supabase connection string in your local terminal session:
export TEST_DB_URL="postgresql://postgres:[YOUR-PASSWORD]@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"

# Run a read-only connection probe:
python -c "
import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

url = os.environ['TEST_DB_URL'].replace('postgresql://', 'postgresql+asyncpg://')
async def probe():
    engine = create_async_engine(url, connect_args={'ssl': True})
    async with engine.begin() as conn:
        res = await conn.execute(text('SELECT version();'))
        print('[SUCCESS] Connected to Supabase PostgreSQL:')
        print(' ', res.scalar())
    await engine.dispose()
asyncio.run(probe())
"
```

### Action 2: Review and Execute Migrations via Supabase Dashboard SQL Editor
Because migrations 001–004 contain PostgreSQL DDL statements and custom Enum types, the safest, zero-risk method to apply them is directly through the official Supabase Web Console:
1. Open the [Supabase SQL Editor](https://supabase.com/dashboard/project/khgvmqfidpazfdjitkeb/sql).
2. Paste the contents of `database/migrations/001_initial_schema.sql` and click **Run**.
3. Paste and run `database/migrations/002_vehicle_intelligence.sql`.
4. Paste and run `database/migrations/003_free_vehicle_data.sql`.
5. Paste and run `database/migrations/004_buyer_intent_and_auth.sql`.
6. Inspect the **Table Editor** to confirm all 31 tables are present.

### Action 3: Review and Approve Cloud Hosting Provisioning
Once the database tables are confirmed, approve linking the repository to Render and Cloudflare Pages/Netlify.

