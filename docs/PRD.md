# Product Requirements Document (PRD) — GaadiLelo.com

**Working Brand Name:** GaadiLelo  
**Tagline:** Buy Together. Save Together.  
**Pilot Market:** Indore, Madhya Pradesh, India (designed for national expansion).  

---

## 1. Executive Summary

GaadiLelo.com is an Indian automotive group-buying marketplace designed to democratize high-value vehicle acquisition. In India's traditional dealership landscape, individual buyers lack negotiating leverage against dealership standard retail margins, mandatory add-ons, and non-transparent accessory pack pricing. 

GaadiLelo shifts market dynamics by pooling demand for specific vehicle models/variants within designated geographic territories (starting with Indore, MP). Once buyer cohorts reach target milestones and undergo qualification, authorized OEM dealerships are invited into competitive, controlled bidding sessions to offer verified transparent quotations.

---

## 2. Target Audience & Personas

### 2.1 The Buyer
- **Consumer Buyers:** Urban and semi-urban Indian commuters, families, and enthusiasts purchasing 2-wheelers (scooters/motorcycles, ICE or EV) and 4-wheelers (hatchbacks, sedans, SUVs, EVs).
- **Commercial Buyers:** Small business owners, fleet operators, logistics companies purchasing light commercial vehicles (LCVs), 3-wheelers, pickup trucks, or buses.
- **Pain Points:** Lack of bargaining leverage, opaque on-road pricing formulas, dealership markups on handling/logistics charges, exhausting negotiations across multiple physical dealerships.

### 2.2 The Authorized Dealership
- **OEM Franchised Dealerships:** Authorized sales partners of brands like Tata, Maruti Suzuki, Mahindra, Hyundai, Honda, TVS, Bajaj, Ola, Ather, Ashok Leyland, etc.
- **Value Proposition:** Bulk inventory turnaround, reduced customer acquisition cost (CAC), pre-qualified high-intent buyer pools, predictable monthly volume delivery.

### 2.3 Platform Administrators
- **Operations & Moderation Team:** Verifies dealership legitimacy (GSTIN, OEM franchise agreement), approves and moderates buying groups, controls bidding schedules, reviews quotations to guarantee zero fraudulent hidden fees, and oversees end-to-end buyer conversions.

---

## 3. Supported Vehicle Spectrum

GaadiLelo is built with a strictly **vehicle-agnostic engine** supporting:
1. **Two-Wheelers:** Motorcycles, Scooters, Electric Scooters, Electric Motorcycles.
2. **Three-Wheelers:** Passenger Auto-rickshaws, Electric 3-Wheelers (L3/L5), Cargo 3-Wheelers.
3. **Four-Wheelers:** Hatchbacks, Sedans, Compact SUVs, Mid/Full-size SUVs, Multi-Utility Vehicles (MUVs), Electric Passenger Vehicles.
4. **Commercial & Heavy Vehicles:** Small Commercial Vehicles (SCVs), Pickups, Cargo Vans, Light/Medium/Heavy Trucks, Commercial Buses.

---

## 4. Core Features & Capabilities

### 4.1 Buyer Experience
- **Location & Category Discovery:** Multi-tiered search filtering by city (Indore initial pilot), vehicle category, brand, model, fuel type (Petrol, Diesel, CNG, Electric, Hybrid), and transmission (Manual, AMT, Automatic).
- **Group Joining & Initiation:** Buyers can explore active local cohorts or start a new group by specifying category, brand, model, variant, timeline, and target cohort size.
- **Privacy Assurance:** Group members never see other buyers' PII (names, contact numbers, emails). Only aggregated cohort statistics are visible.
- **Transparent Quotation Comparison:** Side-by-side transparent price component comparisons (Ex-showroom, RTO/Registration, Road Tax, Insurance, TCS, Manufacturer Discount, Dealer Discount, Exchange Bonus, Corporate Offer, Mandatory vs Optional Accessories, Fastag/Logistics).
- **Dealer Callback Request:** Expressing direct purchase intent triggers a consent-based lead for the chosen dealer.

### 4.2 Dealer Experience
- **Dealership Onboarding:** Registration with business details, dealership name, authorized OEM brands, GSTIN, and verification document upload.
- **Invitation & Bidding Center:** View exclusive invitations to high-intent buyer groups in their authorized geographic zone.
- **Structured Quotation Engine:** Break down comprehensive line items accurately without arbitrary lumpsum quotes.
- **Controlled Revisions:** Update quotes before bidding deadline while preserving complete revision audit trails.
- **Enquiry Pipeline:** Manage qualified leads that opted for callbacks, log progress, and record vehicle delivery confirmations.

### 4.3 Administrator Dashboard
- **Verification Workflow:** Review dealer credentials and approve/reject with feedback.
- **Group Moderation Lifecycle:** Advance groups from `DRAFT` to `OPEN`, `QUALIFYING`, `READY_FOR_BIDDING`, `BIDDING_OPEN`, and `OFFERS_AVAILABLE`.
- **Targeted Dealer Invitations:** Direct specific OEM-authorized dealers to relevant vehicle groups.
- **Quotation Audit & Sanity Check:** Verify discounts, check against MSRP/ex-showroom guidelines, and approve quotations before publishing to buyers.
- **Analytics & Platform Health:** Cohort velocity, quotation competitiveness, buyer conversion metrics, and system audit logs.

---

## 5. Non-Functional Requirements

- **Security & Privacy:** Enforce strict RBAC at API level, parameterized queries via SQLAlchemy ORM, hashed passwords (bcrypt), and encrypted tokens.
- **Scalability:** Monolithic architecture with separated domain services, stateless backend, async database operations, and CDN-ready Next.js frontend.
- **Configurability:** Fully parametric branding (`BRAND_NAME`, `BRAND_TAGLINE`), tax regimes (GST, RTO slabs, TCS rules), and pilot market locations.
