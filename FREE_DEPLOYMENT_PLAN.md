# GaadiLelo.com — Free-Tier Deployment Plan (₹0 Monthly Cost)

## 1. Executive Summary

GaadiLelo.com is designed as India's premier group vehicle-buying marketplace, piloted in Indore, Madhya Pradesh. This deployment plan specifies how the entire application stack is deployed to production using **strictly free-tier hosting services** with zero monthly fees ($0 / ₹0 per month), zero trial conversions, and zero reliance on local SQLite or mock email services.

---

## 2. Architecture & Provider Selection

| Layer | Provider | Free Tier Specification | Cost | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Database** | **Supabase** | Free Tier (PostgreSQL 15, 500 MB storage, 2 projects, IPv6/PgBouncer) | **₹0** | Persistent database storing buyers, dealers, groups, bids, intent audits, and revoked tokens. |
| **Backend API** | **Render** | Free Web Service (512 MB RAM, 0.1 CPU, 750 free instance hours/month) | **₹0** | FastAPI ASGI server (`app.main:app`), token verification, business logic, health checks. |
| **Frontend UI** | **Cloudflare Pages** / **Netlify** | Free Tier (Static/SSR, unlimited/generous bandwidth, complies with commercial terms) | **₹0** | Public landing page, vehicle catalogue, buyer/dealer/admin dashboards, intent flow. |
| **Email Service** | **Resend** | Free Tier (3,000 emails/month, 100 emails/day, SMTP & REST API) | **₹0** | Transactional verification emails and password reset links. |
| **Rate Limiter** | **Upstash Redis** | Free Tier (10,000 commands/day, 256 MB storage) *or in-memory sliding window fallback* | **₹0** | Distributed brute-force defense on `/login`, `/register`, `/forgot-password`, `/reset-password`. |
| **File Storage** | **Supabase Storage** | Free Tier (1 GB storage, 2 GB bandwidth) | **₹0** | Optional private bucket for dealer KYC documents (URLs currently referenced externally). |

---

## 3. Component Details & Build Specifications

### 3.1 Backend Service (FastAPI)
- **Repository Root**: `backend/`
- **Entrypoint**: `app.main:app`
- **Python Runtime**: Python 3.11 / 3.12 / 3.13
- **Dependencies**: Listed in `backend/requirements.txt` (includes `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `psycopg2-binary`, `redis`, `python-jose`, `passlib[bcrypt]`, `pydantic-settings`).
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health` (also aliased at `/api/v1/health`)
- **Key Guards Enforced in Production (`ENVIRONMENT=production`)**:
  - Rejects `sqlite://` database URLs; requires PostgreSQL.
  - Rejects mock email (`EMAIL_PROVIDER=mock` causes immediate shutdown).
  - Rejects default dev `SECRET_KEY`.
  - Hides raw password reset tokens and verification tokens from API responses.
  - Redacts sensitive credentials (passwords, bearer tokens, API keys) from server logs via `SensitiveDataRedactionFilter`.

### 3.2 Frontend Application (Next.js 15)
- **Repository Root**: `frontend/`
- **Framework**: Next.js 15.1 (App Router), React 19, Tailwind CSS.
- **Node Runtime**: Node.js 20.x LTS.
- **Build Command**: `npm run build`
- **Start Command**: `npm run start -p $PORT` (for container/Node hosting) or managed serverless via Vercel / Cloudflare Pages `@cloudflare/next-on-pages`.
- **API Communication**: Uses `NEXT_PUBLIC_API_URL` pointing to the deployed backend URL (e.g., `https://gaadilelo-backend.onrender.com/api/v1`).
- **Security & Mode Guards**:
  - `NEXT_PUBLIC_DEMO_MODE=false` hides the demo persona switcher banner.
  - Session tokens stored securely in `localStorage` and sent via `Authorization: Bearer <token>`.
  - Logout triggers server-side token invalidation via `POST /api/v1/auth/logout`.

---

## 4. Environment Variables Checklist

### 4.1 Backend Environment Variables (Render Dashboard)
| Variable | Description | Production Requirement |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Environment flag | Must be set to `production` |
| `SECRET_KEY` | JWT signing secret | 64-char cryptographically random hex string (`openssl rand -hex 32`) |
| `DATABASE_URL` | PostgreSQL connection URL | Supabase PostgreSQL Connection String (Session/Transaction pooler) |
| `FRONTEND_URL` | Public frontend URL | e.g. `https://gaadilelo.vercel.app` (used for CORS & email links) |
| `CORS_ORIGINS` | Allowed CORS origins | JSON list or comma-separated string containing frontend URL |
| `EMAIL_PROVIDER` | Transactional email provider | Set to `smtp` or `sendgrid` |
| `SMTP_HOST` | SMTP server host | `smtp.resend.com` (or `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | `resend` (or email address) |
| `SMTP_PASSWORD` | SMTP password / API Key | Resend API key (`re_...`) or Google App Password |
| `SMTP_FROM_EMAIL` | Sender email address | `onboarding@resend.dev` (or verified email) |
| `SMTP_USE_TLS` | SMTP TLS encryption | `true` |
| `REDIS_URL` | Redis connection URL (Optional) | Upstash Redis connection string (`rediss://...`) |
| `ENABLE_BACKGROUND_SCHEDULER`| Background cron worker | Set to `false` on web service to prevent sleep disruptions |

### 4.2 Frontend Environment Variables (Vercel / Cloudflare Dashboard)
| Variable | Description | Production Requirement |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_APP_URL` | Public site URL | e.g. `https://gaadilelo.vercel.app` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | e.g. `https://gaadilelo-backend.onrender.com/api/v1` |
| `NEXT_PUBLIC_PILOT_CITY` | Pilot city name | `Indore` |
| `NEXT_PUBLIC_BRAND_NAME` | Platform name | `GaadiLelo` |
| `NEXT_PUBLIC_BRAND_TAGLINE`| Platform tagline | `Buy Together. Save Together.` |
| `NEXT_PUBLIC_DEMO_MODE` | Demo mode switcher | Must be set to `false` |

---

## 5. Free-Tier Constraints & Mitigations

1. **Render Free Tier Spin-Down**:
   - *Behavior*: Free Web Services on Render automatically spin down to sleep after 15 minutes of inactivity. The first request after sleep experiences a 40–50 second cold start delay.
   - *Mitigation*: Public landing page and static vehicle catalogue can be cached or served via CDN; health check pings can keep it warm during peak hours if desired.
2. **Supabase Inactivity Pause**:
   - *Behavior*: Free-tier Supabase projects pause after 7 consecutive days of inactivity.
   - *Mitigation*: Any active database traffic from the app or a weekly check prevents pausing.
3. **Resend Sender Limitations**:
   - *Behavior*: Without a verified custom domain, Resend requires using `onboarding@resend.dev` and only delivers to the owner's registered account email.
   - *Mitigation*: For the free pilot testing phase, owner testing uses the registered email; adding a free Cloudflare DNS TXT record for a custom domain unlocks delivery to any buyer.

