import sys
from pathlib import Path

_file_path = Path(__file__).resolve()
_project_root = _file_path.parents[3]
_backend_dir = _file_path.parents[2]

for _p in [str(_project_root), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import asyncio
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, or_, func
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import (
    VehicleCategory, VehicleBrand, VehicleModel, VehicleVariant
)

# Top 50 cars data with exact user-provided images and realistic Indian ex-showroom specifications
TOP_50_CARS = [
    {
        "rank": 1,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Baleno",
        "slug": "maruti-suzuki-baleno",
        "search_aliases": ["baleno"],
        "body_type": "Hatchback",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcj0XBX8QgG4bAL2SIsWQ9n8DLdTqutGfsS6e-bJDy2Q&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Sigma 1.2L DualJet MT", "fuel": "PETROL", "trans": "MANUAL", "price": 666000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "Delta 1.2L DualJet MT", "fuel": "PETROL", "trans": "MANUAL", "price": 750000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "Zeta 1.2L DualJet MT", "fuel": "PETROL", "trans": "MANUAL", "price": 843000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "Alpha 1.2L DualJet AGS", "fuel": "PETROL", "trans": "AMT", "price": 988000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "Delta S-CNG 1.2L MT", "fuel": "CNG", "trans": "MANUAL", "price": 840000, "engine": "1197 cc", "power": "77.5 PS", "seating": 5}
        ]
    },
    {
        "rank": 2,
        "brand_name": "Tata Motors",
        "name": "Tata Nexon",
        "slug": "tata-nexon",
        "search_aliases": ["nexon"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://asset.autocarindia.com/static/news/images/20260908_073502_5ec713cb.png?w=420",
        "model_year": 2025,
        "variants": [
            {"name": "Smart 1.2L Turbo MT", "fuel": "PETROL", "trans": "MANUAL", "price": 800000, "engine": "1199 cc", "power": "120 PS", "seating": 5},
            {"name": "Pure 1.2L Turbo MT", "fuel": "PETROL", "trans": "MANUAL", "price": 970000, "engine": "1199 cc", "power": "120 PS", "seating": 5},
            {"name": "Creative Plus 1.2L Turbo MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1170000, "engine": "1199 cc", "power": "120 PS", "seating": 5},
            {"name": "Fearless Plus DCA Petrol", "fuel": "PETROL", "trans": "DCT", "price": 1490000, "engine": "1199 cc", "power": "120 PS", "seating": 5},
            {"name": "Pure 1.5L Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1110000, "engine": "1497 cc", "power": "115 PS", "seating": 5}
        ]
    },
    {
        "rank": 3,
        "brand_name": "Tata Motors",
        "name": "Tata Punch",
        "slug": "tata-punch",
        "search_aliases": ["punch"],
        "body_type": "Micro SUV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQI1RZHFzAYbLC_nKDxyTbKhiLnn4u9RlBon0I_fjLQqQ&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Pure 1.2L Revotron MT", "fuel": "PETROL", "trans": "MANUAL", "price": 613000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "Adventure Rhythm 1.2L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 725000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "Accomplished Dazzle 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 885000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "Creative Flagship 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 1020000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "Adventure iCNG Twin Cylinder", "fuel": "CNG", "trans": "MANUAL", "price": 795000, "engine": "1199 cc", "power": "73.5 PS", "seating": 5}
        ]
    },
    {
        "rank": 4,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Fronx",
        "slug": "maruti-suzuki-fronx",
        "search_aliases": ["fronx"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-fronx_600x400.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Sigma 1.2L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 751000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "Delta 1.2L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 837000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "Zeta 1.0L Turbo Boosterjet AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1205000, "engine": "998 cc Turbo", "power": "100 PS", "seating": 5},
            {"name": "Alpha 1.0L Turbo Boosterjet AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1304000, "engine": "998 cc Turbo", "power": "100 PS", "seating": 5},
            {"name": "Sigma S-CNG 1.2L MT", "fuel": "CNG", "trans": "MANUAL", "price": 846000, "engine": "1197 cc", "power": "77.5 PS", "seating": 5}
        ]
    },
    {
        "rank": 5,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Wagon R",
        "slug": "maruti-suzuki-wagon-r",
        "search_aliases": ["wagon r", "wagonr"],
        "body_type": "Hatchback",
        "category_slug": "car",
        "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-wagon-r_600x400.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "LXi 1.0L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 554500, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "VXi 1.0L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 599500, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "ZXi 1.2L DualJet MT", "fuel": "PETROL", "trans": "MANUAL", "price": 628000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "ZXi Plus 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 738000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "LXi S-CNG 1.0L MT", "fuel": "CNG", "trans": "MANUAL", "price": 644500, "engine": "998 cc", "power": "57 PS", "seating": 5}
        ]
    },
    {
        "rank": 6,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Dzire",
        "slug": "maruti-suzuki-dzire",
        "search_aliases": ["dzire"],
        "body_type": "Compact Sedan",
        "category_slug": "car",
        "image_url": "https://www.spinny.com/blog/wp-content/uploads/2024/11/New-Maruti-Suzuki-Dzire-1-jpg.webp",
        "model_year": 2025,
        "variants": [
            {"name": "LXi 1.2L Z-Series MT", "fuel": "PETROL", "trans": "MANUAL", "price": 679000, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "VXi 1.2L Z-Series MT", "fuel": "PETROL", "trans": "MANUAL", "price": 779000, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "ZXi 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 889000, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "ZXi Plus 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 1014000, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "VXi S-CNG 1.2L MT", "fuel": "CNG", "trans": "MANUAL", "price": 874000, "engine": "1197 cc", "power": "70 PS", "seating": 5}
        ]
    },
    {
        "rank": 7,
        "brand_name": "Hyundai",
        "name": "Hyundai Creta",
        "slug": "hyundai-creta",
        "search_aliases": ["creta"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTeE54tQtEGGH_3t6ylCcZ8idM2YjLpUx3qyq68iYLLIJX4O-T1KqT43MxU&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "E 1.5L MPi Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1100000, "engine": "1497 cc", "power": "115 PS", "seating": 5},
            {"name": "EX 1.5L MPi Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1221000, "engine": "1497 cc", "power": "115 PS", "seating": 5},
            {"name": "S(O) 1.5L Petrol IVT", "fuel": "PETROL", "trans": "CVT", "price": 1438000, "engine": "1497 cc", "power": "115 PS", "seating": 5},
            {"name": "SX 1.5L CRDi Diesel AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 1820000, "engine": "1493 cc", "power": "116 PS", "seating": 5},
            {"name": "SX(O) 1.5L Turbo Petrol DCT", "fuel": "PETROL", "trans": "DCT", "price": 2015000, "engine": "1482 cc Turbo", "power": "160 PS", "seating": 5}
        ]
    },
    {
        "rank": 8,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Swift",
        "slug": "maruti-suzuki-swift",
        "search_aliases": ["swift"],
        "body_type": "Hatchback",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqPufqmyo-UJOHWK5jrsKi9CoLc7V-peHEGJYjd5kqLQ&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "LXi 1.2L Z-Series MT", "fuel": "PETROL", "trans": "MANUAL", "price": 649000, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "VXi 1.2L Z-Series MT", "fuel": "PETROL", "trans": "MANUAL", "price": 729500, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "ZXi 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 875000, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "ZXi Plus 1.2L AGS", "fuel": "PETROL", "trans": "AMT", "price": 959500, "engine": "1197 cc", "power": "82 PS", "seating": 5},
            {"name": "VXi S-CNG 1.2L MT", "fuel": "CNG", "trans": "MANUAL", "price": 819500, "engine": "1197 cc", "power": "70 PS", "seating": 5}
        ]
    },
    {
        "rank": 9,
        "brand_name": "Mahindra",
        "name": "Mahindra Scorpio",
        "slug": "mahindra-scorpio-n",
        "search_aliases": ["scorpio", "scorpio-n"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Mahindra/Scorpio-N/13740/1785926288341/front-left-side-47.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Z2 2.2L mHawk Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1360000, "engine": "2198 cc", "power": "132 PS", "seating": 7},
            {"name": "Z4 2.2L mHawk Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1585000, "engine": "2198 cc", "power": "175 PS", "seating": 7},
            {"name": "Z8 2.0L mStallion Petrol AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 2049000, "engine": "1997 cc Turbo", "power": "203 PS", "seating": 7},
            {"name": "Z8L 2.2L mHawk 4x4 AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2454000, "engine": "2198 cc", "power": "175 PS", "seating": 7}
        ]
    },
    {
        "rank": 10,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Ertiga",
        "slug": "maruti-suzuki-ertiga",
        "search_aliases": ["ertiga"],
        "body_type": "MPV",
        "category_slug": "car",
        "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-ertiga_600x400.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "LXi 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 869000, "engine": "1462 cc", "power": "103 PS", "seating": 7},
            {"name": "VXi 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 983000, "engine": "1462 cc", "power": "103 PS", "seating": 7},
            {"name": "ZXi 1.5L Smart Hybrid AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1233000, "engine": "1462 cc", "power": "103 PS", "seating": 7},
            {"name": "ZXi Plus 1.5L AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1303000, "engine": "1462 cc", "power": "103 PS", "seating": 7},
            {"name": "VXi S-CNG 1.5L MT", "fuel": "CNG", "trans": "MANUAL", "price": 1078000, "engine": "1462 cc", "power": "88 PS", "seating": 7}
        ]
    },
    {
        "rank": 11,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Brezza",
        "slug": "maruti-brezza",
        "search_aliases": ["brezza"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://imgd.aeplcdn.com/664x374/n/cw/ec/212741/2026-brezza-exterior-left-rear-three-quarter-2.jpeg?isig=0&q=80&q=80",
        "model_year": 2025,
        "variants": [
            {"name": "LXi 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 834000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "VXi 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 970000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "ZXi 1.5L Smart Hybrid AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1254000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "ZXi Plus 1.5L AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1398000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "VXi S-CNG 1.5L MT", "fuel": "CNG", "trans": "MANUAL", "price": 1065000, "engine": "1462 cc", "power": "88 PS", "seating": 5}
        ]
    },
    {
        "rank": 12,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Celerio",
        "slug": "maruti-suzuki-celerio",
        "search_aliases": ["celerio"],
        "body_type": "Hatchback",
        "category_slug": "car",
        "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-celerio_600x400.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "LXi 1.0L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 536500, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "VXi 1.0L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 583500, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "ZXi 1.0L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 611500, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "ZXi Plus 1.0L AGS", "fuel": "PETROL", "trans": "AMT", "price": 709500, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "VXi S-CNG 1.0L MT", "fuel": "CNG", "trans": "MANUAL", "price": 673500, "engine": "998 cc", "power": "57 PS", "seating": 5}
        ]
    },
    {
        "rank": 13,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Eeco",
        "slug": "maruti-suzuki-eeco",
        "search_aliases": ["eeco"],
        "body_type": "Van / MPV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS1Us6EROvGM0sAe03ew63plLcX61l_4qNYTVTMT-NmGzaBo6GfOrMWLEo&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "5-Seater Standard MT", "fuel": "PETROL", "trans": "MANUAL", "price": 532000, "engine": "1197 cc", "power": "81 PS", "seating": 5},
            {"name": "7-Seater Standard MT", "fuel": "PETROL", "trans": "MANUAL", "price": 561000, "engine": "1197 cc", "power": "81 PS", "seating": 7},
            {"name": "5-Seater AC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 568000, "engine": "1197 cc", "power": "81 PS", "seating": 5},
            {"name": "5-Seater AC S-CNG MT", "fuel": "CNG", "trans": "MANUAL", "price": 658000, "engine": "1197 cc", "power": "72 PS", "seating": 5}
        ]
    },
    {
        "rank": 14,
        "brand_name": "Hyundai",
        "name": "Hyundai Venue",
        "slug": "hyundai-venue",
        "search_aliases": ["venue"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://imgd.aeplcdn.com/1280x720/n/cw/ec/195343/venue-exterior-left-front-three-quarter.jpeg?isig=0",
        "model_year": 2025,
        "variants": [
            {"name": "E 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 794000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "S 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 911000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "SX 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1105000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "SX(O) 1.0L Turbo DCT", "fuel": "PETROL", "trans": "DCT", "price": 1348000, "engine": "998 cc Turbo", "power": "120 PS", "seating": 5},
            {"name": "SX 1.5L CRDi Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1242000, "engine": "1493 cc", "power": "116 PS", "seating": 5}
        ]
    },
    {
        "rank": 15,
        "brand_name": "Kia",
        "name": "Kia Seltos",
        "slug": "kia-seltos",
        "search_aliases": ["seltos"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://www.kia.com/us/en/vehicles/seltos-hybrid/2027/_jcr_content/root/responsivegrid/fiftyfifty_copy_428320636.coreimg.jpeg/1780513367695/my27-seltos-hev-mep-lite-5050-feature-highlights.jpeg",
        "model_year": 2025,
        "variants": [
            {"name": "HTE 1.5L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1090000, "engine": "1497 cc", "power": "115 PS", "seating": 5},
            {"name": "HTK Plus 1.5L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1360000, "engine": "1497 cc", "power": "115 PS", "seating": 5},
            {"name": "HTX 1.5L Petrol IVT", "fuel": "PETROL", "trans": "CVT", "price": 1660000, "engine": "1497 cc", "power": "115 PS", "seating": 5},
            {"name": "GTX Plus 1.5L Turbo DCT", "fuel": "PETROL", "trans": "DCT", "price": 2000000, "engine": "1482 cc Turbo", "power": "160 PS", "seating": 5},
            {"name": "X-Line 1.5L Diesel AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2035000, "engine": "1493 cc", "power": "116 PS", "seating": 5}
        ]
    },
    {
        "rank": 16,
        "brand_name": "Mahindra",
        "name": "Mahindra Thar",
        "slug": "mahindra-thar",
        "search_aliases": ["thar"],
        "body_type": "Off-Road SUV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsR9UcpPWhGdBJfDtIUOnV0Y08SN5QqWxos0JoMI3pVg&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "AX(O) 1.5L RWD Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1135000, "engine": "1497 cc", "power": "118 PS", "seating": 4},
            {"name": "LX 1.5L RWD Diesel MT HardTop", "fuel": "DIESEL", "trans": "MANUAL", "price": 1285000, "engine": "1497 cc", "power": "118 PS", "seating": 4},
            {"name": "LX 2.0L 4x4 Petrol AT HardTop", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1660000, "engine": "1997 cc Turbo", "power": "152 PS", "seating": 4},
            {"name": "LX 2.2L 4x4 Diesel AT HardTop", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 1760000, "engine": "2184 cc", "power": "132 PS", "seating": 4}
        ]
    },
    {
        "rank": 17,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Alto K10",
        "slug": "maruti-suzuki-alto-k10",
        "search_aliases": ["alto", "alto k10"],
        "body_type": "Hatchback",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSK2bmE3xRadnVUx9CAB6Wn0j38uxopJHdr_uakC2sd_A&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Std 1.0L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 399000, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "LXi 1.0L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 483000, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "VXi 1.0L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 506000, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "VXi Plus 1.0L AGS", "fuel": "PETROL", "trans": "AMT", "price": 585000, "engine": "998 cc", "power": "67 PS", "seating": 5},
            {"name": "VXi S-CNG 1.0L MT", "fuel": "CNG", "trans": "MANUAL", "price": 596000, "engine": "998 cc", "power": "57 PS", "seating": 5}
        ]
    },
    {
        "rank": 18,
        "brand_name": "Kia",
        "name": "Kia Sonet",
        "slug": "kia-sonet",
        "search_aliases": ["sonet"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://imgcdn.zigwheels.vn/large/gallery/exterior/12/1065/kia-sonet-21269.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "HTE 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 799000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "HTK Plus 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 990000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "HTX 1.0L Turbo iMT", "fuel": "PETROL", "trans": "AMT", "price": 1150000, "engine": "998 cc Turbo", "power": "120 PS", "seating": 5},
            {"name": "GTX Plus 1.0L Turbo DCT", "fuel": "PETROL", "trans": "DCT", "price": 1475000, "engine": "998 cc Turbo", "power": "120 PS", "seating": 5},
            {"name": "X-Line 1.5L Diesel AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 1575000, "engine": "1493 cc", "power": "116 PS", "seating": 5}
        ]
    },
    {
        "rank": 19,
        "brand_name": "Mahindra",
        "name": "Mahindra Bolero",
        "slug": "mahindra-bolero",
        "search_aliases": ["bolero"],
        "body_type": "Rugged SUV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYLB1p5A_3KOAKc4dfuY6z06SfCD_-t5mOX3hcLTrvv_4M6oDqVWsMDaM&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "B4 1.5L mHawk75 MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 979000, "engine": "1498 cc", "power": "75 PS", "seating": 7},
            {"name": "B6 1.5L mHawk75 MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1000000, "engine": "1498 cc", "power": "75 PS", "seating": 7},
            {"name": "B6(O) 1.5L mHawk75 MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1091000, "engine": "1498 cc", "power": "75 PS", "seating": 7}
        ]
    },
    {
        "rank": 20,
        "brand_name": "Toyota",
        "name": "Toyota Innova",
        "slug": "toyota-innova",
        "search_aliases": ["innova", "innova crysta", "innova hycross"],
        "body_type": "Premium MPV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4ylvUdR-fpNSWJoTnYqG9h7wqKHv6IEZjSJLYgAZdTA&s",
        "model_year": 2025,
        "variants": [
            {"name": "GX 2.4L Diesel MT 7-Str", "fuel": "DIESEL", "trans": "MANUAL", "price": 1999000, "engine": "2393 cc", "power": "150 PS", "seating": 7},
            {"name": "VX 2.4L Diesel MT 7-Str", "fuel": "DIESEL", "trans": "MANUAL", "price": 2464000, "engine": "2393 cc", "power": "150 PS", "seating": 7},
            {"name": "ZX 2.4L Diesel MT 7-Str", "fuel": "DIESEL", "trans": "MANUAL", "price": 2630000, "engine": "2393 cc", "power": "150 PS", "seating": 7},
            {"name": "Hycross VX Hybrid e-Drive", "fuel": "HYBRID", "trans": "CVT", "price": 2597000, "engine": "1987 cc Hybrid", "power": "186 PS", "seating": 7},
            {"name": "Hycross ZX(O) Hybrid", "fuel": "HYBRID", "trans": "CVT", "price": 3098000, "engine": "1987 cc Hybrid", "power": "186 PS", "seating": 7}
        ]
    },
    {
        "rank": 21,
        "brand_name": "Mahindra",
        "name": "Mahindra XUV 3XO",
        "slug": "mahindra-xuv-3xo",
        "search_aliases": ["xuv 3xo", "xuv3xo"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://imgd.aeplcdn.com/1920x1080/n/cw/ec/156405/xuv-3xo-exterior-right-front-three-quarter-492.jpeg?isig=0&q=80&q=80",
        "model_year": 2025,
        "variants": [
            {"name": "MX1 1.2L mStallion Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 779000, "engine": "1197 cc Turbo", "power": "111 PS", "seating": 5},
            {"name": "MX2 Pro 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 899000, "engine": "1197 cc Turbo", "power": "111 PS", "seating": 5},
            {"name": "AX5 1.2L Turbo AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1219000, "engine": "1197 cc Turbo", "power": "130 PS", "seating": 5},
            {"name": "AX7 Luxury 1.2L TGDi AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1549000, "engine": "1197 cc Turbo", "power": "130 PS", "seating": 5}
        ]
    },
    {
        "rank": 22,
        "brand_name": "Mahindra",
        "name": "Mahindra XUV700",
        "slug": "mahindra-xuv700",
        "search_aliases": ["xuv700"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://mc.bajajfinserv.in/media/catalog/product/a/x/ax7l_everest_white_1366x443_.jpeg",
        "model_year": 2025,
        "variants": [
            {"name": "MX 2.0L Petrol MT 5-Str", "fuel": "PETROL", "trans": "MANUAL", "price": 1399000, "engine": "1997 cc Turbo", "power": "200 PS", "seating": 5},
            {"name": "AX5 2.2L Diesel MT 7-Str", "fuel": "DIESEL", "trans": "MANUAL", "price": 1879000, "engine": "2198 cc", "power": "185 PS", "seating": 7},
            {"name": "AX7 2.2L Diesel AT 7-Str", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2399000, "engine": "2198 cc", "power": "185 PS", "seating": 7},
            {"name": "AX7L AWD Diesel AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2699000, "engine": "2198 cc", "power": "185 PS", "seating": 7}
        ]
    },
    {
        "rank": 23,
        "brand_name": "Maruti Suzuki",
        "name": "Maruti Suzuki Grand Vitara",
        "slug": "maruti-suzuki-grand-vitara",
        "search_aliases": ["grand vitara"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://media.zigcdn.com/media/model/2026/Mar/maruti-grandvitara_600x400.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Sigma 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1099000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "Delta 1.5L Smart Hybrid MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1219000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "Zeta 1.5L Smart Hybrid AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1539000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "Alpha 1.5L AllGrip 4x4 MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1701000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "Alpha Plus Strong Hybrid e-CVT", "fuel": "HYBRID", "trans": "CVT", "price": 2009000, "engine": "1490 cc Hybrid", "power": "116 PS", "seating": 5}
        ]
    },
    {
        "rank": 24,
        "brand_name": "Tata Motors",
        "name": "Tata Tiago",
        "slug": "tata-tiago",
        "search_aliases": ["tiago"],
        "body_type": "Hatchback",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSV6W8E6oAI3xqfg50L9ZGSQ3PrjDbp9jtHQWZduI8kIAwpdUcI5RFc2lZe&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "XE 1.2L Revotron MT", "fuel": "PETROL", "trans": "MANUAL", "price": 500000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XT 1.2L Revotron MT", "fuel": "PETROL", "trans": "MANUAL", "price": 600000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XZ Plus 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 780000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XT iCNG Twin Cylinder", "fuel": "CNG", "trans": "MANUAL", "price": 695000, "engine": "1199 cc", "power": "73.5 PS", "seating": 5}
        ]
    },
    {
        "rank": 25,
        "brand_name": "Toyota",
        "name": "Toyota Urban Cruiser Hyryder",
        "slug": "toyota-urban-cruiser-hyryder",
        "search_aliases": ["hyryder", "urban cruiser"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://cdn-s3.autocarindia.com/Toyota/urban-cruiser-taisor/_AAB2126.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "E NeoDrive 1.5L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1114000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "S NeoDrive 1.5L AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1381000, "engine": "1462 cc", "power": "103 PS", "seating": 5},
            {"name": "G Strong Hybrid e-CVT", "fuel": "HYBRID", "trans": "CVT", "price": 1849000, "engine": "1490 cc Hybrid", "power": "116 PS", "seating": 5},
            {"name": "V Strong Hybrid e-CVT", "fuel": "HYBRID", "trans": "CVT", "price": 1999000, "engine": "1490 cc Hybrid", "power": "116 PS", "seating": 5}
        ]
    },
    {
        "rank": 26,
        "brand_name": "Hyundai",
        "name": "Hyundai Aura",
        "slug": "hyundai-aura",
        "search_aliases": ["aura"],
        "body_type": "Compact Sedan",
        "category_slug": "car",
        "image_url": "https://media.zigcdn.com/media/model/2026/Feb/hyundai_aura_600x400.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "E 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 649000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "S 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 733000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "SX Plus 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 890000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "SX 1.2L Bi-Fuel CNG", "fuel": "CNG", "trans": "MANUAL", "price": 905000, "engine": "1197 cc", "power": "69 PS", "seating": 5}
        ]
    },
    {
        "rank": 27,
        "brand_name": "Kia",
        "name": "Kia Carens",
        "slug": "kia-carens",
        "search_aliases": ["carens"],
        "body_type": "MPV",
        "category_slug": "car",
        "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Kia/Carens/11623/1772787448187/front-left-side-47.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Premium 1.5L Petrol MT 7-Str", "fuel": "PETROL", "trans": "MANUAL", "price": 1052000, "engine": "1497 cc", "power": "115 PS", "seating": 7},
            {"name": "Prestige Plus 1.5L Turbo iMT", "fuel": "PETROL", "trans": "AMT", "price": 1495000, "engine": "1482 cc Turbo", "power": "160 PS", "seating": 7},
            {"name": "Luxury Plus 1.5L Turbo DCT 6-Str", "fuel": "PETROL", "trans": "DCT", "price": 1895000, "engine": "1482 cc Turbo", "power": "160 PS", "seating": 6},
            {"name": "Luxury Plus 1.5L Diesel AT 7-Str", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 1967000, "engine": "1493 cc", "power": "116 PS", "seating": 7}
        ]
    },
    {
        "rank": 28,
        "brand_name": "Hyundai",
        "name": "Hyundai i20",
        "slug": "hyundai-i20",
        "search_aliases": ["i20"],
        "body_type": "Premium Hatchback",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT51_PnPJj-zUbpBk1at8ltAdrMbOotb4eW17tdjY9osFscjr-tiVBuqD4&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Era 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 704000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "Magna 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 775000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "Sportz 1.2L IVT", "fuel": "PETROL", "trans": "CVT", "price": 943000, "engine": "1197 cc", "power": "88 PS", "seating": 5},
            {"name": "Asta(O) 1.2L IVT", "fuel": "PETROL", "trans": "CVT", "price": 1121000, "engine": "1197 cc", "power": "88 PS", "seating": 5}
        ]
    },
    {
        "rank": 29,
        "brand_name": "Tata Motors",
        "name": "Tata Altroz",
        "slug": "tata-altroz",
        "search_aliases": ["altroz"],
        "body_type": "Premium Hatchback",
        "category_slug": "car",
        "image_url": "https://cdn-s3.autocarindia.com/legacy/cdni/Galleries/20250522033443_New_Tata_Altroz_Front_Quarter_Static.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "XE 1.2L Revotron Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 665000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XM Plus 1.2L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 760000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XZ Plus 1.2L DCA Automatic", "fuel": "PETROL", "trans": "DCT", "price": 1000000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XZ Plus 1.5L Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1080000, "engine": "1497 cc", "power": "90 PS", "seating": 5},
            {"name": "XM Plus iCNG Twin Cylinder", "fuel": "CNG", "trans": "MANUAL", "price": 845000, "engine": "1199 cc", "power": "73.5 PS", "seating": 5}
        ]
    },
    {
        "rank": 30,
        "brand_name": "Honda",
        "name": "Honda Amaze",
        "slug": "honda-amaze",
        "search_aliases": ["amaze"],
        "body_type": "Compact Sedan",
        "category_slug": "car",
        "image_url": "https://imgd.aeplcdn.com/664x374/n/cw/ec/184377/amaze-2024-exterior-left-rear-three-quarter.jpeg?isig=0&q=80&q=80",
        "model_year": 2025,
        "variants": [
            {"name": "E 1.2L i-VTEC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 720000, "engine": "1199 cc", "power": "90 PS", "seating": 5},
            {"name": "S 1.2L i-VTEC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 787000, "engine": "1199 cc", "power": "90 PS", "seating": 5},
            {"name": "S 1.2L i-VTEC CVT", "fuel": "PETROL", "trans": "CVT", "price": 877000, "engine": "1199 cc", "power": "90 PS", "seating": 5},
            {"name": "VX 1.2L i-VTEC CVT", "fuel": "PETROL", "trans": "CVT", "price": 996000, "engine": "1199 cc", "power": "90 PS", "seating": 5}
        ]
    },
    {
        "rank": 31,
        "brand_name": "Tata Motors",
        "name": "Tata Tigor",
        "slug": "tata-tigor",
        "search_aliases": ["tigor"],
        "body_type": "Compact Sedan",
        "category_slug": "car",
        "image_url": "https://www.lakshmitata.co.in/blog/wp-content/uploads/2025/07/tata-tigor-compact-sedan.webp",
        "model_year": 2025,
        "variants": [
            {"name": "XE 1.2L Revotron MT", "fuel": "PETROL", "trans": "MANUAL", "price": 630000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XM 1.2L Revotron MT", "fuel": "PETROL", "trans": "MANUAL", "price": 680000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XZ Plus 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 850000, "engine": "1199 cc", "power": "86 PS", "seating": 5},
            {"name": "XZ Plus iCNG Twin Cylinder", "fuel": "CNG", "trans": "MANUAL", "price": 895000, "engine": "1199 cc", "power": "73.5 PS", "seating": 5}
        ]
    },
    {
        "rank": 32,
        "brand_name": "Hyundai",
        "name": "Hyundai Grand i10 Nios",
        "slug": "hyundai-grand-i10-nios",
        "search_aliases": ["grand i10", "i10 nios", "grand i10 nios"],
        "body_type": "Hatchback",
        "category_slug": "car",
        "image_url": "https://cdn-s3.autocarindia.com/legacy/cdni/ExtraImages/20190807103020_2019-Hyundai-Grand-i10.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Era 1.2L Kappa MT", "fuel": "PETROL", "trans": "MANUAL", "price": 592000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "Magna 1.2L Kappa MT", "fuel": "PETROL", "trans": "MANUAL", "price": 678000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "Sportz 1.2L Kappa AMT", "fuel": "PETROL", "trans": "AMT", "price": 793000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "Asta 1.2L Kappa AMT", "fuel": "PETROL", "trans": "AMT", "price": 856000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "Magna Bi-Fuel CNG MT", "fuel": "CNG", "trans": "MANUAL", "price": 775000, "engine": "1197 cc", "power": "69 PS", "seating": 5}
        ]
    },
    {
        "rank": 33,
        "brand_name": "Tata Motors",
        "name": "Tata Safari",
        "slug": "tata-safari",
        "search_aliases": ["safari"],
        "body_type": "3-Row Premium SUV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtl9uety5UF8xSOll0KoM56sAv7XRtZeR85gG7oHQ6MdbNYlhXKNCFolM&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Smart 2.0L Kryotec Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1619000, "engine": "1956 cc", "power": "170 PS", "seating": 7},
            {"name": "Pure Plus 2.0L Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1939000, "engine": "1956 cc", "power": "170 PS", "seating": 7},
            {"name": "Adventure Plus Dark AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2349000, "engine": "1956 cc", "power": "170 PS", "seating": 7},
            {"name": "Accomplished Plus Dark 6-Str AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2734000, "engine": "1956 cc", "power": "170 PS", "seating": 6}
        ]
    },
    {
        "rank": 34,
        "brand_name": "Tata Motors",
        "name": "Tata Harrier",
        "slug": "tata-harrier",
        "search_aliases": ["harrier"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRPQzRrGxwXht-CKPDCZPDnytCPrQq8i8Dpp9SDHTJlVPsOBSSbA2MwTIt4&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Smart 2.0L Kryotec Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1549000, "engine": "1956 cc", "power": "170 PS", "seating": 5},
            {"name": "Pure Plus 2.0L Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 1869000, "engine": "1956 cc", "power": "170 PS", "seating": 5},
            {"name": "Adventure Plus Dark AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2329000, "engine": "1956 cc", "power": "170 PS", "seating": 5},
            {"name": "Fearless Plus Dark AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2644000, "engine": "1956 cc", "power": "170 PS", "seating": 5}
        ]
    },
    {
        "rank": 35,
        "brand_name": "Skoda",
        "name": "Skoda Kylaq",
        "slug": "skoda-kylaq",
        "search_aliases": ["kylaq"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://www.motorbeam.com/wp-content/uploads/Skoda-Kylaq-Anniversary-Edition-front.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Classic 1.0L TSI MT", "fuel": "PETROL", "trans": "MANUAL", "price": 789000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Signature 1.0L TSI MT", "fuel": "PETROL", "trans": "MANUAL", "price": 959000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Signature Plus 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1140000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Prestige 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1440000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5}
        ]
    },
    {
        "rank": 36,
        "brand_name": "Hyundai",
        "name": "Hyundai Exter",
        "slug": "hyundai-exter",
        "search_aliases": ["exter"],
        "body_type": "Micro SUV",
        "category_slug": "car",
        "image_url": "https://media.zigcdn.com/media/content/2023/May/64589ce676e8d.jpg?tr=w-420",
        "model_year": 2025,
        "variants": [
            {"name": "EX 1.2L Kappa Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 613000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "S 1.2L Kappa Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 750000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "SX 1.2L Kappa Smart AMT", "fuel": "PETROL", "trans": "AMT", "price": 890000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "SX(O) Connect 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 1043000, "engine": "1197 cc", "power": "83 PS", "seating": 5},
            {"name": "S Dual-Cylinder Hy-CNG", "fuel": "CNG", "trans": "MANUAL", "price": 843000, "engine": "1197 cc", "power": "69 PS", "seating": 5}
        ]
    },
    {
        "rank": 37,
        "brand_name": "Honda",
        "name": "Honda Elevate",
        "slug": "honda-elevate",
        "search_aliases": ["elevate"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://akm-img-a-in.tosshub.com/indiatoday/images/story/202610/honda-elevate-facelift-065047535-16x9.jpg?VersionId=mOVv0oAjkNUV4_cyJJv5wfWO2wgmwkad&size=1280:720",
        "model_year": 2025,
        "variants": [
            {"name": "SV 1.5L i-VTEC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1169000, "engine": "1498 cc", "power": "121 PS", "seating": 5},
            {"name": "V 1.5L i-VTEC CVT", "fuel": "PETROL", "trans": "CVT", "price": 1351000, "engine": "1498 cc", "power": "121 PS", "seating": 5},
            {"name": "VX 1.5L i-VTEC MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1399000, "engine": "1498 cc", "power": "121 PS", "seating": 5},
            {"name": "ZX 1.5L i-VTEC CVT ADAS", "fuel": "PETROL", "trans": "CVT", "price": 1631000, "engine": "1498 cc", "power": "121 PS", "seating": 5}
        ]
    },
    {
        "rank": 38,
        "brand_name": "Volkswagen",
        "name": "Volkswagen Virtus",
        "slug": "volkswagen-virtus",
        "search_aliases": ["virtus"],
        "body_type": "Premium Sedan",
        "category_slug": "car",
        "image_url": "https://assets.volkswagen.com/is/image/volkswagenag/Virtus_Price%20Section%201920x1080?Zm10PXBuZy1hbHBoYSZ3aWQ9ODAwJmJmYz1vZmYmMGFmYw==",
        "model_year": 2025,
        "variants": [
            {"name": "Comfortline 1.0L TSI MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1156000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Highline 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1488000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Topline 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1685000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "GT Plus 1.5L TSI DSG", "fuel": "PETROL", "trans": "DCT", "price": 1941000, "engine": "1498 cc Turbo", "power": "150 PS", "seating": 5}
        ]
    },
    {
        "rank": 39,
        "brand_name": "Skoda",
        "name": "Skoda Slavia",
        "slug": "skoda-slavia",
        "search_aliases": ["slavia"],
        "body_type": "Premium Sedan",
        "category_slug": "car",
        "image_url": "https://asset.autocarindia.com/static/news/images/20261006_064415_070fff14.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Classic 1.0L TSI MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1163000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Signature 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1499000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Prestige 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1699000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Monte Carlo 1.5L TSI DSG", "fuel": "PETROL", "trans": "DCT", "price": 1912000, "engine": "1498 cc Turbo", "power": "150 PS", "seating": 5}
        ]
    },
    {
        "rank": 40,
        "brand_name": "Toyota",
        "name": "Toyota Glanza",
        "slug": "toyota-glanza",
        "search_aliases": ["glanza"],
        "body_type": "Premium Hatchback",
        "category_slug": "car",
        "image_url": "https://imgd.aeplcdn.com/1920x1080/n/cw/ec/221362/glanza-facelift-exterior-right-front-three-quarter-6.jpeg?isig=0&q=80&q=80",
        "model_year": 2025,
        "variants": [
            {"name": "E 1.2L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 686000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "S 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 823000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "G 1.2L MT", "fuel": "PETROL", "trans": "MANUAL", "price": 878000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "V 1.2L AMT", "fuel": "PETROL", "trans": "AMT", "price": 1000000, "engine": "1197 cc", "power": "90 PS", "seating": 5},
            {"name": "S E-CNG 1.2L MT", "fuel": "CNG", "trans": "MANUAL", "price": 865000, "engine": "1197 cc", "power": "77.5 PS", "seating": 5}
        ]
    },
    {
        "rank": 41,
        "brand_name": "Volkswagen",
        "name": "Volkswagen Taigun",
        "slug": "volkswagen-taigun",
        "search_aliases": ["taigun"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Volkswagen/Taigun/13468/1778063618610/front-view-118.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Comfortline 1.0L TSI MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1170000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Highline 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1540000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Topline 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1760000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "GT Plus Edge 1.5L DSG", "fuel": "PETROL", "trans": "DCT", "price": 2000000, "engine": "1498 cc Turbo", "power": "150 PS", "seating": 5}
        ]
    },
    {
        "rank": 42,
        "brand_name": "Skoda",
        "name": "Skoda Kushaq",
        "slug": "skoda-kushaq",
        "search_aliases": ["kushaq"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://cdn-s3.autocarindia.com/Skoda/kushaq/Skoda-Kushaq-front-quarter.jpg?w=728&q=75&fm=auto",
        "model_year": 2025,
        "variants": [
            {"name": "Classic 1.0L TSI MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1189000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Signature 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1559000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Prestige 1.0L TSI AT", "fuel": "PETROL", "trans": "AUTOMATIC", "price": 1789000, "engine": "999 cc Turbo", "power": "115 PS", "seating": 5},
            {"name": "Monte Carlo 1.5L TSI DSG", "fuel": "PETROL", "trans": "DCT", "price": 2049000, "engine": "1498 cc Turbo", "power": "150 PS", "seating": 5}
        ]
    },
    {
        "rank": 43,
        "brand_name": "MG Motor",
        "name": "MG Hector",
        "slug": "mg-hector",
        "search_aliases": ["hector"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/MG/Hector/13125/1765801652897/exterior-image-164.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Style 1.5L Turbo MT", "fuel": "PETROL", "trans": "MANUAL", "price": 1399000, "engine": "1451 cc Turbo", "power": "143 PS", "seating": 5},
            {"name": "Shine Pro 1.5L CVT", "fuel": "PETROL", "trans": "CVT", "price": 1717000, "engine": "1451 cc Turbo", "power": "143 PS", "seating": 5},
            {"name": "Sharp Pro 2.0L Diesel MT", "fuel": "DIESEL", "trans": "MANUAL", "price": 2170000, "engine": "1956 cc", "power": "170 PS", "seating": 5},
            {"name": "Savvy Pro 1.5L CVT ADAS", "fuel": "PETROL", "trans": "CVT", "price": 2245000, "engine": "1451 cc Turbo", "power": "143 PS", "seating": 5}
        ]
    },
    {
        "rank": 44,
        "brand_name": "MG Motor",
        "name": "MG Windsor EV",
        "slug": "mg-windsor-ev",
        "search_aliases": ["windsor", "windsor ev"],
        "body_type": "Electric Crossover",
        "category_slug": "electric-vehicle",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQdatfWSPwzrydW8b36K1Orp1RWujgpK53XocHo917nsO69bQ7G5q6lbq4b&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Excite 38 kWh EV", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1350000, "engine": "38 kWh", "power": "136 PS", "seating": 5},
            {"name": "Exclusive 38 kWh EV", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1450000, "engine": "38 kWh", "power": "136 PS", "seating": 5},
            {"name": "Essence 38 kWh EV", "fuel": "ELECTRIC", "trans": "SINGLE_SPEED_EV", "price": 1550000, "engine": "38 kWh", "power": "136 PS", "seating": 5}
        ]
    },
    {
        "rank": 45,
        "brand_name": "Mahindra",
        "name": "Mahindra Scorpio Classic",
        "slug": "mahindra-scorpio-classic",
        "search_aliases": ["scorpio classic"],
        "body_type": "Mid-size SUV",
        "category_slug": "car",
        "image_url": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Mahindra/Scorpio/10764/1778474504907/front-left-side-47.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Classic S 2.2L mHawk MT 7-Str", "fuel": "DIESEL", "trans": "MANUAL", "price": 1362000, "engine": "2184 cc", "power": "132 PS", "seating": 7},
            {"name": "Classic S11 2.2L mHawk MT 7-Str", "fuel": "DIESEL", "trans": "MANUAL", "price": 1742000, "engine": "2184 cc", "power": "132 PS", "seating": 7}
        ]
    },
    {
        "rank": 46,
        "brand_name": "Nissan",
        "name": "Nissan Magnite",
        "slug": "nissan-magnite",
        "search_aliases": ["magnite"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUG5jjeKcy7L-F15v5LPdp03K5OkMUw1eB7HUKXOPZCoIGMBcy27Eg4c29&s=10",
        "model_year": 2025,
        "variants": [
            {"name": "Visia 1.0L B4D Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 599000, "engine": "999 cc", "power": "72 PS", "seating": 5},
            {"name": "Acenta 1.0L Petrol MT", "fuel": "PETROL", "trans": "MANUAL", "price": 714000, "engine": "999 cc", "power": "72 PS", "seating": 5},
            {"name": "N-Connecta 1.0L Turbo CVT", "fuel": "PETROL", "trans": "CVT", "price": 979000, "engine": "999 cc Turbo", "power": "100 PS", "seating": 5},
            {"name": "Tekna Plus 1.0L Turbo CVT", "fuel": "PETROL", "trans": "CVT", "price": 1150000, "engine": "999 cc Turbo", "power": "100 PS", "seating": 5}
        ]
    },
    {
        "rank": 47,
        "brand_name": "Renault",
        "name": "Renault Triber",
        "slug": "renault-triber",
        "search_aliases": ["triber"],
        "body_type": "Compact MPV",
        "category_slug": "car",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/2021_Renault_Triber_RXZ_%28Indonesia%29_front_view.jpg?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=original",
        "model_year": 2025,
        "variants": [
            {"name": "RXE 1.0L Energy MT 7-Str", "fuel": "PETROL", "trans": "MANUAL", "price": 600000, "engine": "999 cc", "power": "72 PS", "seating": 7},
            {"name": "RXL 1.0L Energy MT 7-Str", "fuel": "PETROL", "trans": "MANUAL", "price": 680000, "engine": "999 cc", "power": "72 PS", "seating": 7},
            {"name": "RXT 1.0L EASY-R AMT 7-Str", "fuel": "PETROL", "trans": "AMT", "price": 788000, "engine": "999 cc", "power": "72 PS", "seating": 7},
            {"name": "RXZ 1.0L EASY-R AMT 7-Str", "fuel": "PETROL", "trans": "AMT", "price": 897000, "engine": "999 cc", "power": "72 PS", "seating": 7}
        ]
    },
    {
        "rank": 48,
        "brand_name": "Renault",
        "name": "Renault Kiger",
        "slug": "renault-kiger",
        "search_aliases": ["kiger"],
        "body_type": "Compact SUV",
        "category_slug": "car",
        "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Renault/Kiger/12295/1764934839670/front-left-side-47.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "RXE 1.0L Energy MT", "fuel": "PETROL", "trans": "MANUAL", "price": 600000, "engine": "999 cc", "power": "72 PS", "seating": 5},
            {"name": "RXT(O) 1.0L Energy MT", "fuel": "PETROL", "trans": "MANUAL", "price": 800000, "engine": "999 cc", "power": "72 PS", "seating": 5},
            {"name": "RXZ 1.0L Turbo CVT", "fuel": "PETROL", "trans": "CVT", "price": 1123000, "engine": "999 cc Turbo", "power": "100 PS", "seating": 5}
        ]
    },
    {
        "rank": 49,
        "brand_name": "Toyota",
        "name": "Toyota Fortuner",
        "slug": "toyota-fortuner",
        "search_aliases": ["fortuner"],
        "body_type": "Full-size SUV",
        "category_slug": "car",
        "image_url": "https://auto.economictimes.indiatimes.com/files/retail_files/fortuner-1665472907-prod-var.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "2.7L Petrol 4x2 MT", "fuel": "PETROL", "trans": "MANUAL", "price": 3343000, "engine": "2694 cc", "power": "166 PS", "seating": 7},
            {"name": "2.8L Diesel 4x2 AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 3821000, "engine": "2755 cc", "power": "204 PS", "seating": 7},
            {"name": "2.8L Diesel 4x4 AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 4232000, "engine": "2755 cc", "power": "204 PS", "seating": 7},
            {"name": "Legender 2.8L 4x4 AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 4764000, "engine": "2755 cc", "power": "204 PS", "seating": 7},
            {"name": "GR-S 2.8L 4x4 AT", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 5144000, "engine": "2755 cc", "power": "204 PS", "seating": 7}
        ]
    },
    {
        "rank": 50,
        "brand_name": "Hyundai",
        "name": "Hyundai Alcazar",
        "slug": "hyundai-alcazar",
        "search_aliases": ["alcazar"],
        "body_type": "3-Row Premium SUV",
        "category_slug": "car",
        "image_url": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Hyundai/Alcazar/9246/1758802404168/front-left-side-47.jpg",
        "model_year": 2025,
        "variants": [
            {"name": "Executive 1.5L Turbo Petrol MT 7-Str", "fuel": "PETROL", "trans": "MANUAL", "price": 1499000, "engine": "1482 cc Turbo", "power": "160 PS", "seating": 7},
            {"name": "Prestige 1.5L CRDi Diesel MT 7-Str", "fuel": "DIESEL", "trans": "MANUAL", "price": 1599000, "engine": "1493 cc", "power": "116 PS", "seating": 7},
            {"name": "Platinum 1.5L Turbo DCT 6-Str", "fuel": "PETROL", "trans": "DCT", "price": 1960000, "engine": "1482 cc Turbo", "power": "160 PS", "seating": 6},
            {"name": "Signature 1.5L CRDi Diesel AT 6-Str", "fuel": "DIESEL", "trans": "AUTOMATIC", "price": 2155000, "engine": "1493 cc", "power": "116 PS", "seating": 6}
        ]
    }
]

async def seed_top_50():
    async with AsyncSessionLocal() as db:
        print(f"[TOP-50 SEED] Seeding and updating all 50 top-selling cars with exact images and verified prices...")

        # Pre-cache brands
        b_res = await db.execute(select(VehicleBrand))
        brands = {b.name.lower(): b for b in b_res.scalars().all()}
        # Aliases
        if "tata motors" in brands:
            brands["tata"] = brands["tata motors"]
        if "mg motor" in brands:
            brands["mg"] = brands["mg motor"]

        # Pre-cache categories
        cat_car = (await db.execute(select(VehicleCategory).where(VehicleCategory.slug == "car"))).scalars().first()
        cat_ev = (await db.execute(select(VehicleCategory).where(VehicleCategory.slug == "electric-vehicle"))).scalars().first() or cat_car

        updated_count = 0
        created_count = 0

        for car in TOP_50_CARS:
            brand = brands.get(car["brand_name"].lower())
            if not brand:
                print(f"Warning: Brand {car['brand_name']} not found, skipping {car['name']}")
                continue

            target_cat = cat_ev if car["category_slug"] == "electric-vehicle" else cat_car

            # Try to match existing model by:
            # 1. Exact name or slug
            # 2. Search aliases in model name under this brand
            model = None
            res = await db.execute(
                select(VehicleModel).where(
                    or_(
                        VehicleModel.name == car["name"],
                        VehicleModel.slug == car["slug"]
                    )
                )
            )
            model = res.scalars().first()

            if not model:
                # Search by brand + aliases
                for alias in car["search_aliases"]:
                    res_alias = await db.execute(
                        select(VehicleModel).where(
                            VehicleModel.brand_id == brand.id,
                            or_(
                                VehicleModel.name.ilike(f"{alias}"),
                                VehicleModel.name.ilike(f"{alias} %"),
                                VehicleModel.name.ilike(f"% {alias}"),
                                VehicleModel.name.ilike(f"{car['brand_name']} {alias}%")
                            )
                        )
                    )
                    candidates = res_alias.scalars().all()
                    if candidates:
                        # Prefer one that doesn't have multiple extra words
                        candidates.sort(key=lambda m: len(m.name))
                        model = candidates[0]
                        break

            if model:
                # Update model with clean standardized name, exact image_url, body_type
                model.name = car["name"]
                model.image_url = car["image_url"]
                model.body_type = car["body_type"]
                model.vehicle_category_slug = car["category_slug"]
                model.canonical_brand_name = car["brand_name"]
                model.canonical_model_name = car["name"].replace(car["brand_name"], "").strip()
                model.is_active = True
                model.last_verified_at = datetime.now(timezone.utc)
                await db.flush()
                updated_count += 1
            else:
                # Create brand new model
                model = VehicleModel(
                    brand_id=brand.id,
                    name=car["name"],
                    slug=car["slug"],
                    vehicle_category_slug=car["category_slug"],
                    body_type=car["body_type"],
                    model_year=car["model_year"],
                    canonical_brand_name=car["brand_name"],
                    canonical_model_name=car["name"].replace(car["brand_name"], "").strip(),
                    image_url=car["image_url"],
                    is_active=True,
                    last_verified_at=datetime.now(timezone.utc)
                )
                db.add(model)
                await db.flush()
                created_count += 1

            # Seed rich official variants
            # Check existing variants
            v_res = await db.execute(select(VehicleVariant).where(VehicleVariant.model_id == model.id))
            existing_variants = {v.name.lower(): v for v in v_res.scalars().all()}

            for v in car["variants"]:
                v_name = v["name"]
                if v_name.lower() in existing_variants:
                    ev = existing_variants[v_name.lower()]
                    ev.fuel_type = v["fuel"]
                    ev.transmission = v["trans"]
                    ev.reference_ex_showroom = Decimal(str(v["price"]))
                    ev.engine_cc_or_battery_kwh = v.get("engine")
                    ev.seating_capacity = v.get("seating", 5)
                    ev.is_active = True
                else:
                    db.add(
                        VehicleVariant(
                            model_id=model.id,
                            name=v_name,
                            fuel_type=v["fuel"],
                            transmission=v["trans"],
                            seating_capacity=v.get("seating", 5),
                            engine_cc_or_battery_kwh=v.get("engine"),
                            reference_ex_showroom=Decimal(str(v["price"])),
                            specifications=v,
                            source_priority=1,
                            is_active=True,
                            last_verified_at=datetime.now(timezone.utc)
                        )
                    )

        await db.commit()
        print(f"[TOP-50 SEED] Complete! Updated: {updated_count}, Created: {created_count}. Total: {len(TOP_50_CARS)} top-selling cars ready.")

if __name__ == "__main__":
    asyncio.run(seed_top_50())

