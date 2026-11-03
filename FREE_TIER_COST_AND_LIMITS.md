# GaadiLelo.com — Free-Tier Cost Analysis & Provider Quota Limits

## Strict Budget Constraint: ₹0 / Month

This document audits all services selected for the GaadiLelo production pilot to ensure that **no costs will be incurred** and highlights operational limitations under free usage tiers.

---

## 1. Provider Cost & Quota Matrix

| Provider | Service | Plan | Monthly Cost | Free Quota | Over-Quota Risk | Risk Mitigation |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **Supabase** | Cloud PostgreSQL | Free | **₹0** | 500 MB database storage, 2 active projects, 50,000 monthly active users, 2 GB egress. | Project pauses after 7 days of inactivity. | Automated weekly health check query keeps project active. No credit card required. |
| **Render** | FastAPI Backend | Free Web Service | **₹0** | 750 instance hours/month, 512 MB RAM, 0.1 CPU core, shared IPv4/IPv6, auto SSL. | Spins down to sleep after 15 min idle. 100 GB outbound bandwidth limit. | Cold starts take ~45s. Free tier does NOT auto-charge; requests simply queue or error if quota exhausted. |
| **Vercel** | Next.js Frontend | Hobby (Personal) | **₹0** | 100 GB bandwidth, unlimited deployments, serverless functions (100 GB-hrs), auto SSL. | Strict non-commercial hobby guidelines; overage notifications sent via email. | Cloudflare Pages available as instant $0 alternative if commercial classification is needed. |
| **Resend** | Transactional Email | Free | **₹0** | 3,000 emails/month, 100 emails/day, 1 custom domain. | Sending blocked after 100 emails/day (no overage charges). | Rate limiter prevents registration abuse. 100 emails/day is sufficient for pilot cohorts. |
| **Upstash** | Redis Rate Limiting | Free | **₹0** | 10,000 requests/day, 256 MB memory, 1 concurrent database. | Commands rejected (HTTP 429) once 10,000/day exceeded. | Application includes in-memory sliding window fallback if Redis is unconfigured or unreachable. |

---

## 2. Inactivity & Sleep Behaviors

### 2.1 Render Free Web Service
- **Idle Timeout**: After 15 minutes of zero incoming HTTP requests, the instance spins down to zero.
- **Spin-Up Delay**: The first incoming request takes 35–50 seconds to boot the container, load Python packages, and connect to Supabase. Subsequent requests respond in < 150 ms.
- **Mitigation for Pilot**: Inform test users of the brief initial wake-up delay, or set up a free scheduled ping (e.g. Cron-Job.org / UptimeRobot) targeting `/health` during pilot testing hours (9 AM – 9 PM IST).

### 2.2 Supabase PostgreSQL
- **Pause Policy**: Projects on the Free tier that receive no database queries for 7 consecutive days are paused.
- **Recovery**: Paused projects can be unpaused with one click in the Supabase dashboard with zero data loss.
- **Mitigation**: Normal app traffic or a daily health check prevents pausing entirely.

---

## 3. Potential Billing Traps to Avoid

1. **Never Add a Credit Card for Automatic Upgrades**: Ensure all cloud accounts are kept on standard Free / Hobby tiers without pay-as-you-go enabled.
2. **Do Not Purchase a Custom Domain Immediately**: Use provider-assigned URLs during the pilot phase:
   - Frontend: `https://gaadilelo.vercel.app` (or `.pages.dev`)
   - Backend: `https://gaadilelo-api.onrender.com`
3. **Storage & Bandwidth Caps**:
   - The application does not store binary vehicle images in database tables; it references secure external URLs (`imgd.aeplcdn.com`, `unsplash.com`). This ensures database storage remains well below 20 MB out of the 500 MB limit.

