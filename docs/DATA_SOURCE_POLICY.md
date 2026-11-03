# GaadiLelo Data Source & Legal Compliance Policy

## 1. Principles of Data Collection

GaadiLelo's Vehicle Intelligence Engine operates strictly under responsible, ethical, and legally compliant data acquisition standards.

### Core Commandments
1. **No Bypassing of Protections**: GaadiLelo never attempts to bypass CAPTCHAs, bot detections, Cloudflare/Akamai challenges, or paywalls.
2. **Strict Adherence to `robots.txt`**: All automated discovery adapters respect target robots exclusion standards. If a path is disallowed, no crawler requests are made to that path.
3. **Attribution & Provenance**: Every extracted specification, price, and image preserves clear provenance, storing:
   - Source URL
   - Retrieval timestamp
   - Source category (OEM Official, Press Release, Licensed Partner)
   - Extracted field citations (`VehicleSpecificationSource`)
4. **Prefer Licensed APIs and Official Press Portals**: Preference is given to official OEM press kits (e.g. Tata Motors Media, Mahindra Press Releases, Maruti Suzuki Press Room), RSS feeds, and authorized public sitemaps.

---

## 2. Supported Data Source Tiers

| Source Tier | Example Providers | Extraction Technique | Licensing / Policy |
| :--- | :--- | :--- | :--- |
| **Tier 1: OEM Media & Press Releases** | Tata Motors Media, Mahindra Pressroom, Maruti Suzuki Media | Structured Press Releases, Open Sitemaps, Public RSS | Permitted Public Domain News |
| **Tier 2: Commercial Automotive APIs** | Licensed Automotive Data Providers | Authenticated REST/GraphQL JSON APIs | Contractual Commercial License |
| **Tier 3: Manufacturer Spec Sheets** | OEM Official Brochures (PDF/HTML) | Direct PDF/Spec Sheet Parsing | Manufacturer Public Marketing Collateral |
| **Tier 4: Customer-Triggered On-Demand Discovery** | Individual Customer Requests | Targeted Search & Extraction | User-Assisted Catalog Enrichment |

---

## 3. Rate Limiting & Crawl Courtesy

To avoid placing undue load on partner or manufacturer systems:
- **Rate Limit**: Maximum 1 request per 3 seconds per host.
- **Concurrent Requests**: Fixed at 1 concurrent request per external domain.
- **Header Identification**: User-Agent headers explicitly identify the crawler:
  ```http
  User-Agent: GaadiLeloBot/1.0 (+https://gaadilelo.com/bot; bot@gaadilelo.com)
  ```
- **Exponential Backoff**: If an HTTP `429 Too Many Requests` or `503 Service Unavailable` is encountered, the adapter immediately backs off for `min(2^retry_count * 5, 120)` seconds.

---

## 4. Intellectual Property & Brand Rights

- **Trademarks & Badges**: All manufacturer logos, brand names (Tata, Mahindra, Maruti, Hyundai, Kia, Ather, etc.), and model badges remain the exclusive property of their respective trademark holders.
- **Catalog Purpose**: Vehicle images and specifications displayed on GaadiLelo are utilized solely for consumer vehicle comparison and authorized dealership group bidding aggregation.
- **Takedown & Correction Policy**: If an OEM or dealer notifies GaadiLelo of inaccurate technical specifications or requests content adjustment, the administrative console provides immediate correction and unpublishing capabilities at `/admin/intelligence/review/[id]`.

