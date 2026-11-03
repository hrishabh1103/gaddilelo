import uuid
import json
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal

def run():
    con = sqlite3.connect('gaadilelo.db')
    cur = con.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    # Find Brands
    brands = {r[1].lower(): r[0] for r in cur.execute("SELECT id, name FROM vehicle_brands").fetchall()}
    honda_id = brands.get("honda")
    hyundai_id = brands.get("hyundai")
    kia_id = brands.get("kia")
    toyota_id = brands.get("toyota")
    maruti_id = brands.get("maruti suzuki") or brands.get("maruti")
    mahindra_id = brands.get("mahindra")
    tata_id = brands.get("tata motors") or brands.get("tata")

    print(f"Seeding flagship Indian vehicle variants into gaadilelo.db...")

    flagship_catalog = [
        # 1. HONDA ELEVATE
        {
            "brand_id": honda_id,
            "name": "Honda Elevate",
            "slug": "honda-elevate",
            "body_type": "Mid-size SUV",
            "image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800",
            "length_mm": 4312, "width_mm": 1790, "height_mm": 1650, "wheelbase_mm": 2650, "ground_clearance_mm": 220,
            "safety_rating_stars": 5, "safety_rating_agency": "BHARAT_NCAP",
            "variants": [
                {"name": "SV 1.5L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1169000, "engine": "1498 cc", "mileage": 15.31, "seating": 5, "specs": {"power": "121 PS", "airbags": 6, "led_projectors": True}},
                {"name": "V 1.5L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1241000, "engine": "1498 cc", "mileage": 15.31, "seating": 5, "specs": {"power": "121 PS", "touchscreen": "8 inch", "airbags": 6}},
                {"name": "V 1.5L i-VTEC CVT (Automatic)", "fuel": "PETROL", "trans": "CVT", "price": 1351000, "engine": "1498 cc", "mileage": 16.92, "seating": 5, "specs": {"power": "121 PS", "paddle_shifters": True, "airbags": 6}},
                {"name": "VX 1.5L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1380000, "engine": "1498 cc", "mileage": 15.31, "seating": 5, "specs": {"power": "121 PS", "single_pane_sunroof": True, "alloy_wheels": "17 inch", "airbags": 6}},
                {"name": "VX 1.5L i-VTEC CVT (Automatic)", "fuel": "PETROL", "trans": "CVT", "price": 1490000, "engine": "1498 cc", "mileage": 16.92, "seating": 5, "specs": {"power": "121 PS", "single_pane_sunroof": True, "airbags": 6}},
                {"name": "ZX 1.5L i-VTEC (Manual with ADAS)", "fuel": "PETROL", "trans": "MANUAL", "price": 1521000, "engine": "1498 cc", "mileage": 15.31, "seating": 5, "specs": {"power": "121 PS", "adas": "Honda Sensing", "leatherette_upholstery": True, "airbags": 6}},
                {"name": "ZX 1.5L i-VTEC CVT (Automatic with ADAS)", "fuel": "PETROL", "trans": "CVT", "price": 1631000, "engine": "1498 cc", "mileage": 16.92, "seating": 5, "specs": {"power": "121 PS", "adas": "Honda Sensing", "touchscreen": "10.25 inch", "airbags": 6}}
            ]
        },
        # 2. HONDA CITY
        {
            "brand_id": honda_id,
            "name": "Honda City",
            "slug": "honda-city-sedan",
            "body_type": "Sedan",
            "image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800",
            "length_mm": 4583, "width_mm": 1748, "height_mm": 1489, "wheelbase_mm": 2600, "ground_clearance_mm": 165,
            "safety_rating_stars": 5, "safety_rating_agency": "GLOBAL_NCAP",
            "variants": [
                {"name": "SV 1.5L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1208000, "engine": "1498 cc", "mileage": 17.8, "seating": 5, "specs": {"power": "121 PS", "airbags": 6}},
                {"name": "V 1.5L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1285000, "engine": "1498 cc", "mileage": 17.8, "seating": 5, "specs": {"power": "121 PS", "touchscreen": "8 inch", "airbags": 6}},
                {"name": "V 1.5L i-VTEC CVT (Automatic)", "fuel": "PETROL", "trans": "CVT", "price": 1410000, "engine": "1498 cc", "mileage": 18.4, "seating": 5, "specs": {"power": "121 PS", "airbags": 6}},
                {"name": "VX 1.5L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1397000, "engine": "1498 cc", "mileage": 17.8, "seating": 5, "specs": {"power": "121 PS", "sunroof": True, "airbags": 6}},
                {"name": "ZX 1.5L i-VTEC CVT (Automatic with Sunroof)", "fuel": "PETROL", "trans": "CVT", "price": 1635000, "engine": "1498 cc", "mileage": 18.4, "seating": 5, "specs": {"power": "121 PS", "sunroof": True, "adas": "Honda Sensing", "airbags": 6}},
                {"name": "e:HEV ZX Strong Hybrid (e-CVT)", "fuel": "HYBRID", "trans": "AUTOMATIC", "price": 2055000, "engine": "1498 cc + Dual Motors", "mileage": 27.13, "seating": 5, "specs": {"power": "126 PS Combined", "torque": "253 Nm", "pure_ev_mode": True, "airbags": 6}}
            ]
        },
        # 3. HONDA AMAZE
        {
            "brand_id": honda_id,
            "name": "Honda Amaze",
            "slug": "honda-amaze",
            "body_type": "Compact Sedan",
            "image_url": "https://static-cdn.cars24.com/prod/auto-news24-cms/Newsroom/2024/12/04/78362c74-5144-4fc6-b854-b796ec76ecb8-mew-2025-honda-amaze-red-front-design-ashish.webp?w=356&dpr=2.625&optimize=low&format=auto&quality=50",
            "length_mm": 3995, "width_mm": 1695, "height_mm": 1501, "wheelbase_mm": 2470, "ground_clearance_mm": 170,
            "safety_rating_stars": 4, "safety_rating_agency": "GLOBAL_NCAP",
            "variants": [
                {"name": "E 1.2L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 720000, "engine": "1199 cc", "mileage": 18.6, "seating": 5, "specs": {"power": "90 PS", "airbags": 2}},
                {"name": "S 1.2L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 797000, "engine": "1199 cc", "mileage": 18.6, "seating": 5, "specs": {"power": "90 PS", "steering_controls": True, "airbags": 2}},
                {"name": "S 1.2L i-VTEC CVT (Automatic)", "fuel": "PETROL", "trans": "CVT", "price": 887000, "engine": "1199 cc", "mileage": 18.3, "seating": 5, "specs": {"power": "90 PS", "paddle_shifters": True, "airbags": 2}},
                {"name": "VX 1.2L i-VTEC (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 904000, "engine": "1199 cc", "mileage": 18.6, "seating": 5, "specs": {"power": "90 PS", "touchscreen": "7 inch", "alloy_wheels": True, "airbags": 2}},
                {"name": "VX 1.2L i-VTEC CVT (Automatic)", "fuel": "PETROL", "trans": "CVT", "price": 996000, "engine": "1199 cc", "mileage": 18.3, "seating": 5, "specs": {"power": "90 PS", "touchscreen": "7 inch", "alloy_wheels": True, "airbags": 2}}
            ]
        },
        # 4. HYUNDAI CRETA
        {
            "brand_id": hyundai_id,
            "name": "Hyundai Creta",
            "slug": "hyundai-creta-suv",
            "body_type": "Mid-size SUV",
            "image_url": "https://images.timesdrive.in/photo/msid-151135855,thumbsize-2028145/151135855.jpg",
            "length_mm": 4330, "width_mm": 1790, "height_mm": 1635, "wheelbase_mm": 2610, "ground_clearance_mm": 190,
            "safety_rating_stars": 5, "safety_rating_agency": "BHARAT_NCAP",
            "variants": [
                {"name": "E 1.5L MPi Petrol (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1099900, "engine": "1497 cc", "mileage": 17.4, "seating": 5, "specs": {"power": "115 PS", "airbags": 6}},
                {"name": "EX 1.5L MPi Petrol (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1221000, "engine": "1497 cc", "mileage": 17.4, "seating": 5, "specs": {"power": "115 PS", "touchscreen": "8 inch", "airbags": 6}},
                {"name": "S(O) 1.5L MPi Petrol (Manual)", "fuel": "PETROL", "trans": "MANUAL", "price": 1436000, "engine": "1497 cc", "mileage": 17.4, "seating": 5, "specs": {"power": "115 PS", "panoramic_sunroof": True, "airbags": 6}},
                {"name": "SX Tech 1.5L CRDi Diesel (Automatic)", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 1789000, "engine": "1493 cc", "mileage": 19.1, "seating": 5, "specs": {"power": "116 PS", "adas_level_2": True, "airbags": 6}},
                {"name": "SX(O) 1.5L Turbo Petrol DCT", "fuel": "PETROL", "trans": "DCT", "price": 2000000, "engine": "1482 cc Turbo", "mileage": 18.4, "seating": 5, "specs": {"power": "160 PS", "panoramic_sunroof": True, "bose_audio": True, "airbags": 6}}
            ]
        },
        # 5. KIA SELTOS
        {
            "brand_id": kia_id,
            "name": "Kia Seltos",
            "slug": "kia-seltos",
            "body_type": "Mid-size SUV",
            "image_url": "https://hips.hearstapps.com/hmg-prod/images/526856bc-657b-43f6-ac32-644a22dd19ec.jpg?crop=0.771xw:0.650xh;0.101xw,0.217xh&resize=1200:*",
            "length_mm": 4365, "width_mm": 1800, "height_mm": 1645, "wheelbase_mm": 2610, "ground_clearance_mm": 190,
            "safety_rating_stars": 5, "safety_rating_agency": "BHARAT_NCAP",
            "variants": [
                {"name": "HTE 1.5L Smartstream Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1090000, "engine": "1497 cc", "mileage": 17.0, "seating": 5, "specs": {"power": "115 PS", "airbags": 6}},
                {"name": "HTK Plus 1.5L Smartstream Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1360000, "engine": "1497 cc", "mileage": 17.0, "seating": 5, "specs": {"power": "115 PS", "panoramic_sunroof": True, "airbags": 6}},
                {"name": "HTX 1.5L Smartstream Petrol IVT", "fuel": "PETROL", "trans": "CVT", "price": 1670000, "engine": "1497 cc", "mileage": 17.7, "seating": 5, "specs": {"power": "115 PS", "panoramic_sunroof": True, "airbags": 6}},
                {"name": "GTX Plus 1.5L Turbo Petrol DCT", "fuel": "PETROL", "trans": "DCT", "price": 1940000, "engine": "1482 cc Turbo", "mileage": 17.9, "seating": 5, "specs": {"power": "160 PS", "adas_level_2": True, "airbags": 6}}
            ]
        },
        # 6. TOYOTA URBAN CRUISER HYRYDER
        {
            "brand_id": toyota_id,
            "name": "Toyota Urban Cruiser Hyryder",
            "slug": "toyota-hyryder",
            "body_type": "Mid-size SUV",
            "image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800",
            "length_mm": 4365, "width_mm": 1795, "height_mm": 1645, "wheelbase_mm": 2600, "ground_clearance_mm": 210,
            "safety_rating_stars": 5, "safety_rating_agency": "BHARAT_NCAP",
            "variants": [
                {"name": "E 1.5L NeoDrive MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1114000, "engine": "1462 cc", "mileage": 21.12, "seating": 5, "specs": {"power": "103 PS", "airbags": 2}},
                {"name": "G 1.5L NeoDrive AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1569000, "engine": "1462 cc", "mileage": 20.58, "seating": 5, "specs": {"power": "103 PS", "sunroof": True, "airbags": 6}},
                {"name": "V 1.5L Strong Hybrid e-CVT", "fuel": "HYBRID", "trans": "AUTOMATIC", "price": 2019000, "engine": "1490 cc Hybrid", "mileage": 27.97, "seating": 5, "specs": {"power": "116 PS Combined", "panoramic_sunroof": True, "heads_up_display": True, "airbags": 6}}
            ]
        }
    ]

    for item in flagship_catalog:
        b_id = item["brand_id"]
        if not b_id:
            continue

        # Check if model already exists (by name or slug)
        m_row = cur.execute(
            "SELECT id FROM vehicle_models WHERE brand_id = ? AND (LOWER(name) = ? OR slug = ?)",
            (b_id, item["name"].lower(), item["slug"])
        ).fetchone()

        if m_row:
            m_id = m_row[0]
            # Update metadata
            cur.execute("""
                UPDATE vehicle_models SET 
                    length_mm = ?, width_mm = ?, height_mm = ?, wheelbase_mm = ?, ground_clearance_mm = ?,
                    safety_rating_stars = ?, safety_rating_agency = ?, last_verified_at = ?
                WHERE id = ?
            """, (item.get("length_mm"), item.get("width_mm"), item.get("height_mm"), item.get("wheelbase_mm"), item.get("ground_clearance_mm"), item.get("safety_rating_stars"), item.get("safety_rating_agency"), now_str, m_id))
        else:
            m_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO vehicle_models (
                    id, brand_id, name, slug, body_type, image_url, is_active, created_at,
                    length_mm, width_mm, height_mm, wheelbase_mm, ground_clearance_mm,
                    safety_rating_stars, safety_rating_agency, last_verified_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m_id, b_id, item["name"], item["slug"], item["body_type"], item["image_url"], now_str,
                item.get("length_mm"), item.get("width_mm"), item.get("height_mm"), item.get("wheelbase_mm"), item.get("ground_clearance_mm"),
                item.get("safety_rating_stars"), item.get("safety_rating_agency"), now_str
            ))

        # Also link "City" in existing database if name was just "City"
        if item["name"] == "Honda City":
            existing_city = cur.execute("SELECT id FROM vehicle_models WHERE brand_id = ? AND name = 'City'", (b_id,)).fetchone()
            if existing_city:
                m_id = existing_city[0]

        # Insert / update variants
        for v in item["variants"]:
            v_row = cur.execute("SELECT id FROM vehicle_variants WHERE model_id = ? AND name = ?", (m_id, v["name"])).fetchone()
            if not v_row:
                v_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO vehicle_variants (
                        id, model_id, name, fuel_type, transmission, seating_capacity,
                        engine_cc_or_battery_kwh, reference_ex_showroom, specifications,
                        claimed_mileage_kmpl, source_priority, is_active, created_at, last_verified_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
                """, (
                    v_id, m_id, v["name"], v["fuel"], v["trans"], v.get("seating", 5),
                    v.get("engine"), v["price"], json.dumps(v.get("specs", {})),
                    v.get("mileage"), now_str, now_str
                ))

        print(f"  [OK] {item['name']} verified with {len(item['variants'])} variants.")

    con.commit()
    con.close()
    print("Flagship Indian catalog successfully seeded!")

if __name__ == "__main__":
    run()

