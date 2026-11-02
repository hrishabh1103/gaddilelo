-- ====================================================================
-- GAADILELO.COM — Realistic Indore Pilot Seed SQL
-- File: seed_indore.sql
-- ====================================================================

-- 1. Cities
INSERT INTO cities (id, name, state, pincode_prefix, is_active) VALUES
('c0000000-0000-0000-0000-000000000001', 'Indore', 'Madhya Pradesh', '452', TRUE),
('c0000000-0000-0000-0000-000000000002', 'Bhopal', 'Madhya Pradesh', '462', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. Vehicle Categories
INSERT INTO vehicle_categories (id, slug, name, description, icon_name, display_order) VALUES
('cat00000-0000-0000-0000-000000000001', 'car', 'Passenger Cars', 'Hatchbacks, Sedans, Compact & Mid-size SUVs, MUVs', 'Car', 1),
('cat00000-0000-0000-0000-000000000002', 'electric-vehicle', 'Electric Vehicles', 'Electric Scooters, Electric Cars & Commercial EVs', 'Zap', 2),
('cat00000-0000-0000-0000-000000000003', 'two-wheeler', 'Two-Wheelers', 'Commuter & Premium Motorcycles and Scooters', 'Bike', 3),
('cat00000-0000-0000-0000-000000000004', 'commercial-vehicle', 'Commercial Vehicles', 'Pickups, Cargo 3W, Small Commercial Vehicles', 'Truck', 4),
('cat00000-0000-0000-0000-000000000005', 'three-wheeler', 'Three-Wheelers', 'Passenger & Cargo Auto-rickshaws', 'Boxes', 5)
ON CONFLICT (id) DO NOTHING;

-- 3. Vehicle Brands
INSERT INTO vehicle_brands (id, category_id, name, slug, logo_url) VALUES
('b0000000-0000-0000-0000-000000000001', 'cat00000-0000-0000-0000-000000000001', 'Tata Motors', 'tata-motors', 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=100'),
('b0000000-0000-0000-0000-000000000002', 'cat00000-0000-0000-0000-000000000001', 'Maruti Suzuki', 'maruti-suzuki', 'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=100'),
('b0000000-0000-0000-0000-000000000003', 'cat00000-0000-0000-0000-000000000001', 'Mahindra', 'mahindra', 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=100'),
('b0000000-0000-0000-0000-000000000004', 'cat00000-0000-0000-0000-000000000002', 'Ather Energy', 'ather-energy', 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=100'),
('b0000000-0000-0000-0000-000000000005', 'cat00000-0000-0000-0000-000000000004', 'Ashok Leyland', 'ashok-leyland', 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=100')
ON CONFLICT (id) DO NOTHING;

-- 4. Vehicle Models & Variants
INSERT INTO vehicle_models (id, brand_id, name, slug, body_type, image_url, is_active) VALUES
('m0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'Tata Nexon', 'tata-nexon', 'Compact SUV', 'https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=600&auto=format&fit=crop&q=80', TRUE),
('m0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000002', 'Maruti Suzuki Brezza', 'maruti-brezza', 'Compact SUV', 'https://images.unsplash.com/photo-1590362891991-f776e747a588?w=600&auto=format&fit=crop&q=80', TRUE),
('m0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000004', 'Ather 450X Gen 3', 'ather-450x', 'Electric Scooter', 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=600&auto=format&fit=crop&q=80', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO vehicle_variants (id, model_id, name, fuel_type, transmission, seating_capacity, engine_cc_or_battery_kwh, reference_ex_showroom, specifications, is_active) VALUES
('v0000000-0000-0000-0000-000000000001', 'm0000000-0000-0000-0000-000000000001', 'Creative Plus 1.2L Turbo Petrol', 'PETROL', 'MANUAL', 5, '1199 cc', 1169000.00, '{"mileage": "17.4 kmpl", "power": "120 PS", "airbags": 6}', TRUE),
('v0000000-0000-0000-0000-000000000002', 'm0000000-0000-0000-0000-000000000002', 'VXi 1.5L Smart Hybrid', 'PETROL', 'MANUAL', 5, '1462 cc', 969000.00, '{"mileage": "19.89 kmpl", "power": "103 PS"}', TRUE),
('v0000000-0000-0000-0000-000000000003', 'm0000000-0000-0000-0000-000000000003', '450X 3.7 kWh Pro Pack', 'ELECTRIC', 'SINGLE_SPEED_EV', 2, '3.7 kWh', 154999.00, '{"true_range": "110 km", "top_speed": "90 kmph"}', TRUE)
ON CONFLICT (id) DO NOTHING;
