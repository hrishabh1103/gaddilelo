-- ====================================================================
-- GAADILELO.COM — Realistic Indore Pilot Seed SQL (Catalog Only)
-- File: database/seed/seed_indore.sql
-- Description: Clean, idempotent seed data with valid RFC 4122 UUIDs.
--              No test accounts, dummy groups, or fake bids.
-- ====================================================================

-- 1. CITIES (Indore pilot territory & Bhopal hub)
INSERT INTO cities (id, name, state, pincode_prefix, is_active) VALUES
('c0000000-0000-4000-8000-000000000001', 'Indore', 'Madhya Pradesh', '452', TRUE),
('c0000000-0000-4000-8000-000000000002', 'Bhopal', 'Madhya Pradesh', '462', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. VEHICLE CATEGORIES
INSERT INTO vehicle_categories (id, slug, name, description, icon_name, display_order) VALUES
('ca000000-0000-4000-8000-000000000001', 'car', 'Passenger Cars', 'Hatchbacks, Sedans, Compact & Mid-size SUVs, MUVs', 'Car', 1),
('ca000000-0000-4000-8000-000000000002', 'electric-vehicle', 'Electric Vehicles', 'Electric Scooters, Electric Cars & Commercial EVs', 'Zap', 2),
('ca000000-0000-4000-8000-000000000003', 'two-wheeler', 'Two-Wheelers', 'Commuter & Premium Motorcycles and Scooters', 'Bike', 3),
('ca000000-0000-4000-8000-000000000004', 'commercial-vehicle', 'Commercial Vehicles', 'Pickups, Cargo 3W, Small Commercial Vehicles', 'Truck', 4),
('ca000000-0000-4000-8000-000000000005', 'three-wheeler', 'Three-Wheelers', 'Passenger & Cargo Auto-rickshaws', 'Boxes', 5)
ON CONFLICT (id) DO NOTHING;

-- 3. VEHICLE BRANDS
INSERT INTO vehicle_brands (id, category_id, name, slug, logo_url) VALUES
('b0000000-0000-4000-8000-000000000001', 'ca000000-0000-4000-8000-000000000001', 'Tata Motors', 'tata-motors', 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=100'),
('b0000000-0000-4000-8000-000000000002', 'ca000000-0000-4000-8000-000000000001', 'Maruti Suzuki', 'maruti-suzuki', 'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=100'),
('b0000000-0000-4000-8000-000000000003', 'ca000000-0000-4000-8000-000000000001', 'Mahindra', 'mahindra', 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=100'),
('b0000000-0000-4000-8000-000000000004', 'ca000000-0000-4000-8000-000000000001', 'Hyundai', 'hyundai', 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=100'),
('b0000000-0000-4000-8000-000000000005', 'ca000000-0000-4000-8000-000000000001', 'Honda', 'honda', 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=100'),
('b0000000-0000-4000-8000-000000000006', 'ca000000-0000-4000-8000-000000000001', 'Kia', 'kia', 'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=100'),
('b0000000-0000-4000-8000-000000000007', 'ca000000-0000-4000-8000-000000000001', 'Toyota', 'toyota', 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=100'),
('b0000000-0000-4000-8000-000000000008', 'ca000000-0000-4000-8000-000000000002', 'Ather Energy', 'ather-energy', 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=100'),
('b0000000-0000-4000-8000-000000000009', 'ca000000-0000-4000-8000-000000000002', 'Ola Electric', 'ola-electric', 'https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=100'),
('b0000000-0000-4000-8000-000000000010', 'ca000000-0000-4000-8000-000000000003', 'TVS Motor', 'tvs-motor', 'https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=100'),
('b0000000-0000-4000-8000-000000000011', 'ca000000-0000-4000-8000-000000000003', 'Royal Enfield', 'royal-enfield', 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=100'),
('b0000000-0000-4000-8000-000000000012', 'ca000000-0000-4000-8000-000000000004', 'Ashok Leyland', 'ashok-leyland', 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=100')
ON CONFLICT (id) DO NOTHING;

-- 4. VEHICLE MODELS
INSERT INTO vehicle_models (id, brand_id, name, slug, body_type, image_url, is_active) VALUES
-- Tata Models
('d0000000-0000-4000-8000-000000000001', 'b0000000-0000-4000-8000-000000000001', 'Tata Nexon', 'tata-nexon', 'Compact SUV', 'https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=600&auto=format&fit=crop&q=80', TRUE),
('d0000000-0000-4000-8000-000000000002', 'b0000000-0000-4000-8000-000000000001', 'Tata Punch', 'tata-punch', 'Micro SUV', 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600&auto=format&fit=crop&q=80', TRUE),
('d0000000-0000-4000-8000-000000000003', 'b0000000-0000-4000-8000-000000000001', 'Tata Safari', 'tata-safari', 'Flagship SUV', 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600&auto=format&fit=crop&q=80', TRUE),
-- Maruti Models
('d0000000-0000-4000-8000-000000000004', 'b0000000-0000-4000-8000-000000000002', 'Maruti Suzuki Brezza', 'maruti-brezza', 'Compact SUV', 'https://images.unsplash.com/photo-1590362891991-f776e747a588?w=600&auto=format&fit=crop&q=80', TRUE),
('d0000000-0000-4000-8000-000000000005', 'b0000000-0000-4000-8000-000000000002', 'Maruti Grand Vitara', 'maruti-grand-vitara', 'Mid-size SUV', 'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=600&auto=format&fit=crop&q=80', TRUE),
-- Mahindra Models
('d0000000-0000-4000-8000-000000000006', 'b0000000-0000-4000-8000-000000000003', 'Mahindra Scorpio-N', 'mahindra-scorpio-n', 'Mid-size SUV', 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600&auto=format&fit=crop&q=80', TRUE),
('d0000000-0000-4000-8000-000000000007', 'b0000000-0000-4000-8000-000000000003', 'Mahindra Thar', 'mahindra-thar', 'Lifestyle Off-Road SUV', 'https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=600&auto=format&fit=crop&q=80', TRUE),
('d0000000-0000-4000-8000-000000000008', 'b0000000-0000-4000-8000-000000000003', 'Mahindra XUV700', 'mahindra-xuv700', 'Premium SUV', 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600&auto=format&fit=crop&q=80', TRUE),
-- Hyundai Models
('d0000000-0000-4000-8000-000000000009', 'b0000000-0000-4000-8000-000000000004', 'Hyundai Creta', 'hyundai-creta', 'Mid-size SUV', 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=600&auto=format&fit=crop&q=80', TRUE),
-- Honda Models
('d0000000-0000-4000-8000-000000000010', 'b0000000-0000-4000-8000-000000000005', 'Honda Elevate', 'honda-elevate', 'Mid-size SUV', 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600&auto=format&fit=crop&q=80', TRUE),
-- Kia Models
('d0000000-0000-4000-8000-000000000011', 'b0000000-0000-4000-8000-000000000006', 'Kia Seltos', 'kia-seltos', 'Mid-size SUV', 'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=600&auto=format&fit=crop&q=80', TRUE),
-- Ather & Ola Models
('d0000000-0000-4000-8000-000000000012', 'b0000000-0000-4000-8000-000000000008', 'Ather 450X Gen 3', 'ather-450x', 'Electric Scooter', 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=600&auto=format&fit=crop&q=80', TRUE),
('d0000000-0000-4000-8000-000000000013', 'b0000000-0000-4000-8000-000000000009', 'Ola S1 Pro Gen 2', 'ola-s1-pro', 'Electric Scooter', 'https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=600&auto=format&fit=crop&q=80', TRUE),
-- Commercial Models
('d0000000-0000-4000-8000-000000000014', 'b0000000-0000-4000-8000-000000000012', 'Ashok Leyland Bada Dost i4', 'ashok-leyland-bada-dost', 'Small Commercial Vehicle', 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=600&auto=format&fit=crop&q=80', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 5. VEHICLE VARIANTS
INSERT INTO vehicle_variants (id, model_id, name, fuel_type, transmission, seating_capacity, engine_cc_or_battery_kwh, reference_ex_showroom, specifications, is_active) VALUES
-- Tata Nexon
('e0000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'Creative Plus 1.2L Turbo Petrol', 'PETROL', 'MANUAL', 5, '1199 cc', 1169000.00, '{"mileage": "17.4 kmpl", "power": "120 PS", "airbags": 6}', TRUE),
('e0000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000001', 'Fearless Plus S 1.5L Diesel DCA', 'DIESEL', 'AUTOMATIC', 5, '1497 cc', 1499000.00, '{"mileage": "23.2 kmpl", "power": "115 PS", "ventilated_seats": true}', TRUE),
-- Tata Punch
('e0000000-0000-4000-8000-000000000003', 'd0000000-0000-4000-8000-000000000002', 'Accomplished Dazzle 1.2L Petrol MT', 'PETROL', 'MANUAL', 5, '1199 cc', 825000.00, '{"mileage": "18.8 kmpl", "airbags": 2}', TRUE),
-- Maruti Brezza
('e0000000-0000-4000-8000-000000000004', 'd0000000-0000-4000-8000-000000000004', 'VXi 1.5L Smart Hybrid', 'PETROL', 'MANUAL', 5, '1462 cc', 969000.00, '{"mileage": "19.89 kmpl", "power": "103 PS"}', TRUE),
('e0000000-0000-4000-8000-000000000005', 'd0000000-0000-4000-8000-000000000004', 'ZXi Plus 1.5L AT', 'PETROL', 'AUTOMATIC', 5, '1462 cc', 1398000.00, '{"mileage": "19.8 kmpl", "sunroof": true}', TRUE),
-- Mahindra Scorpio-N & Thar
('e0000000-0000-4000-8000-000000000006', 'd0000000-0000-4000-8000-000000000006', 'Z8L 2.2L mHawk Diesel 4x4 AT', 'DIESEL', 'AUTOMATIC', 7, '2198 cc', 2454000.00, '{"power": "175 PS", "torque": "400 Nm", "sony_audio": "12 speakers"}', TRUE),
('e0000000-0000-4000-8000-000000000007', 'd0000000-0000-4000-8000-000000000007', 'LX 4x4 Hard Top 2.2L Diesel MT', 'DIESEL', 'MANUAL', 4, '2184 cc', 1575000.00, '{"power": "130 PS", "4x4_low_range": true}', TRUE),
-- Hyundai Creta
('e0000000-0000-4000-8000-000000000008', 'd0000000-0000-4000-8000-000000000009', 'SX(O) 1.5L Turbo Petrol DCT', 'PETROL', 'DCT', 5, '1482 cc', 1999000.00, '{"power": "160 PS", "panoramic_sunroof": true, "adas_level_2": true}', TRUE),
-- Honda Elevate
('e0000000-0000-4000-8000-000000000009', 'd0000000-0000-4000-8000-000000000010', 'ZX 1.5L i-VTEC CVT with ADAS', 'PETROL', 'CVT', 5, '1498 cc', 1631000.00, '{"power": "121 PS", "adas": "Honda Sensing"}', TRUE),
-- EV Two Wheelers
('e0000000-0000-4000-8000-000000000010', 'd0000000-0000-4000-8000-000000000012', '450X 3.7 kWh Pro Pack', 'ELECTRIC', 'SINGLE_SPEED_EV', 2, '3.7 kWh', 154999.00, '{"true_range": "110 km", "top_speed": "90 kmph"}', TRUE),
('e0000000-0000-4000-8000-000000000011', 'd0000000-0000-4000-8000-000000000013', 'S1 Pro 4 kWh (Gen 2)', 'ELECTRIC', 'SINGLE_SPEED_EV', 2, '4.0 kWh', 147499.00, '{"true_range": "180 km", "top_speed": "120 kmph"}', TRUE),
-- Commercial
('e0000000-0000-4000-8000-000000000012', 'd0000000-0000-4000-8000-000000000014', 'Bada Dost i4 High Deck 1.5L Diesel', 'DIESEL', 'MANUAL', 3, '1476 cc', 872000.00, '{"payload": "1825 kg", "power": "80 HP"}', TRUE)
ON CONFLICT (id) DO NOTHING;
