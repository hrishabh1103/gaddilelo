# REST API Specification — GaadiLelo.com

Base URL: `/api/v1`

---

## 1. Authentication & Users (`/api/v1/auth`)

- `POST /auth/register`  
  Payload: `{ email, password, phone, full_name, role: 'BUYER' | 'DEALER', city_id, dealership_name?, gstin? }`  
  Response: `{ user: UserProfile, token: string }`

- `POST /auth/login`  
  Payload: `{ email, password }`  
  Response: `{ user: UserProfile, token: string }`

- `GET /auth/me`  
  Headers: `Authorization: Bearer <token>`  
  Response: `{ user: UserProfile, role, dealer_profile? }`

- `PUT /auth/profile`  
  Update personal preferences, city, phone, communication consent.

---

## 2. Geography & Vehicle Catalog (`/api/v1/catalog`)

- `GET /catalog/cities`  
  List active cities (e.g. Indore, MP).

- `GET /catalog/categories`  
  List all vehicle categories (Two-Wheelers, Three-Wheelers, Cars, EVs, Commercial Vehicles).

- `GET /catalog/brands?category_id={id}`  
  List OEMs (Tata, Maruti Suzuki, Hyundai, Mahindra, Ola Electric, TVS, etc.).

- `GET /catalog/models?brand_id={id}&category_id={id}&fuel_type={type}&transmission={type}&body_type={type}`  
  List models with active group counts.

- `GET /catalog/models/{id}`  
  Detailed model page with variants and available buying cohorts.

- `GET /catalog/variants/{id}`  
  Variant specifications and reference ex-showroom price.

---

## 3. Group Buying Engine (`/api/v1/groups`)

- `GET /groups`  
  Filter by city, category, brand, model, status. Returns active cohorts.

- `GET /groups/{id}`  
  Group details, current member count, progress milestone, purchase timeline, bidding status. (No buyer personal PII leaked).

- `POST /groups` (Buyer Role)  
  Create a new buying group for a specific vehicle variant and city.

- `POST /groups/{id}/join` (Buyer Role)  
  Join group. Validates user has not already joined. Increments member count.

- `POST /groups/{id}/leave` (Buyer Role)  
  Leave group before bidding starts. Decrements member count.

- `GET /groups/{id}/offers` (Buyer / Admin / Invited Dealer)  
  List approved quotations for this group with side-by-side breakdown.

---

## 4. Dealer Bidding & Quotations (`/api/v1/dealers`)

- `GET /dealers/dashboard` (Dealer Role)  
  Statistics: invitations received, active bidding, quotations submitted, buyer leads.

- `GET /dealers/invitations` (Dealer Role)  
  List groups the dealer is authorized to bid on.

- `POST /dealers/quotations` (Dealer Role)  
  Submit a new quotation for an invited group. Includes vehicle-agnostic line items and discounts.

- `PUT /dealers/quotations/{id}` (Dealer Role)  
  Revise quotation before deadline. Automatically archives previous revision snapshot.

- `GET /dealers/leads` (Dealer Role)  
  List buyer callback leads assigned to this dealer.

- `PUT /dealers/leads/{id}/status` (Dealer Role)  
  Update status (`CONTACTED`, `TEST_DRIVE_SCHEDULED`, `PURCHASE_COMPLETED`, etc.).

---

## 5. Buyer Lead & Callback Engine (`/api/v1/leads`)

- `POST /leads/request-callback` (Buyer Role)  
  Buyer selects a preferred dealership quotation and requests callback. Consents to share contact info with that specific dealer.

---

## 6. Administration & Governance (`/api/v1/admin`)

- `GET /admin/overview`  
  Platform analytics: buyers, verified dealers, active groups, bidding sessions, quotes submitted, conversion rate.

- `GET /admin/dealers`  
  List dealerships, inspect documents, review GSTIN.

- `PUT /admin/dealers/{id}/verify`  
  Approve or reject dealership verification status.

- `GET /admin/groups`  
  Manage all buying groups across the state/country.

- `PUT /admin/groups/{id}/status`  
  Transition status (`OPEN` -> `QUALIFYING` -> `READY_FOR_BIDDING` -> `BIDDING_OPEN` -> `OFFERS_AVAILABLE`).

- `POST /admin/groups/{id}/invite-dealers`  
  Invite verified OEM dealerships to participate in bidding.

- `GET /admin/quotations`  
  Review submitted quotations.

- `PUT /admin/quotations/{id}/approve`  
  Approve quotation to make it visible to buyers.

- `PUT /admin/quotations/{id}/reject`  
  Reject quotation with feedback for the dealer to rectify.

- `GET /admin/audit-logs`  
  View temporal system audit trail.

---

## 7. Notifications (`/api/v1/notifications`)

- `GET /notifications`  
  List in-app notifications for authenticated user.

- `PUT /notifications/{id}/read`  
  Mark notification as read.
