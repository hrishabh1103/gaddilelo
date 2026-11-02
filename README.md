# GaadiLelo.com — Vehicle Group-Buying Marketplace

> **"Buy Together. Save Together."**  
> Initial Pilot Market: **Indore, Madhya Pradesh, India** (Architected for National Expansion)

---

## 1. Product Overview

**GaadiLelo.com** is an Indian automotive group-buying marketplace engineered to democratize high-value vehicle purchases. By aggregating consumer and commercial demand into geographic cohorts, authorized OEM dealerships compete during scheduled bidding windows by submitting their best transparent on-road quotations.

Buyers compare competing offers side-by-side, inspect itemized statutory costs and verified discounts, and independently choose whether to accept and request a callback for direct showroom delivery.

### Supported Vehicle Categories:
- **Two-Wheelers:** Commuter & Performance Motorcycles, Scooters.
- **Electric Vehicles:** Electric Scooters (Ather, Ola), Electric Cars (Tata Nexon EV).
- **Passenger Cars:** Hatchbacks, Sedans, Compact & Mid-size SUVs (Tata Nexon, Maruti Brezza, Mahindra Scorpio-N).
- **Commercial Vehicles:** Pickups, Small Commercial Vehicles (Ashok Leyland Bada Dost), Trucks, Buses.
- **Three-Wheelers:** Passenger & Cargo Auto-rickshaws.

---

## 2. Core Architectural Highlights

1. **Modular Monolithic Architecture:** Clear domain service boundaries (`auth`, `catalog`, `groups`, `dealers`, `leads`, `pricing`, `admin`, `notifications`) without premature microservice complexity.
2. **Vehicle-Agnostic Pricing Engine:** Mathematical pricing formulation without hardcoded automobile assumptions. Handles configurable statutory TCS (1% > ₹10 Lakhs in India), state RTO slabs, comprehensive insurance, and strictly validates discounts to eliminate double-counting and negative dealer margins.
3. **Strict Buyer Privacy Shield:** Group members never see other buyers' PII (names, phone numbers, emails). Contact information is exclusively forwarded to an authorized dealer upon explicit, consent-based callback request.
4. **Transparent Revision History:** Dealerships can adjust quotations before bidding closures while archiving snapshot histories for auditability.
5. **Indore Pilot Ready:** Pre-seeded with authentic Indore dealerships (Sanghi Brothers Tata, Patel Motors Maruti Arena, Shreeji Mahindra) and high-demand Indian vehicle variants.

---

## 3. Technology Stack

- **Frontend:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Lucide React Icons.
- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2.0 (Async ORM), Pydantic v2, PyJWT, Bcrypt.
- **Database:** Supabase PostgreSQL / SQLAlchemy Async Engine (Dual-compatible with SQLite `aiosqlite` for instant zero-dependency local dev).
- **Security & RBAC:** Role-based authorization (`BUYER`, `DEALER`, `ADMIN`), Row-Level Security (RLS) SQL policies, password hashing, and audit trails.

---

## 4. Repository Structure

```
Car_Buy_Group/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoints: auth, catalog, groups, dealers, admin, leads, pricing
│   │   ├── core/            # Config, async database engine, security (bcrypt & JWT)
│   │   ├── models/          # SQLAlchemy ORM models (UUIDs, relationships, enums)
│   │   ├── schemas/         # Pydantic v2 request/response & validation schemas
│   │   ├── services/        # Pricing engine, group lifecycle engine, notification service
│   │   ├── seed/            # Python automated seed script for Indore pilot
│   │   └── main.py          # FastAPI application & lifespan setup
│   ├── tests/               # Pytest async test suite
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router (Landing, Catalog, Groups, Compare, Portals)
│   │   ├── components/      # Reusable UI, layout navigation, footer, demo switcher
│   │   ├── context/         # AuthContext (JWT session management, demo persona switcher)
│   │   ├── lib/             # API client with token injector
│   │   └── types/           # TypeScript interfaces matching backend models
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── database/
│   ├── migrations/
│   │   └── 001_initial_schema.sql  # Supabase PostgreSQL schema with RLS & indexes
│   └── seed/
│       └── seed_indore.sql          # Realistic Indore pilot SQL seed
├── docs/
│   ├── PRD.md                       # Comprehensive Product Requirements Document
│   ├── ARCHITECTURE.md              # System design, state machine, & sequence diagrams
│   ├── DATABASE.md                  # Relational schema specification & table definitions
│   └── API_SPECIFICATION.md         # RESTful API endpoint contract
├── infrastructure/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── .env.example
├── README.md
└── pytest.ini
```

---

## 5. Quick Start (Local Development)

### 5.1 Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ and npm

### 5.2 Backend Setup
```bash
# 1. Create and activate virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed realistic Indore pilot data (Indore dealerships, vehicles, active cohorts)
python3 -m backend.app.seed.seed_data

# 4. Run tests
PYTHONPATH=.. pytest ../backend/tests -v

# 5. Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### 5.3 Frontend Setup
```bash
# In a separate terminal:
cd frontend

# 1. Install dependencies
npm install

# 2. Run Next.js development server
npm run dev
```
Application will be live at: `http://localhost:3000`

---

## 6. Pre-Configured Demo Personas

For rapid testing and grading, 1-click persona switchers are built directly into the top navigation bar:

| Role | Name | Email | Password | Details |
|---|---|---|---|---|
| **Buyer** | Rahul Sharma | `rahul.sharma@gmail.com` | `Buyer@123` | Indore resident; member of Tata Nexon & Brezza cohorts |
| **Buyer 2** | Priya Verma | `priya.verma@gmail.com` | `Buyer@123` | Ather 450X EV cohort initiator |
| **Dealer** | Sanghi Brothers | `sales@sanghimotors.com` | `Dealer@123` | Authorized Tata Motors Dealership (AB Road, Indore) |
| **Dealer 2** | Patel Motors | `bids@patelmotors.com` | `Dealer@123` | Authorized Maruti Suzuki Arena (Vijay Nagar, Indore) |
| **Admin** | Platform Ops | `admin@gaadilelo.com` | `Admin@123` | Platform governance, verification & quotation moderation |

---

## 7. Key Workflows Tested & Functional

1. **Buyer Journey:**
   - Explore vehicles across Cars, EVs, 2W, 3W, and Commercial categories.
   - Start a buying group for a specific vehicle variant in Indore with target members.
   - Join existing buying groups (with automatic duplicate membership prevention).
   - Inspect competing dealer quotations side-by-side with itemized on-road breakdowns.
   - Request callback with explicit buyer consent.

2. **Dealership Journey:**
   - Receive group bidding invitations for authorized OEM brands.
   - Submit quotations via the vehicle-agnostic pricing engine.
   - Dynamically calculate statutory taxes, TCS, discounts, and final on-road price.
   - Revise quotations before bidding close while preserving previous revision logs.
   - Manage buyer callback leads and update pipeline status (`TEST_DRIVE_SCHEDULED` -> `PURCHASE_COMPLETED`).

3. **Admin Governance:**
   - Approve or reject dealership verification status with feedback.
   - Advance group lifecycle (`OPEN` -> `QUALIFYING` -> `READY_FOR_BIDDING` -> `BIDDING_OPEN` -> `OFFERS_AVAILABLE`).
   - Dispatch invitations to all verified dealerships in the pilot market.
   - Review and approve submitted quotations to publish them to buyers.
   - Inspect tamper-evident audit logs.

---

## 8. License

Proprietary — Developed for GaadiLelo.com Indore Pilot Expansion.
