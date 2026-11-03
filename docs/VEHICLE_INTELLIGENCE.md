# GaadiLelo Vehicle Intelligence & Automated Discovery Engine

## 1. Architectural Overview

The **Vehicle Intelligence & Automated Discovery Engine** transforms GaadiLelo.com into a self-updating, automotive-grade vehicle discovery platform. It mirrors the comprehensive catalog depth and specification rigor of CarDekho while directly feeding GaadiLelo's core group-buying and dealership bidding workflow.

```
                                  +---------------------------------------+
                                  |         Data Source Ingestion         |
                                  |  - OEM Official Press Feeds & APIs    |
                                  |  - Automotive News / RSS Feeds        |
                                  |  - Customer Zero-Search Discovery     |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |      Discovery & Ingestion Job        |
                                  | (VehicleDiscoveryJob & SourceRegistry)|
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       AI Extraction Pipeline          |
                                  |   - Spec Extraction (Variants, Fuel)  |
                                  |   - Offline Regex/Heuristic Fallback  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |        Normalization Engine           |
                                  |  - Prices: Lakh / Cr -> Decimal INR   |
                                  |  - Power: kW / BHP -> PS              |
                                  |  - Torque: lb-ft / kgm -> Nm          |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       Validation & Sanity Checks      |
                                  |   - Physical Plausibility Ranges      |
                                  |   - Anomaly & Conflict Detection      |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       Deduplication & Diffing         |
                                  |   - Token Match vs Existing Catalog   |
                                  |   - Price History & Update Auditing   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |     Admin Review & Moderation Queue   |
                                  |  (Status: PENDING_REVIEW / REJECTED)  |
                                  +-------------------+-------------------+
                                                      |
                                         (Admin 1-Click Approval)
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |      Live Catalogue Publication       |
                                  |  - Insert/Update Brand, Model, Variant|
                                  |  - Customer In-App Notification Sent  |
                                  |  - Available for Group Buying         |
                                  +---------------------------------------+
```

---

## 2. Core Service Modules (`backend/app/services/vehicle_intelligence/`)

| Module | Primary Responsibility |
| :--- | :--- |
| `source_registry.py` | Abstract `BaseSourceAdapter` pattern, pluggable OEM and news adapters, source health tracking, rate limiting, and last sync logging. |
| `extraction_service.py` | Extracts high-fidelity technical specs (powertrain, transmission, dimensions, boot space, battery capacity, range) with AI model and offline deterministic regex fallback. |
| `normalization_service.py` | Converts Indian market colloquialisms (e.g., `12.5 Lakh`, `1.45 Crore`) to standardized integers and standardizes physical engineering units. |
| `validation_service.py` | Enforces engineering plausibility (battery 5-250 kWh, mileage 5-150 km/l, engine 50-16000 cc) and cross-source conflict flags. |
| `deduplication_service.py` | Normalized tokenized comparison against existing `VehicleBrand`, `VehicleModel`, and `VehicleVariant` records in the database. |
| `update_service.py` | Tracks spec and price changes, logs `VehiclePriceHistory` and `VehicleUpdateHistory` snapshots. |
| `search_service.py` | Two-tier search returning existing catalog matches or triggering the zero-search customer discovery prompt. |
| `discovery_service.py` | Orchestration layer handling customer-triggered requests, scheduled background scans, admin approval with catalog publishing, and subscriber notifications. |

---

## 3. Customer-Triggered Zero-Search Discovery Workflow

1. **Buyer Searches**: A buyer visits `/vehicles` and searches for an uncatalogued vehicle (e.g. *"Mahindra BE 6e"* or *"Hyundai Creta EV"*).
2. **Zero Results & Prompt**: When 0 records match, the UI renders the discovery banner:
   > *"We couldn't find this vehicle in our catalogue. Let us discover it for you."*
3. **Buyer Submission**: The buyer enters the vehicle name, category, and optional notes/notification email.
4. **Instant Ingestion & AI Extraction**: The backend immediately registers a `VehicleDiscoveryRecord` (status: `PENDING_REVIEW`), extracts technical specs and variants from available sources or fallback parsers, and subscribes the user's ID/email.
5. **Admin Review & Publication**: The vehicle appears in the Admin Review Queue (`/admin/intelligence/review/[id]`). The administrator can inspect variants, citations, and images, and clicks **Approve & Publish**.
6. **Buyer Notification**: Once approved, the brand, model, and variants are created in the live catalog, and an in-app notification is automatically dispatched to the requesting buyer with a direct link to start a Group Buying cohort.

---

## 4. Multi-Category Automotive Support

The engine supports full Indian vehicle taxonomy:
- **Two-Wheelers**: Commuter Motorcycles, Premium Motorcycles, Electric Two-Wheelers (Ola, Ather, TVS iQube), Scooters.
- **Three-Wheelers**: Cargo, Passenger, and Electric Autos (Mahindra Treo, Bajaj RE, Piaggio Ape).
- **Passenger Vehicles**: Hatchbacks, Sedans, Compact & Midsize SUVs, Multi-Utility Vehicles (MUVs), Electric Cars (Tata EV, Mahindra EV, BYD).
- **Commercial Vehicles**: Small Commercial Vehicles (Tata Ace, Ashok Leyland Bada Dost), Light Trucks, Heavy Duty Haulers, and Buses.

---

## 5. Security & Verification Guarantee

- **Admin Governance**: No automated ingestion writes directly to the live buyer catalog without human admin verification.
- **Role Enforcement**: Discovery records can only be approved or rejected by users with `ADMIN` role.
- **Immutable Audit Trail**: All specification updates, price modifications, and approvals are permanently recorded in `VehiclePriceHistory` and `VehicleUpdateHistory`.

