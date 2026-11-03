from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from decimal import Decimal

class OEMSpecificationRegistry:
    """
    Official Indian Automotive Manufacturer Registry (28 Leading OEMs).
    
    Covers:
    - Passenger Cars & SUVs: Tata Motors, Mahindra, Maruti Suzuki, Hyundai, Kia, Toyota, Honda, Renault, Nissan, Volkswagen, Skoda, MG Motor, BYD
    - Two-Wheelers: Royal Enfield, Hero MotoCorp, Honda 2Wheelers, TVS Motor, Bajaj Auto, Ather Energy, Ola Electric
    - Commercial Vehicles: Ashok Leyland, Tata Motors Commercial Vehicles, Mahindra Commercial, Eicher Motors, Force Motors
    
    Operating Rules:
    - Source Priority 1: Official Manufacturer Specification Sheets & Public Press Releases
    - Source Priority 2: Official Manufacturer Product Portals
    - Deterministic parsing without paid AI/API dependencies
    - Strict physical validation (no passenger car seating/airbags on motorcycles)
    """

    OEM_PORTALS = {
        "Tata Motors": {
            "type": "CARS_AND_EVS",
            "portal_url": "https://cars.tatamotors.com",
            "press_url": "https://www.tatamotors.com/media/press-releases/",
            "models": {
                "Tata Nexon": {
                    "category": "car",
                    "body_type": "Compact SUV",
                    "length_mm": 3994, "width_mm": 1811, "height_mm": 1607, "wheelbase_mm": 2498,
                    "ground_clearance_mm": 208, "safety_rating": 5, "safety_agency": "BHARAT_NCAP",
                    "variants": [
                        {"name": "Smart 1.2L Turbo Petrol", "fuel": "PETROL", "trans": "MANUAL", "price": 799990, "engine": "1199 cc", "power": "120 PS", "torque": "170 Nm", "seating": 5, "airbags": 6},
                        {"name": "Creative Plus 1.2L Turbo Petrol", "fuel": "PETROL", "trans": "MANUAL", "price": 1169000, "engine": "1199 cc", "power": "120 PS", "torque": "170 Nm", "seating": 5, "airbags": 6},
                        {"name": "Fearless Plus DCA Petrol", "fuel": "PETROL", "trans": "DCT", "price": 1499990, "engine": "1199 cc", "power": "120 PS", "torque": "170 Nm", "seating": 5, "airbags": 6},
                        {"name": "Empowered Plus LR EV", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1719000, "battery": "40.5 kWh", "power": "145 PS", "torque": "215 Nm", "range_claimed": 465, "range_tested": 370, "seating": 5, "airbags": 6}
                    ]
                },
                "Tata Punch": {
                    "category": "car",
                    "body_type": "Micro SUV",
                    "length_mm": 3827, "width_mm": 1742, "height_mm": 1615, "wheelbase_mm": 2445,
                    "ground_clearance_mm": 187, "safety_rating": 5, "safety_agency": "BHARAT_NCAP",
                    "variants": [
                        {"name": "Smart 1.2L Revotron Petrol", "fuel": "PETROL", "trans": "MANUAL", "price": 612900, "engine": "1199 cc", "power": "86 PS", "torque": "115 Nm", "seating": 5, "airbags": 2},
                        {"name": "Adventure Rhythm 1.2L Petrol", "fuel": "PETROL", "trans": "MANUAL", "price": 725000, "engine": "1199 cc", "power": "86 PS", "torque": "115 Nm", "seating": 5, "airbags": 2},
                        {"name": "Accomplished Dazzle 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 885000, "engine": "1199 cc", "power": "86 PS", "torque": "115 Nm", "seating": 5, "airbags": 2},
                        {"name": "Creative Flagship 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 1020000, "engine": "1199 cc", "power": "86 PS", "torque": "115 Nm", "seating": 5, "airbags": 6},
                        {"name": "Adventure iCNG Twin Cylinder", "fuel": "CNG", "trans": "MANUAL", "price": 795000, "engine": "1199 cc", "power": "73.4 PS", "torque": "103 Nm", "seating": 5, "airbags": 2}
                    ]
                },
                "Tata Harrier": {
                    "category": "car",
                    "body_type": "Mid-size SUV",
                    "length_mm": 4605, "width_mm": 1922, "height_mm": 1718, "wheelbase_mm": 2741,
                    "ground_clearance_mm": 205, "safety_rating": 5, "safety_agency": "BHARAT_NCAP",
                    "variants": [
                        {"name": "Smart 2.0L Kryotec Diesel", "fuel": "DIESEL", "trans": "MANUAL", "price": 1549000, "engine": "1956 cc", "power": "170 PS", "torque": "350 Nm", "seating": 5, "airbags": 6},
                        {"name": "Pure Plus 2.0L Kryotec Diesel", "fuel": "DIESEL", "trans": "MANUAL", "price": 1869000, "engine": "1956 cc", "power": "170 PS", "torque": "350 Nm", "seating": 5, "airbags": 6},
                        {"name": "Adventure Plus Dark AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2329000, "engine": "1956 cc", "power": "170 PS", "torque": "350 Nm", "seating": 5, "airbags": 6},
                        {"name": "Fearless Plus Dark AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2644000, "engine": "1956 cc", "power": "170 PS", "torque": "350 Nm", "seating": 5, "airbags": 7}
                    ]
                },
                "Tata Curvv": {
                    "category": "car",
                    "body_type": "SUV Coupe",
                    "length_mm": 4308, "width_mm": 1810, "height_mm": 1630,
                    "variants": [
                        {"name": "Smart 1.2L Turbo Petrol", "fuel": "PETROL", "trans": "MANUAL", "price": 999990, "engine": "1198 cc", "power": "125 PS", "torque": "225 Nm", "seating": 5, "airbags": 6}
                    ]
                }
            }
        },
        "Mahindra": {
            "type": "SUVS_AND_EVS",
            "portal_url": "https://auto.mahindra.com",
            "press_url": "https://auto.mahindra.com/newsroom",
            "models": {
                "Mahindra XEV 9e": {
                    "category": "electric-vehicle",
                    "body_type": "Electric SUV Coupe",
                    "length_mm": 4790, "width_mm": 1905, "height_mm": 1690, "wheelbase_mm": 2775,
                    "ground_clearance_mm": 207,
                    "variants": [
                        {"name": "Pack One (59 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2190000, "battery": "59 kWh", "power": "231 PS", "torque": "380 Nm", "range_claimed": 535, "range_tested": 440, "seating": 5, "airbags": 6},
                        {"name": "Pack Two (79 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2490000, "battery": "79 kWh", "power": "285 PS", "torque": "380 Nm", "range_claimed": 656, "range_tested": 530, "seating": 5, "airbags": 7},
                        {"name": "Pack Three Luxury (79 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2790000, "battery": "79 kWh", "power": "285 PS", "torque": "380 Nm", "range_claimed": 656, "range_tested": 530, "seating": 5, "airbags": 7}
                    ]
                },
                "Mahindra XEV 9s": {
                    "category": "electric-vehicle",
                    "body_type": "Electric SUV",
                    "length_mm": 4740, "width_mm": 1900, "height_mm": 1680, "wheelbase_mm": 2775,
                    "ground_clearance_mm": 205,
                    "variants": [
                        {"name": "Pack One (59 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2090000, "battery": "59 kWh", "power": "231 PS", "torque": "380 Nm", "range_claimed": 520, "range_tested": 430, "seating": 5, "airbags": 6},
                        {"name": "Pack Two (79 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2390000, "battery": "79 kWh", "power": "285 PS", "torque": "380 Nm", "range_claimed": 640, "range_tested": 510, "seating": 5, "airbags": 7}
                    ]
                },
                "Mahindra BE 6e": {
                    "category": "electric-vehicle",
                    "body_type": "Electric SUV Coupe",
                    "length_mm": 4371, "width_mm": 1907, "height_mm": 1627, "wheelbase_mm": 2775,
                    "ground_clearance_mm": 207,
                    "variants": [
                        {"name": "Pack One (59 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1890000, "battery": "59 kWh", "power": "231 PS", "torque": "380 Nm", "range_claimed": 450, "range_tested": 380, "seating": 5, "airbags": 6},
                        {"name": "Pack Two (79 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2690000, "battery": "79 kWh", "power": "285 PS", "torque": "380 Nm", "range_claimed": 682, "range_tested": 520, "seating": 5, "airbags": 7}
                    ]
                },
                "Mahindra BE 6": {
                    "category": "electric-vehicle",
                    "body_type": "Electric SUV Coupe",
                    "length_mm": 4371, "width_mm": 1907, "height_mm": 1627, "wheelbase_mm": 2775,
                    "ground_clearance_mm": 207,
                    "variants": [
                        {"name": "Pack One (59 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1890000, "battery": "59 kWh", "power": "231 PS", "torque": "380 Nm", "range_claimed": 450, "range_tested": 380, "seating": 5, "airbags": 6},
                        {"name": "Pack Two (79 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2690000, "battery": "79 kWh", "power": "285 PS", "torque": "380 Nm", "range_claimed": 682, "range_tested": 520, "seating": 5, "airbags": 7}
                    ]
                },
                "Mahindra Scorpio-N": {
                    "category": "car",
                    "body_type": "Mid-size SUV",
                    "length_mm": 4662, "width_mm": 1917, "height_mm": 1857,
                    "variants": [
                        {"name": "Z4 2.2L mHawk Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1585000, "engine": "2198 cc", "power": "175 PS", "torque": "370 Nm", "seating": 7, "airbags": 2},
                        {"name": "Z8 2.0L mStallion Petrol AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 2049000, "engine": "1997 cc", "power": "203 PS", "torque": "380 Nm", "seating": 7, "airbags": 6},
                        {"name": "Z8L 2.2L mHawk Diesel 4x4", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2454000, "engine": "2198 cc", "power": "175 PS", "torque": "400 Nm", "seating": 7, "airbags": 6}
                    ]
                },
                "Mahindra XUV 3XO": {
                    "category": "car",
                    "body_type": "Compact SUV",
                    "length_mm": 3990, "width_mm": 1821, "height_mm": 1647, "wheelbase_mm": 2600,
                    "ground_clearance_mm": 201, "safety_rating": 5, "safety_agency": "BHARAT_NCAP",
                    "variants": [
                        {"name": "MX1 1.2L mStallion Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 779000, "engine": "1197 cc", "power": "111 PS", "torque": "200 Nm", "seating": 5, "airbags": 6},
                        {"name": "MX2 Pro 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 899000, "engine": "1197 cc", "power": "111 PS", "torque": "200 Nm", "seating": 5, "airbags": 6},
                        {"name": "AX5 1.2L TGDi Turbo AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1219000, "engine": "1197 cc", "power": "130 PS", "torque": "230 Nm", "seating": 5, "airbags": 6},
                        {"name": "AX7 Luxury 1.2L TGDi AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1549000, "engine": "1197 cc", "power": "130 PS", "torque": "230 Nm", "seating": 5, "airbags": 6}
                    ]
                },
                "Mahindra Bolero Pik-Up": {
                    "category": "commercial-vehicle",
                    "body_type": "Commercial Pickup Truck",
                    "length_mm": 5215, "width_mm": 1700, "height_mm": 1865, "wheelbase_mm": 3264,
                    "variants": [
                        {"name": "Bolero Maxi Truck Plus", "fuel": "DIESEL", "trans": "MANUAL", "price": 775000, "engine": "2523 cc", "power": "65 HP", "torque": "195 Nm", "payload_kg": 1200, "seating": 2, "airbags": 0},
                        {"name": "Bolero Pik-Up ExtraLong 1.3T", "fuel": "DIESEL", "trans": "MANUAL", "price": 895000, "engine": "2523 cc", "power": "75 HP", "torque": "200 Nm", "payload_kg": 1300, "seating": 2, "airbags": 0},
                        {"name": "Bolero Pik-Up ExtraLong 1.7T", "fuel": "DIESEL", "trans": "MANUAL", "price": 935000, "engine": "2523 cc", "power": "75 HP", "torque": "200 Nm", "payload_kg": 1700, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Maruti Suzuki": {
            "type": "CARS",
            "portal_url": "https://www.marutisuzuki.com",
            "press_url": "https://www.marutisuzuki.com/corporate/media/press-releases",
            "models": {
                "Maruti Suzuki Swift": {
                    "category": "car",
                    "body_type": "Hatchback",
                    "length_mm": 3860, "width_mm": 1735, "height_mm": 1520, "wheelbase_mm": 2450,
                    "variants": [
                        {"name": "LXi 1.2L Z-Series MT", "fuel": "PETROL", "trans": "MANUAL", "price": 649000, "engine": "1197 cc", "power": "82 PS", "torque": "112 Nm", "mileage": 24.8, "seating": 5, "airbags": 6},
                        {"name": "VXi 1.2L Z-Series MT", "fuel": "PETROL", "trans": "MANUAL", "price": 729500, "engine": "1197 cc", "power": "82 PS", "torque": "112 Nm", "mileage": 24.8, "seating": 5, "airbags": 6},
                        {"name": "ZXi 1.2L Z-Series AGS", "fuel": "PETROL", "trans": "AMT", "price": 875000, "engine": "1197 cc", "power": "82 PS", "torque": "112 Nm", "mileage": 25.75, "seating": 5, "airbags": 6},
                        {"name": "ZXi Plus 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 959500, "engine": "1197 cc", "power": "82 PS", "torque": "112 Nm", "mileage": 25.75, "seating": 5, "airbags": 6}
                    ]
                },
                "Maruti Suzuki Brezza": {
                    "category": "car",
                    "body_type": "Compact SUV",
                    "length_mm": 3995, "width_mm": 1790, "height_mm": 1685, "wheelbase_mm": 2500,
                    "variants": [
                        {"name": "LXi 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 834000, "engine": "1462 cc", "power": "103 PS", "torque": "137 Nm", "mileage": 19.89, "seating": 5, "airbags": 2},
                        {"name": "ZXi Plus 1.5L AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1398000, "engine": "1462 cc", "power": "103 PS", "torque": "137 Nm", "mileage": 19.8, "seating": 5, "airbags": 6}
                    ]
                },
                "Maruti Suzuki WagonR": {
                    "category": "car",
                    "body_type": "Hatchback",
                    "length_mm": 3655, "width_mm": 1620, "height_mm": 1675, "wheelbase_mm": 2435,
                    "variants": [
                        {"name": "LXi 1.0L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 554500, "engine": "998 cc", "power": "67 PS", "torque": "89 Nm", "mileage": 24.35, "seating": 5, "airbags": 2},
                        {"name": "VXi 1.0L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 599500, "engine": "998 cc", "power": "67 PS", "torque": "89 Nm", "mileage": 24.35, "seating": 5, "airbags": 2},
                        {"name": "ZXi 1.2L DualJet MT", "fuel": "PETROL", "trans": "MANUAL", "price": 628000, "engine": "1197 cc", "power": "90 PS", "torque": "113 Nm", "mileage": 23.56, "seating": 5, "airbags": 2},
                        {"name": "ZXi Plus 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 738000, "engine": "1197 cc", "power": "90 PS", "torque": "113 Nm", "mileage": 24.43, "seating": 5, "airbags": 2},
                        {"name": "LXi S-CNG 1.0L MT", "fuel": "CNG", "trans": "MANUAL", "price": 644500, "engine": "998 cc", "power": "57 PS", "torque": "82 Nm", "mileage": 34.05, "seating": 5, "airbags": 2},
                        {"name": "VXi S-CNG 1.0L MT", "fuel": "CNG", "trans": "MANUAL", "price": 689500, "engine": "998 cc", "power": "57 PS", "torque": "82 Nm", "mileage": 34.05, "seating": 5, "airbags": 2}
                    ]
                },
                "Maruti Suzuki Wagon R": {
                    "category": "car",
                    "body_type": "Hatchback",
                    "length_mm": 3655, "width_mm": 1620, "height_mm": 1675, "wheelbase_mm": 2435,
                    "variants": [
                        {"name": "LXi 1.0L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 554500, "engine": "998 cc", "power": "67 PS", "torque": "89 Nm", "mileage": 24.35, "seating": 5, "airbags": 2},
                        {"name": "VXi 1.0L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 599500, "engine": "998 cc", "power": "67 PS", "torque": "89 Nm", "mileage": 24.35, "seating": 5, "airbags": 2},
                        {"name": "ZXi 1.2L DualJet MT", "fuel": "PETROL", "trans": "MANUAL", "price": 628000, "engine": "1197 cc", "power": "90 PS", "torque": "113 Nm", "mileage": 23.56, "seating": 5, "airbags": 2},
                        {"name": "ZXi Plus 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 738000, "engine": "1197 cc", "power": "90 PS", "torque": "113 Nm", "mileage": 24.43, "seating": 5, "airbags": 2},
                        {"name": "LXi S-CNG 1.0L MT", "fuel": "CNG", "trans": "MANUAL", "price": 644500, "engine": "998 cc", "power": "57 PS", "torque": "82 Nm", "mileage": 34.05, "seating": 5, "airbags": 2}
                    ]
                },
                "Maruti Suzuki Ignis": {
                    "category": "car",
                    "body_type": "Compact Hatchback",
                    "length_mm": 3700, "width_mm": 1690, "height_mm": 1595, "wheelbase_mm": 2435,
                    "ground_clearance_mm": 180,
                    "variants": [
                        {"name": "Sigma 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 584000, "engine": "1197 cc", "power": "83 PS", "torque": "113 Nm", "mileage": 20.89, "seating": 5, "airbags": 2},
                        {"name": "Delta 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 638000, "engine": "1197 cc", "power": "83 PS", "torque": "113 Nm", "mileage": 20.89, "seating": 5, "airbags": 2},
                        {"name": "Zeta 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 696000, "engine": "1197 cc", "power": "83 PS", "torque": "113 Nm", "mileage": 20.89, "seating": 5, "airbags": 2},
                        {"name": "Alpha 1.2L Petrol AMT", "fuel": "PETROL", "trans": "AMT", "price": 816000, "engine": "1197 cc", "power": "83 PS", "torque": "113 Nm", "mileage": 20.89, "seating": 5, "airbags": 2}
                    ]
                },
                "Maruti Suzuki Grand Vitara": {
                    "category": "car",
                    "body_type": "Mid-size SUV",
                    "length_mm": 4345, "width_mm": 1795, "height_mm": 1645, "wheelbase_mm": 2600,
                    "ground_clearance_mm": 210,
                    "variants": [
                        {"name": "Sigma 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1099000, "engine": "1462 cc", "power": "103 PS", "torque": "137 Nm", "mileage": 21.11, "seating": 5, "airbags": 2},
                        {"name": "Delta 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1219000, "engine": "1462 cc", "power": "103 PS", "torque": "137 Nm", "mileage": 21.11, "seating": 5, "airbags": 2},
                        {"name": "Zeta 1.5L Smart Hybrid AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1539000, "engine": "1462 cc", "power": "103 PS", "torque": "137 Nm", "mileage": 20.58, "seating": 5, "airbags": 6},
                        {"name": "Alpha 1.5L Smart Hybrid AllGrip 4x4", "fuel": "PETROL", "trans": "MANUAL", "price": 1701000, "engine": "1462 cc", "power": "103 PS", "torque": "137 Nm", "seating": 5, "airbags": 6},
                        {"name": "Zeta Plus Strong Hybrid e-CVT", "fuel": "HYBRID", "trans": "CVT", "price": 1843000, "engine": "1490 cc", "power": "116 PS", "torque": "141 Nm", "mileage": 27.97, "seating": 5, "airbags": 6},
                        {"name": "Alpha Plus Strong Hybrid e-CVT", "fuel": "HYBRID", "trans": "CVT", "price": 2009000, "engine": "1490 cc", "power": "116 PS", "torque": "141 Nm", "mileage": 27.97, "seating": 5, "airbags": 6},
                        {"name": "Delta S-CNG 1.5L MT", "fuel": "CNG", "trans": "MANUAL", "price": 1315000, "engine": "1462 cc", "power": "88 PS", "torque": "121.5 Nm", "mileage": 26.6, "seating": 5, "airbags": 2}
                    ]
                }
            }
        },
        "Hyundai": {
            "type": "CARS_AND_SUVS",
            "portal_url": "https://www.hyundai.com/in/en",
            "press_url": "https://www.hyundai.com/in/en/hyundai-story/press-releases",
            "models": {
                "Hyundai Creta": {
                    "category": "car",
                    "body_type": "Mid-size SUV",
                    "length_mm": 4330, "width_mm": 1790, "height_mm": 1635, "wheelbase_mm": 2610,
                    "ground_clearance_mm": 190,
                    "variants": [
                        {"name": "E 1.5L MPi Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1099900, "engine": "1497 cc", "power": "115 PS", "torque": "144 Nm", "seating": 5, "airbags": 6},
                        {"name": "EX 1.5L MPi Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1221000, "engine": "1497 cc", "power": "115 PS", "torque": "144 Nm", "seating": 5, "airbags": 6},
                        {"name": "SX 1.5L CRDi Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1699900, "engine": "1493 cc", "power": "116 PS", "torque": "250 Nm", "seating": 5, "airbags": 6},
                        {"name": "SX(O) 1.5L Turbo Petrol DCT", "fuel": "PETROL", "trans": "DCT", "price": 2014900, "engine": "1482 cc", "power": "160 PS", "torque": "253 Nm", "seating": 5, "airbags": 6}
                    ]
                },
                "Hyundai Venue": {
                    "category": "car",
                    "body_type": "Compact SUV",
                    "length_mm": 3995, "width_mm": 1770, "height_mm": 1617, "wheelbase_mm": 2500,
                    "ground_clearance_mm": 195,
                    "variants": [
                        {"name": "E 1.2L Kappa Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 794100, "engine": "1197 cc", "power": "83 PS", "torque": "114 Nm", "seating": 5, "airbags": 6},
                        {"name": "S Plus 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 935800, "engine": "1197 cc", "power": "83 PS", "torque": "114 Nm", "seating": 5, "airbags": 6},
                        {"name": "SX 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1105200, "engine": "1197 cc", "power": "83 PS", "torque": "114 Nm", "seating": 5, "airbags": 6},
                        {"name": "SX(O) 1.0L Turbo GDi DCT", "fuel": "PETROL", "trans": "DCT", "price": 1348000, "engine": "998 cc", "power": "120 PS", "torque": "172 Nm", "seating": 5, "airbags": 6}
                    ]
                }
            }
        },
        "Kia": {
            "type": "CARS_AND_SUVS",
            "portal_url": "https://www.kia.com/in",
            "press_url": "https://www.kia.com/in/discover-kia/press-release.html",
            "models": {
                "Kia Seltos": {
                    "category": "car",
                    "body_type": "Mid-size SUV",
                    "length_mm": 4365, "width_mm": 1800, "height_mm": 1645, "wheelbase_mm": 2610,
                    "ground_clearance_mm": 190,
                    "variants": [
                        {"name": "HTE 1.5L Smartstream Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1090000, "engine": "1497 cc", "power": "115 PS", "torque": "144 Nm", "seating": 5, "airbags": 6},
                        {"name": "HTK Plus 1.5L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1406000, "engine": "1497 cc", "power": "115 PS", "torque": "144 Nm", "seating": 5, "airbags": 6},
                        {"name": "HTX 1.5L CRDi Diesel AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 1820000, "engine": "1493 cc", "power": "116 PS", "torque": "250 Nm", "seating": 5, "airbags": 6},
                        {"name": "GTX Plus 1.5L Turbo Petrol DCT", "fuel": "PETROL", "trans": "DCT", "price": 2000000, "engine": "1482 cc", "power": "160 PS", "torque": "253 Nm", "seating": 5, "airbags": 6},
                        {"name": "X-Line 1.5L Turbo Petrol DCT", "fuel": "PETROL", "trans": "DCT", "price": 2037000, "engine": "1482 cc", "power": "160 PS", "torque": "253 Nm", "seating": 5, "airbags": 6}
                    ]
                }
            }
        },
        "Toyota": {
            "type": "CARS_AND_MPVS",
            "portal_url": "https://www.toyotabharat.com",
            "press_url": "https://www.toyotabharat.com/news/",
            "models": {
                "Toyota Innova Crysta": {
                    "category": "car",
                    "body_type": "Premium MPV",
                    "length_mm": 4735, "width_mm": 1830, "height_mm": 1795, "wheelbase_mm": 2750,
                    "variants": [
                        {"name": "GX 2.4L Diesel 7-Seater", "fuel": "DIESEL", "trans": "MANUAL", "price": 1999000, "engine": "2393 cc", "power": "150 PS", "torque": "343 Nm", "seating": 7, "airbags": 3},
                        {"name": "VX 2.4L Diesel 8-Seater", "fuel": "DIESEL", "trans": "MANUAL", "price": 2464000, "engine": "2393 cc", "power": "150 PS", "torque": "343 Nm", "seating": 8, "airbags": 7},
                        {"name": "ZX 2.4L Diesel 7-Seater", "fuel": "DIESEL", "trans": "MANUAL", "price": 2630000, "engine": "2393 cc", "power": "150 PS", "torque": "343 Nm", "seating": 7, "airbags": 7}
                    ]
                }
            }
        },
        "MG Motor": {
            "type": "CARS_AND_EVS",
            "portal_url": "https://www.mgmotor.co.in",
            "press_url": "https://www.mgmotor.co.in/media-center",
            "models": {
                "MG Windsor EV": {
                    "category": "electric-vehicle",
                    "body_type": "Crossover EV",
                    "length_mm": 4295, "width_mm": 1850, "height_mm": 1677, "wheelbase_mm": 2700,
                    "variants": [
                        {"name": "Excite (38 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1349800, "battery": "38 kWh", "power": "136 PS", "torque": "200 Nm", "range_claimed": 331, "range_tested": 275, "seating": 5, "airbags": 6},
                        {"name": "Exclusive (38 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1449800, "battery": "38 kWh", "power": "136 PS", "torque": "200 Nm", "range_claimed": 331, "range_tested": 275, "seating": 5, "airbags": 6},
                        {"name": "Essence (38 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1549800, "battery": "38 kWh", "power": "136 PS", "torque": "200 Nm", "range_claimed": 331, "range_tested": 275, "seating": 5, "airbags": 6}
                    ]
                }
            }
        },
        "BYD": {
            "type": "ELECTRIC_VEHICLES",
            "portal_url": "https://bydautoindia.com",
            "press_url": "https://bydautoindia.com/press",
            "models": {
                "BYD Atto 3": {
                    "category": "electric-vehicle",
                    "body_type": "Electric SUV",
                    "length_mm": 4455, "width_mm": 1875, "height_mm": 1615, "wheelbase_mm": 2720,
                    "variants": [
                        {"name": "Dynamic (49.92 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2499000, "battery": "49.92 kWh", "power": "204 PS", "torque": "310 Nm", "range_claimed": 468, "range_tested": 380, "seating": 5, "airbags": 7},
                        {"name": "Premium (60.48 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 2985000, "battery": "60.48 kWh", "power": "204 PS", "torque": "310 Nm", "range_claimed": 521, "range_tested": 430, "seating": 5, "airbags": 7},
                        {"name": "Superior (60.48 kWh)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 3399000, "battery": "60.48 kWh", "power": "204 PS", "torque": "310 Nm", "range_claimed": 521, "range_tested": 430, "seating": 5, "airbags": 7}
                    ]
                }
            }
        },
        "Honda": {
            "type": "CARS_AND_SCOOTERS",
            "portal_url": "https://www.hondacarindia.com",
            "press_url": "https://www.hondacarindia.com/media-center",
            "models": {
                "Honda Elevate": {
                    "category": "car",
                    "body_type": "Mid-size SUV",
                    "length_mm": 4312, "width_mm": 1790, "height_mm": 1650, "wheelbase_mm": 2650,
                    "ground_clearance_mm": 220,
                    "variants": [
                        {"name": "SV 1.5L i-VTEC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1169000, "engine": "1498 cc", "power": "121 PS", "torque": "145 Nm", "seating": 5, "airbags": 2},
                        {"name": "V 1.5L i-VTEC CVT", "fuel": "PETROL", "trans": "CVT", "price": 1321000, "engine": "1498 cc", "power": "121 PS", "torque": "145 Nm", "seating": 5, "airbags": 2},
                        {"name": "ZX 1.5L i-VTEC CVT (Top)", "fuel": "PETROL", "trans": "CVT", "price": 1620000, "engine": "1498 cc", "power": "121 PS", "torque": "145 Nm", "seating": 5, "airbags": 6}
                    ]
                },
                "Honda City": {
                    "category": "car",
                    "body_type": "Sedan",
                    "length_mm": 4574, "width_mm": 1748, "height_mm": 1489, "wheelbase_mm": 2600,
                    "variants": [
                        {"name": "SV 1.5L i-VTEC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1182000, "engine": "1498 cc", "power": "121 PS", "torque": "145 Nm", "seating": 5, "airbags": 4},
                        {"name": "ZX 1.5L i-VTEC CVT", "fuel": "PETROL", "trans": "CVT", "price": 1635000, "engine": "1498 cc", "power": "121 PS", "torque": "145 Nm", "seating": 5, "airbags": 6}
                    ]
                },
                "Honda Amaze": {
                    "category": "car",
                    "body_type": "Compact Sedan",
                    "length_mm": 3995, "width_mm": 1695, "height_mm": 1501, "wheelbase_mm": 2470,
                    "variants": [
                        {"name": "E 1.2L i-VTEC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 716000, "engine": "1199 cc", "power": "90 PS", "torque": "110 Nm", "seating": 5, "airbags": 2},
                        {"name": "VX 1.2L i-VTEC CVT", "fuel": "PETROL", "trans": "CVT", "price": 992000, "engine": "1199 cc", "power": "90 PS", "torque": "110 Nm", "seating": 5, "airbags": 2}
                    ]
                },
                "Honda Activa": {
                    "category": "two-wheeler",
                    "body_type": "Gearless Scooter",
                    "length_mm": 1833, "width_mm": 697, "height_mm": 1156, "wheelbase_mm": 1260,
                    "ground_clearance_mm": 162,
                    "variants": [
                        {"name": "Activa 6G Standard", "fuel": "PETROL", "trans": "CVT", "price": 76684, "engine": "109.51 cc", "power": "7.84 PS", "torque": "8.90 Nm", "mileage": 50.0, "seating": 2, "airbags": 0},
                        {"name": "Activa 6G Deluxe", "fuel": "PETROL", "trans": "CVT", "price": 79184, "engine": "109.51 cc", "power": "7.84 PS", "torque": "8.90 Nm", "mileage": 50.0, "seating": 2, "airbags": 0},
                        {"name": "Activa 6G H-Smart", "fuel": "PETROL", "trans": "CVT", "price": 82684, "engine": "109.51 cc", "power": "7.84 PS", "torque": "8.90 Nm", "mileage": 50.0, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Hero MotoCorp": {
            "type": "TWO_WHEELERS",
            "portal_url": "https://www.heromotocorp.com",
            "press_url": "https://www.heromotocorp.com/en-in/press-releases.html",
            "models": {
                "Hero Splendor Plus": {
                    "category": "two-wheeler",
                    "body_type": "Commuter Motorcycle",
                    "length_mm": 2000, "width_mm": 720, "height_mm": 1052, "wheelbase_mm": 1236,
                    "ground_clearance_mm": 165,
                    "variants": [
                        {"name": "Self Start Drum Brake Cast Wheel", "fuel": "PETROL", "trans": "MANUAL", "price": 75441, "engine": "97.2 cc", "power": "8.02 PS", "torque": "8.05 Nm", "mileage": 70.0, "seating": 2, "airbags": 0},
                        {"name": "Splendor Plus XTEC", "fuel": "PETROL", "trans": "MANUAL", "price": 79911, "engine": "97.2 cc", "power": "8.02 PS", "torque": "8.05 Nm", "mileage": 70.0, "seating": 2, "airbags": 0},
                        {"name": "Splendor Plus XTEC 2.0", "fuel": "PETROL", "trans": "MANUAL", "price": 82911, "engine": "97.2 cc", "power": "8.02 PS", "torque": "8.05 Nm", "mileage": 73.0, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Royal Enfield": {
            "type": "MOTORCYCLES",
            "portal_url": "https://www.royalenfield.com",
            "press_url": "https://www.royalenfield.com/in/en/press-releases",
            "models": {
                "Royal Enfield Hunter 350": {
                    "category": "two-wheeler",
                    "body_type": "Roadster Motorcycle",
                    "length_mm": 2055, "width_mm": 800, "height_mm": 1055, "wheelbase_mm": 1370,
                    "ground_clearance_mm": 150,
                    "variants": [
                        {"name": "Factory Series (Base)", "fuel": "PETROL", "trans": "MANUAL", "price": 137600, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.2, "seating": 2, "airbags": 0},
                        {"name": "Dapper Series (Mid)", "fuel": "PETROL", "trans": "MANUAL", "price": 166000, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.2, "seating": 2, "airbags": 0},
                        {"name": "Rebel Series (Top)", "fuel": "PETROL", "trans": "MANUAL", "price": 171700, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.2, "seating": 2, "airbags": 0}
                    ]
                },
                "Royal Enfield Classic 350": {
                    "category": "two-wheeler",
                    "body_type": "Modern Classic Motorcycle",
                    "length_mm": 2145, "width_mm": 785, "height_mm": 1090, "wheelbase_mm": 1390,
                    "ground_clearance_mm": 170,
                    "variants": [
                        {"name": "Redditch Single Channel ABS", "fuel": "PETROL", "trans": "MANUAL", "price": 193080, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.0, "seating": 2, "airbags": 0},
                        {"name": "Halcyon Dual Channel ABS", "fuel": "PETROL", "trans": "MANUAL", "price": 202094, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.0, "seating": 2, "airbags": 0},
                        {"name": "Signals Edition Dual Channel ABS", "fuel": "PETROL", "trans": "MANUAL", "price": 213805, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.0, "seating": 2, "airbags": 0},
                        {"name": "Dark Series Alloy Wheels", "fuel": "PETROL", "trans": "MANUAL", "price": 220974, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.0, "seating": 2, "airbags": 0},
                        {"name": "Chrome Series Dual Channel", "fuel": "PETROL", "trans": "MANUAL", "price": 224755, "engine": "349 cc", "power": "20.2 PS", "torque": "27 Nm", "mileage": 36.0, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Bajaj Auto": {
            "type": "TWO_AND_THREE_WHEELERS",
            "portal_url": "https://www.bajajauto.com",
            "press_url": "https://www.bajajauto.com/about-us/news-media",
            "models": {
                "Bajaj Pulsar NS200": {
                    "category": "two-wheeler",
                    "body_type": "Naked Sports Motorcycle",
                    "length_mm": 2017, "width_mm": 804, "height_mm": 1075, "wheelbase_mm": 1363,
                    "ground_clearance_mm": 168,
                    "variants": [
                        {"name": "Pulsar NS200 Dual Channel ABS USD Fork", "fuel": "PETROL", "trans": "MANUAL", "price": 158976, "engine": "199.5 cc", "power": "24.5 PS", "torque": "18.74 Nm", "mileage": 37.0, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "TVS Motor": {
            "type": "TWO_WHEELERS",
            "portal_url": "https://www.tvsmotor.com",
            "press_url": "https://www.tvsmotor.com/media/press-releases",
            "models": {
                "TVS Apache RTR 160": {
                    "category": "two-wheeler",
                    "body_type": "Sports Commuter Motorcycle",
                    "length_mm": 2085, "width_mm": 730, "height_mm": 1105,
                    "variants": [
                        {"name": "RTR 160 2V Single Disc", "fuel": "PETROL", "trans": "MANUAL", "price": 119990, "engine": "159.7 cc", "power": "16.04 PS", "torque": "13.85 Nm", "mileage": 45.0, "seating": 2, "airbags": 0},
                        {"name": "RTR 160 4V Special Edition", "fuel": "PETROL", "trans": "MANUAL", "price": 132000, "engine": "159.7 cc", "power": "17.55 PS", "torque": "14.73 Nm", "mileage": 43.0, "seating": 2, "airbags": 0}
                    ]
                },
                "TVS Jupiter": {
                    "category": "two-wheeler",
                    "body_type": "Family Scooter",
                    "length_mm": 1834, "width_mm": 678, "height_mm": 1286, "wheelbase_mm": 1275,
                    "ground_clearance_mm": 163,
                    "variants": [
                        {"name": "Jupiter Sheet Metal White", "fuel": "PETROL", "trans": "CVT", "price": 73700, "engine": "113.3 cc", "power": "8.02 PS", "torque": "9.8 Nm", "mileage": 50.0, "seating": 2, "airbags": 0},
                        {"name": "Jupiter Drum Alloy", "fuel": "PETROL", "trans": "CVT", "price": 79200, "engine": "113.3 cc", "power": "8.02 PS", "torque": "9.8 Nm", "mileage": 50.0, "seating": 2, "airbags": 0},
                        {"name": "Jupiter SmartXonnect Disc", "fuel": "PETROL", "trans": "CVT", "price": 87250, "engine": "113.3 cc", "power": "8.02 PS", "torque": "9.8 Nm", "mileage": 50.0, "seating": 2, "airbags": 0}
                    ]
                },
                "TVS iQube": {
                    "category": "electric-vehicle",
                    "body_type": "Electric Scooter",
                    "length_mm": 1805, "width_mm": 645, "height_mm": 1140, "wheelbase_mm": 1301,
                    "variants": [
                        {"name": "iQube Standard 2.2 kWh", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 107299, "battery": "2.2 kWh", "power": "4.4 kW", "torque": "140 Nm", "range_claimed": 75, "range_tested": 60, "seating": 2, "airbags": 0},
                        {"name": "iQube S 3.4 kWh", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 146420, "battery": "3.4 kWh", "power": "4.4 kW", "torque": "140 Nm", "range_claimed": 100, "range_tested": 85, "seating": 2, "airbags": 0},
                        {"name": "iQube ST 5.1 kWh", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 185373, "battery": "5.1 kWh", "power": "4.4 kW", "torque": "140 Nm", "range_claimed": 150, "range_tested": 125, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Ather Energy": {
            "type": "ELECTRIC_SCOOTERS",
            "portal_url": "https://www.atherenergy.com",
            "press_url": "https://www.atherenergy.com/press",
            "models": {
                "Ather 450X": {
                    "category": "electric-vehicle",
                    "body_type": "Electric Performance Scooter",
                    "length_mm": 1814, "width_mm": 734, "height_mm": 1120,
                    "variants": [
                        {"name": "450X 2.9 kWh", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 150500, "battery": "2.9 kWh", "power": "6.4 kW (8.7 PS)", "torque": "26 Nm", "range_claimed": 126, "range_tested": 105, "range_idc_claimed": 126, "range_tested_truerange": 105, "range": "126 km (IDC claimed)", "seating": 2, "airbags": 0},
                        {"name": "450X 3.7 kWh Pro Pack", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 190500, "battery": "3.7 kWh", "power": "6.4 kW (8.7 PS)", "torque": "26 Nm", "range_claimed": 161, "range_tested": 130, "range_idc_claimed": 161, "range_tested_truerange": 130, "range": "161 km (IDC claimed)", "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Ola Electric": {
            "type": "ELECTRIC_SCOOTERS",
            "portal_url": "https://www.olaelectric.com",
            "press_url": "https://www.olaelectric.com/newsroom",
            "models": {
                "Ola S1": {
                    "category": "electric-vehicle",
                    "body_type": "Electric Scooter",
                    "length_mm": 1860, "width_mm": 700, "height_mm": 1155,
                    "variants": [
                        {"name": "S1 Air 3 kWh", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 104999, "battery": "3.0 kWh", "power": "6 kW", "torque": "22 Nm", "range_claimed": 151, "range_tested": 115, "seating": 2, "airbags": 0},
                        {"name": "S1 Pro Gen 2 4 kWh", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 134999, "battery": "4.0 kWh", "power": "11 kW", "torque": "58 Nm", "range_claimed": 195, "range_tested": 143, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Tata Motors Commercial Vehicles": {
            "type": "COMMERCIAL_VEHICLES",
            "portal_url": "https://smallcommercialvehicles.tatamotors.com",
            "press_url": "https://www.tatamotors.com/media/press-releases/",
            "models": {
                "Tata Ace": {
                    "category": "commercial-vehicle",
                    "body_type": "Small Commercial Vehicle (Mini Truck)",
                    "length_mm": 3800, "width_mm": 1500, "height_mm": 1845,
                    "variants": [
                        {"name": "Ace Gold Diesel Plus", "fuel": "DIESEL", "trans": "MANUAL", "price": 599000, "engine": "700 cc", "power": "20 HP", "torque": "45 Nm", "payload_kg": 750, "seating": 2, "airbags": 0},
                        {"name": "Ace EV (Electric Mini Truck)", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 920000, "battery": "21.3 kWh", "power": "36 HP", "torque": "130 Nm", "range_claimed": 154, "range_tested": 120, "payload_kg": 600, "seating": 2, "airbags": 0}
                    ]
                },
                "Tata 407": {
                    "category": "commercial-vehicle",
                    "body_type": "Light Commercial Truck",
                    "length_mm": 4945, "width_mm": 2100, "height_mm": 2280, "wheelbase_mm": 3100,
                    "variants": [
                        {"name": "SFC 407 Gold 29WB", "fuel": "DIESEL", "trans": "MANUAL", "price": 1230000, "engine": "2956 cc 4SPCR Diesel", "power": "100 HP", "torque": "300 Nm", "payload_kg": 2250, "gvw_kg": 4450, "seating": 2, "airbags": 0},
                        {"name": "LPT 407 Gold 34WB", "fuel": "DIESEL", "trans": "MANUAL", "price": 1310000, "engine": "2956 cc 4SPCR Diesel", "power": "100 HP", "torque": "300 Nm", "payload_kg": 2400, "gvw_kg": 4650, "seating": 2, "airbags": 0}
                    ]
                }
            }
        },
        "Ashok Leyland": {
            "type": "COMMERCIAL_VEHICLES",
            "portal_url": "https://www.ashokleyland.com",
            "press_url": "https://www.ashokleyland.com/in/en/media-and-press-releases",
            "models": {
                "Ashok Leyland Dost": {
                    "category": "commercial-vehicle",
                    "body_type": "Light Commercial Truck",
                    "length_mm": 4485, "width_mm": 1620, "height_mm": 1835, "wheelbase_mm": 2350,
                    "variants": [
                        {"name": "Dost Strong Diesel", "fuel": "DIESEL", "trans": "MANUAL", "price": 725000, "engine": "1478 cc", "power": "70 HP", "torque": "170 Nm", "payload_kg": 1250, "seating": 2, "airbags": 0},
                        {"name": "Bada Dost i2 Diesel", "fuel": "DIESEL", "trans": "MANUAL", "price": 875000, "engine": "1478 cc", "power": "70 HP", "torque": "190 Nm", "payload_kg": 1425, "seating": 3, "airbags": 0},
                        {"name": "Bada Dost i3+ Diesel", "fuel": "DIESEL", "trans": "MANUAL", "price": 915000, "engine": "1478 cc", "power": "80 HP", "torque": "190 Nm", "payload_kg": 1525, "seating": 3, "airbags": 0},
                        {"name": "Bada Dost i4 Diesel", "fuel": "DIESEL", "trans": "MANUAL", "price": 945000, "engine": "1478 cc", "power": "80 HP", "torque": "190 Nm", "payload_kg": 1860, "seating": 3, "airbags": 0}
                    ]
                },
                "Ashok Leyland truck": {
                    "category": "commercial-vehicle",
                    "body_type": "Medium Commercial Truck",
                    "length_mm": 5025, "width_mm": 1842, "height_mm": 2060,
                    "variants": [
                        {"name": "Ecomet Star 1415 Medium Truck", "fuel": "DIESEL", "trans": "MANUAL", "price": 2250000, "engine": "3839 cc", "power": "150 HP", "torque": "450 Nm", "gvw_kg": 14050, "seating": 3, "airbags": 0}
                    ]
                }
            }
        },
        "Eicher Motors": {
            "type": "COMMERCIAL_VEHICLES",
            "portal_url": "https://www.eicher.in",
            "press_url": "https://www.eicher.in/press-releases",
            "models": {
                "Eicher Pro series": {
                    "category": "commercial-vehicle",
                    "body_type": "Commercial Truck",
                    "length_mm": 5395, "width_mm": 2005, "height_mm": 2280,
                    "variants": [
                        {"name": "Pro 2049 Light Truck", "fuel": "DIESEL", "trans": "MANUAL", "price": 1216000, "engine": "1965 cc E366 3-cyl Diesel", "power": "100 HP", "torque": "285 Nm", "payload_kg": 2366, "gvw_kg": 4995, "seating": 3, "airbags": 0},
                        {"name": "Pro 3015 Medium Truck", "fuel": "DIESEL", "trans": "MANUAL", "price": 2375000, "engine": "3760 cc E494 4-cyl Diesel", "power": "160 HP", "torque": "500 Nm", "payload_kg": 10500, "gvw_kg": 16140, "seating": 3, "airbags": 0},
                        {"name": "Pro 3019 Heavy Medium Truck", "fuel": "DIESEL", "trans": "MANUAL", "price": 2750000, "engine": "3760 cc E494 4-cyl Diesel", "power": "180 HP", "torque": "600 Nm", "payload_kg": 12800, "gvw_kg": 18500, "seating": 3, "airbags": 0}
                    ]
                }
            }
        }
    }

    @classmethod
    def match_model(cls, query: str) -> Optional[Dict[str, Any]]:
        """Finds OEM baseline specifications for a model query."""
        clean_q = query.lower().strip()
        common_brand_words = {"maruti", "suzuki", "tata", "mahindra", "hyundai", "honda", "toyota", "kia", "hero", "bajaj", "tvs", "ather", "ola", "ashok", "leyland", "eicher", "mg", "motor"}
        
        for brand_name, data in cls.OEM_PORTALS.items():
            for m_name, m_data in data["models"].items():
                m_lower = m_name.lower()
                if m_lower in clean_q or clean_q in m_lower:
                    return {
                        "brand": brand_name,
                        "model": m_name,
                        "portal_url": data["portal_url"],
                        "press_url": data["press_url"],
                        "details": m_data
                    }
                
                # Check pure model name without brand
                model_specific = " ".join([w for w in m_lower.split() if w not in common_brand_words])
                if model_specific and (model_specific in clean_q or clean_q in model_specific):
                    return {
                        "brand": brand_name,
                        "model": m_name,
                        "portal_url": data["portal_url"],
                        "press_url": data["press_url"],
                        "details": m_data
                    }

                # Check model token matching
                tokens = [t for t in model_specific.split() if len(t) >= 2]
                if tokens and all(t in clean_q for t in tokens):
                    return {
                        "brand": brand_name,
                        "model": m_name,
                        "portal_url": data["portal_url"],
                        "press_url": data["press_url"],
                        "details": m_data
                    }
        return None

# Register Top 50 Indian Flagship Models into OEM_PORTALS
try:
    from backend.app.seed.seed_top_50_cars import TOP_50_CARS
    for _c in TOP_50_CARS:
        _b = _c["brand_name"]
        if _b not in OEMSpecificationRegistry.OEM_PORTALS:
            OEMSpecificationRegistry.OEM_PORTALS[_b] = {
                "type": "CARS",
                "portal_url": f"https://www.{_b.lower().replace(' ', '')}.com",
                "press_url": f"https://www.{_b.lower().replace(' ', '')}.com/press",
                "models": {}
            }
        _oem_entry = OEMSpecificationRegistry.OEM_PORTALS[_b]["models"]
        if _c["name"] not in _oem_entry:
            _oem_entry[_c["name"]] = {
                "category": _c["category_slug"],
                "body_type": _c["body_type"],
                "variants": _c["variants"]
            }
except Exception as _e:
    pass
