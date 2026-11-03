# GaadiLelo Vehicle Discovery & Intelligence API Specification

Base Path: `/api/v1/intelligence`

All endpoints return JSON responses. Protected endpoints require a valid Supabase JWT Bearer token in the `Authorization` header (`Bearer <token>`).

---

## 1. Public & Buyer Endpoints

### 1.1 Two-Stage Vehicle Search
Returns matching catalog vehicles or signals that a vehicle is uncatalogued with a discovery trigger.

- **Method**: `GET /api/v1/intelligence/search`
- **Query Parameters**:
  - `query` (string, required): Search term (e.g., `"Mahindra BE 6e"`, `"Creta"`)
  - `category` (string, optional): Filter by vehicle category (`CARS`, `TWO_WHEELER`, etc.)
- **Response**:
```json
{
  "query": "Mahindra BE 6e",
  "category": "CARS",
  "catalog_matches": [],
  "needs_discovery": true,
  "discovery_prompt": "We couldn't find 'Mahindra BE 6e' in our catalogue. Let us discover it for you."
}
```

---

### 1.2 Customer Discovery Request
Triggers on-demand vehicle intelligence extraction and registers the user to receive an alert upon admin publication.

- **Method**: `POST /api/v1/intelligence/discovery-requests`
- **Authentication**: Optional (Guest or Authenticated Buyer)
- **Request Body**:
```json
{
  "vehicle_name": "Mahindra BE 6e",
  "category": "CARS",
  "notes": "Looking for 79kWh dual-motor battery pack variant in Indore",
  "contact_email": "buyer@example.com"
}
```
- **Response** (`201 Created`):
```json
{
  "id": "7b0a84d4-28b3-4fe6-b31f-0e8620df949b",
  "model_name": "BE 6e",
  "brand_name": "Mahindra",
  "category": "CARS",
  "status": "PENDING_REVIEW",
  "confidence_score": 0.88,
  "created_at": "2026-11-02T13:30:00Z"
}
```

---

## 2. Administrator Moderation & Queue Endpoints

All endpoints below require an authenticated user with `role: "ADMIN"`.

### 2.1 Overview Statistics
- **Method**: `GET /api/v1/intelligence/overview`
- **Response**:
```json
{
  "total_records": 12,
  "pending_review": 3,
  "approved_published": 8,
  "rejected": 1,
  "total_sources": 4,
  "active_sources": 4,
  "total_subscribers": 15
}
```

---

### 2.2 Discovery Queue
Lists discovered vehicle records with filtering by status and vehicle category.

- **Method**: `GET /api/v1/intelligence/queue`
- **Query Parameters**:
  - `status` (string, optional): `PENDING_REVIEW`, `APPROVED_PUBLISHED`, `REJECTED`, `IN_PROGRESS`
  - `category` (string, optional): Vehicle category
  - `limit` (int, default: 50)
  - `offset` (int, default: 0)

---

### 2.3 Record Detail Dossier
Retrieves the comprehensive vehicle dossier, including extracted variants, technical specifications, data citations, imagery, and subscriber count.

- **Method**: `GET /api/v1/intelligence/records/{id}`
- **Response**:
```json
{
  "id": "7b0a84d4-28b3-4fe6-b31f-0e8620df949b",
  "source_id": "...",
  "source_name": "Mahindra Official Press",
  "source_url": "https://www.mahindra.com/press-releases/be-6e-launch",
  "brand_name": "Mahindra",
  "model_name": "BE 6e",
  "category": "CARS",
  "body_type": "SUV",
  "status": "PENDING_REVIEW",
  "confidence_score": 0.95,
  "extracted_data": {
    "brand_name": "Mahindra",
    "model_name": "BE 6e",
    "category": "CARS",
    "body_type": "SUV",
    "min_price": 1890000,
    "max_price": 2690000,
    "description": "Born Electric SUV built on INGLO architecture...",
    "variants": [
      {
        "name": "Pack One (59 kWh)",
        "fuel_type": "ELECTRIC",
        "transmission": "AUTOMATIC",
        "ex_showroom_price": 1890000,
        "power_ps": 231,
        "torque_nm": 380,
        "battery_capacity_kwh": 59,
        "range_km": 550
      }
    ]
  },
  "subscriber_count": 2,
  "created_at": "2026-11-02T13:30:00Z"
}
```

---

### 2.4 Approve and Publish Record
Publishes the vehicle and its variants into the live catalog (`VehicleBrand`, `VehicleModel`, `VehicleVariant`) and dispatches in-app notifications to all subscribed buyers.

- **Method**: `POST /api/v1/intelligence/records/{id}/approve`
- **Request Body**:
```json
{
  "publish_to_catalog": true,
  "admin_notes": "Verified against Mahindra official launch spec sheet."
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Vehicle approved and published to catalogue",
  "record_id": "7b0a84d4-28b3-4fe6-b31f-0e8620df949b",
  "brand_id": "...",
  "model_id": "...",
  "variants_created": 2,
  "subscribers_notified": 2
}
```

---

### 2.5 Reject Record
Marks a discovery record as rejected with administrative reason notes.

- **Method**: `POST /api/v1/intelligence/records/{id}/reject`
- **Request Body**:
```json
{
  "reason": "Duplicate concept car, production model not yet scheduled."
}
```

---

### 2.6 Data Sources Management
- `GET /api/v1/intelligence/sources`: Lists configured data sources and health metrics.
- `POST /api/v1/intelligence/sources/{id}/sync`: Triggers an immediate ingestion sync for a specific source.
- `POST /api/v1/intelligence/scan-now`: Triggers a comprehensive background ingestion run across all active sources.

---

### 2.7 Specification & Price History Audit
- **Method**: `GET /api/v1/intelligence/history`
- **Query Parameters**:
  - `limit` (int, default: 50)
- **Response**: Array of price modifications and specification changes with timestamps and recorded reasons.

