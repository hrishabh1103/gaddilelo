# GaadiLelo.com — Deployment Runbook

This runbook provides the exact step-by-step procedures to deploy the GaadiLelo MVP to public free-tier hosting.

---

## Pre-Requisites & Security Rules
- **₹0 Cost**: Do not enter credit card details or enable auto-billing.
- **Credential Privacy**: Never paste raw database passwords, JWT secrets, or API keys into chat or git repositories.
- **Target Supabase Project**: `https://khgvmqfidpazfdjitkeb.supabase.co`

---

## Stage 1: Supabase Database Migration (Owner Action)

1. Open your [Supabase Project Dashboard](https://supabase.com/dashboard/project/khgvmqfidpazfdjitkeb).
2. Go to **Project Settings** -> **Database**.
3. Under **Connection string**, copy the **URI** connection string. It will look like:
   `postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?pgbouncer=true`
   *(Or direct port 5432: `postgresql://postgres:[YOUR-PASSWORD]@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres`)*
4. In your terminal, run the local validation first (zero database access):
   ```bash
   python scripts/run_migrations.py --validate
   ```
5. Test read-only connectivity to Supabase:
   ```bash
   DATABASE_URL="<PASTE_YOUR_SUPABASE_URI>" python scripts/run_migrations.py --check-connection
   ```
6. Run the read-only migration planner to inspect remote status:
   ```bash
   DATABASE_URL="<PASTE_YOUR_SUPABASE_URI>" python scripts/run_migrations.py --plan
   ```
7. When you are ready to execute the migrations:
   ```bash
   DATABASE_URL="<PASTE_YOUR_SUPABASE_URI>" python scripts/run_migrations.py --execute --confirm-live-migration
   ```
6. Verify in the Supabase Table Editor that all 31 tables (including `users`, `dealers`, `buying_groups`, `buyer_intent_confirmations`, `auth_tokens`, and `revoked_tokens`) are present.

---

## Stage 2: Deploy Backend to Render (Free Web Service)

1. Sign up / Log in to [Render.com](https://render.com) (Free Tier).
2. Click **New +** -> **Web Service**.
3. Connect your repository or choose **Public Git repository**.
4. Configure service settings:
   - **Name**: `gaadilelo-backend`
   - **Region**: Singapore or Frankfurt (choose nearest free region)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free` ($0/mo)
5. Add the **Environment Variables** in the Render Dashboard:
   - `ENVIRONMENT`: `production`
   - `SECRET_KEY`: *(Generate with `openssl rand -hex 32`)*
   - `DATABASE_URL`: *(Your Supabase PostgreSQL URI with asyncpg driver prefix: `postgresql+asyncpg://...` or standard `postgresql://...`)*
   - `FRONTEND_URL`: `https://<YOUR-FRONTEND-URL>.vercel.app`
   - `CORS_ORIGINS`: `["https://<YOUR-FRONTEND-URL>.vercel.app"]`
   - `EMAIL_PROVIDER`: `smtp`
   - `SMTP_HOST`: `smtp.resend.com`
   - `SMTP_PORT`: `587`
   - `SMTP_USER`: `resend`
   - `SMTP_PASSWORD`: `<YOUR-RESEND-API-KEY>`
   - `SMTP_FROM_EMAIL`: `onboarding@resend.dev`
   - `SMTP_USE_TLS`: `true`
   - `ENABLE_BACKGROUND_SCHEDULER`: `false`
6. Click **Create Web Service**. Wait for deployment to complete.
7. Verify the backend health endpoint:
   ```bash
   curl -I https://<YOUR-RENDER-APP>.onrender.com/health
   ```
   Should return `HTTP/1.1 200 OK` with `{"status": "ok", "environment": "production"}`.

---

## Stage 3: Deploy Frontend to Cloudflare Pages or Netlify (Free Tier)

*Note: Vercel Hobby strictly prohibits commercial websites; using it for GaadiLelo violates Vercel Terms of Service. Cloudflare Pages and Netlify Free both permit commercial projects on their free tiers.*

### Option A: Cloudflare Pages
1. Sign up / Log in to [Cloudflare](https://dash.cloudflare.com).
2. Go to **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git**.
3. Select your repository.
4. Configure build settings:
   - **Framework Preset**: `Next.js`
   - **Root directory**: `frontend`
   - **Build command**: `npx @cloudflare/next-on-pages` (or standard `npm run build`)
   - **Build output directory**: `.vercel/output/static` (or `.next`)
5. Add Environment Variables:
   - `NEXT_PUBLIC_APP_URL`: `https://<YOUR-PROJECT>.pages.dev`
   - `NEXT_PUBLIC_API_URL`: `https://<YOUR-RENDER-APP>.onrender.com/api/v1`
   - `NEXT_PUBLIC_PILOT_CITY`: `Indore`
   - `NEXT_PUBLIC_BRAND_NAME`: `GaadiLelo`
   - `NEXT_PUBLIC_BRAND_TAGLINE`: `Buy Together. Save Together.`
   - `NEXT_PUBLIC_DEMO_MODE`: `false`
6. Click **Save and Deploy**.

### Option B: Netlify Free
1. Sign up / Log in to [Netlify](https://app.netlify.com).
2. Click **Add new site** -> **Import an existing project**.
3. Configure settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next`
4. Set the exact same environment variables as above.
5. Deploy.

---

## Stage 4: End-to-End Verification Checklist

Perform these tests on the deployed application:
1. **Public Site**: Open `https://<YOUR-PROJECT>.vercel.app`. Verify that the demo persona switcher is completely hidden.
2. **Buyer Registration**: Register a new buyer account (`testbuyer@example.com`). Verify that the response does not expose verification tokens.
3. **Email Verification**: Check email for verification link and verify the account.
4. **Login & JWT**: Log in with verified credentials and receive the JWT token.
5. **Group Creation & Intent**: Browse Tata Nexon / Creta, initiate a group, check the buyer intent confirmation checkboxes, and confirm the group creation.
6. **Dealer KYC & Quotation**: Log in as a dealer, verify that only verified dealers can submit bids, and test quote comparison on the buyer dashboard.
7. **Logout & Invalidation**: Click Sign Out and verify that subsequent requests with the old JWT return `401 Unauthorized` (revoked token).

