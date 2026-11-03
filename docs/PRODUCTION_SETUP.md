# GaadiLelo — Production Deployment & Hosting Guide

This document outlines the architecture, configuration, and step-by-step procedures to deploy GaadiLelo to production.

---

## 1. Architecture Overview

- **Frontend**: Next.js 15.5 App Router (TypeScript, Tailwind CSS, Lucide icons)
  - Recommended Hosting: **Vercel**
- **Backend API**: FastAPI (Python 3.11+, SQLAlchemy 2.0 Async, Pydantic v2, PyJWT, Bcrypt)
  - Recommended Hosting: **Render / Railway / Google Cloud Run / AWS EC2**
- **Database**: PostgreSQL (Supabase or Managed Cloud PostgreSQL)
- **Local Fallback**: SQLite (`gaadilelo.db`) with zero configuration required for local evaluation.

---

## 2. Environment Variables

### Frontend (`frontend/.env.local` or Vercel Environment Variables)
| Variable | Description | Production Example |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_APP_URL` | Canonical web URL | `https://gaadilelo.com` |
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://api.gaadilelo.com/api/v1` |
| `NEXT_PUBLIC_BRAND_NAME` | Platform brand name | `GaadiLelo` |
| `NEXT_PUBLIC_BRAND_TAGLINE` | Brand tagline | `Buy Together. Save Together.` |
| `NEXT_PUBLIC_PILOT_CITY` | Primary pilot city | `Indore` |
| `NEXT_PUBLIC_DEMO_MODE` | Hide demo quick-login | `false` |

### Backend (`backend/.env` or Container Environment Variables)
| Variable | Description | Production Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres` |
| `SECRET_KEY` | 64-char random JWT secret | `[SECURE-RANDOM-SECRET]` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Session token lifetime | `1440` (24 hours) |
| `CORS_ORIGINS` | Permitted frontend origins | `https://gaadilelo.com,https://www.gaadilelo.com` |
| `SUPABASE_URL` | Optional Supabase project URL | `https://[REF].supabase.co` |
| `SUPABASE_ANON_KEY` | Optional Supabase anon key | `[ANON_KEY]` |

---

## 3. Database Initialization on Supabase / PostgreSQL

To apply all schema tables, run migrations in chronological order from `database/migrations/`:

```bash
# Apply initial tables (Users, Groups, Quotations, Vehicles)
psql "$DATABASE_URL" -f database/migrations/001_initial_schema.sql

# Apply vehicle intelligence & external sources
psql "$DATABASE_URL" -f database/migrations/002_vehicle_intelligence.sql

# Apply open dataset attribution & sync tables
psql "$DATABASE_URL" -f database/migrations/003_free_vehicle_data.sql

# Apply buyer intent affirmations and auth tokens
psql "$DATABASE_URL" -f database/migrations/004_buyer_intent_and_auth.sql
```

To seed the top 50 bestselling Indian vehicles:
```bash
python -m backend.app.seed.seed_top_50_cars
```

---

## 4. Local Development Startup

Start the backend:
```bash
cd /Users/hrishabh/Car_Buy_Group
backend/venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the frontend:
```bash
cd /Users/hrishabh/Car_Buy_Group/frontend
npm run dev
```

Visit: `http://localhost:3000`

---

## 5. Security & Verification Checklist

- [x] **No public demo buttons in production**: Gated behind `NEXT_PUBLIC_DEMO_MODE=false`.
- [x] **Real Authentication lifecycle**:
  - `/register`: Strict email/phone uniqueness, dealer GSTIN requirement.
  - `/login`: Bcrypt password verification and signed JWT issuance.
  - `/forgot-password`: Generates secure password reset tokens.
  - `/reset-password`: Validates token signature and expiration before updating password hash.
  - `/verify-email`: Self-service email confirmation.
- [x] **Dealer Verification Guard**: Dealerships in `PENDING` status are strictly forbidden (`403 Forbidden`) from submitting quotations until approved by an administrator.
- [x] **Buyer Intent Affirmations**: Every group creation and join action captures genuine purchase intent, non-binding understanding, and contact consent in the `buyer_intent_confirmations` audit table.
- [x] **Buyer PII Protection**: Full names, email addresses, and phone numbers are excluded from public group listings and member cohorts.
- [x] **Zero "Loading variants..." Locks**: Model selection populates variants instantaneously from the vehicle catalog with resilient baseline fallback.
- [x] **Styling Integrity**: All 29 routes compile cleanly with Tailwind CSS bundles; no raw unstyled layout.

