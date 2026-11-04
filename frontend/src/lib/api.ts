// API Client with automatic proxy, multi-target resolution, and resilient fallback

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

// Fallback catalog cache for maximum resiliency in case backend is initializing
export const FALLBACK_CATEGORIES = [
  { id: 'ca000000-0000-4000-8000-000000000001', slug: 'car', name: 'Passenger Cars', description: 'Hatchbacks, Sedans, Compact & Mid-size SUVs', icon_name: 'Car', display_order: 1 },
  { id: 'ca000000-0000-4000-8000-000000000002', slug: 'electric-vehicle', name: 'Electric Vehicles', description: 'Electric Scooters, Electric Cars & Commercial EVs', icon_name: 'Zap', display_order: 2 },
  { id: 'ca000000-0000-4000-8000-000000000003', slug: 'two-wheeler', name: 'Two-Wheelers', description: 'Commuter & Premium Motorcycles and Scooters', icon_name: 'Bike', display_order: 3 },
  { id: 'ca000000-0000-4000-8000-000000000004', slug: 'commercial-vehicle', name: 'Commercial Vehicles', description: 'Pickups, Small Commercial Vehicles & Trucks', icon_name: 'Truck', display_order: 4 },
  { id: 'ca000000-0000-4000-8000-000000000005', slug: 'three-wheeler', name: 'Three-Wheelers', description: 'Passenger & Cargo Auto-rickshaws', icon_name: 'Boxes', display_order: 5 }
];

export const FALLBACK_CITIES = [
  { id: 'c0000000-0000-4000-8000-000000000001', name: 'Indore', state: 'Madhya Pradesh', pincode_prefix: '452', is_active: true },
  { id: 'c0000000-0000-4000-8000-000000000002', name: 'Bhopal', state: 'Madhya Pradesh', pincode_prefix: '462', is_active: true }
];

export const FALLBACK_BRANDS = [
  { id: 'b0000000-0000-4000-8000-000000000001', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Tata Motors', slug: 'tata-motors' },
  { id: 'b0000000-0000-4000-8000-000000000002', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Maruti Suzuki', slug: 'maruti-suzuki' },
  { id: 'b0000000-0000-4000-8000-000000000003', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Mahindra', slug: 'mahindra' },
  { id: 'b0000000-0000-4000-8000-000000000004', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Hyundai', slug: 'hyundai' },
  { id: 'b0000000-0000-4000-8000-000000000005', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Kia', slug: 'kia' },
  { id: 'b0000000-0000-4000-8000-000000000006', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Toyota', slug: 'toyota' },
  { id: 'b0000000-0000-4000-8000-000000000012', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Honda', slug: 'honda' },
  { id: 'b0000000-0000-4000-8000-000000000013', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Skoda', slug: 'skoda' },
  { id: 'b0000000-0000-4000-8000-000000000014', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Volkswagen', slug: 'volkswagen' },
  { id: 'b0000000-0000-4000-8000-000000000015', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'MG Motor', slug: 'mg' },
  { id: 'b0000000-0000-4000-8000-000000000016', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Renault', slug: 'renault' },
  { id: 'b0000000-0000-4000-8000-000000000017', category_id: 'ca000000-0000-4000-8000-000000000001', name: 'Nissan', slug: 'nissan' },
  { id: 'b0000000-0000-4000-8000-000000000007', category_id: 'ca000000-0000-4000-8000-000000000002', name: 'Ather Energy', slug: 'ather-energy' },
  { id: 'b0000000-0000-4000-8000-000000000008', category_id: 'ca000000-0000-4000-8000-000000000002', name: 'Ola Electric', slug: 'ola-electric' },
  { id: 'b0000000-0000-4000-8000-000000000009', category_id: 'ca000000-0000-4000-8000-000000000003', name: 'Royal Enfield', slug: 'royal-enfield' },
  { id: 'b0000000-0000-4000-8000-000000000010', category_id: 'ca000000-0000-4000-8000-000000000003', name: 'TVS Motor', slug: 'tvs-motor' },
  { id: 'b0000000-0000-4000-8000-000000000011', category_id: 'ca000000-0000-4000-8000-000000000004', name: 'Ashok Leyland', slug: 'ashok-leyland' }
];

export const FALLBACK_MODELS = [
  {
    "id": "m0000000-0000-0000-0000-000000000001",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Baleno",
    "slug": "maruti-suzuki-baleno",
    "body_type": "Hatchback",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcj0XBX8QgG4bAL2SIsWQ9n8DLdTqutGfsS6e-bJDy2Q&s=10",
    "is_active": true,
    "min_price": 666000,
    "max_price": 988000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0001-00000001",
        "name": "Sigma 1.2L DualJet MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 666000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0001-00000002",
        "name": "Delta 1.2L DualJet MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 750000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0001-00000003",
        "name": "Zeta 1.2L DualJet MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 843000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0001-00000004",
        "name": "Alpha 1.2L DualJet AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 988000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0001-00000005",
        "name": "Delta S-CNG 1.2L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 840000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "77.5 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000002",
    "brand_id": "b0000000-0000-0000-0000-000000000001",
    "brand_name": "Tata Motors",
    "category_slug": "car",
    "name": "Tata Nexon",
    "slug": "tata-nexon",
    "body_type": "Compact SUV",
    "image_url": "https://asset.autocarindia.com/static/news/images/20260908_073502_5ec713cb.png?w=420",
    "is_active": true,
    "min_price": 800000,
    "max_price": 1490000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0002-00000001",
        "name": "Smart 1.2L Turbo MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 800000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "120 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0002-00000002",
        "name": "Pure 1.2L Turbo MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 970000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "120 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0002-00000003",
        "name": "Creative Plus 1.2L Turbo MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1170000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "120 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0002-00000004",
        "name": "Fearless Plus DCA Petrol",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1490000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "120 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0002-00000005",
        "name": "Pure 1.5L Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1110000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000003",
    "brand_id": "b0000000-0000-0000-0000-000000000001",
    "brand_name": "Tata Motors",
    "category_slug": "car",
    "name": "Tata Punch",
    "slug": "tata-punch",
    "body_type": "Micro SUV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQI1RZHFzAYbLC_nKDxyTbKhiLnn4u9RlBon0I_fjLQqQ&s=10",
    "is_active": true,
    "min_price": 613000,
    "max_price": 1020000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0003-00000001",
        "name": "Pure 1.2L Revotron MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 613000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0003-00000002",
        "name": "Adventure Rhythm 1.2L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 725000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0003-00000003",
        "name": "Accomplished Dazzle 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 885000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0003-00000004",
        "name": "Creative Flagship 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 1020000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0003-00000005",
        "name": "Adventure iCNG Twin Cylinder",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 795000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "73.5 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000004",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Fronx",
    "slug": "maruti-suzuki-fronx",
    "body_type": "Compact SUV",
    "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-fronx_600x400.jpg",
    "is_active": true,
    "min_price": 751000,
    "max_price": 1304000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0004-00000001",
        "name": "Sigma 1.2L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 751000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0004-00000002",
        "name": "Delta 1.2L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 837000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0004-00000003",
        "name": "Zeta 1.0L Turbo Boosterjet AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1205000,
        "engine_cc_or_battery_kwh": "998 cc Turbo",
        "specifications": {
          "power": "100 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0004-00000004",
        "name": "Alpha 1.0L Turbo Boosterjet AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1304000,
        "engine_cc_or_battery_kwh": "998 cc Turbo",
        "specifications": {
          "power": "100 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0004-00000005",
        "name": "Sigma S-CNG 1.2L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 846000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "77.5 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000005",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Wagon R",
    "slug": "maruti-suzuki-wagon-r",
    "body_type": "Hatchback",
    "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-wagon-r_600x400.jpg",
    "is_active": true,
    "min_price": 554500,
    "max_price": 738000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0005-00000001",
        "name": "LXi 1.0L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 554500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0005-00000002",
        "name": "VXi 1.0L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 599500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0005-00000003",
        "name": "ZXi 1.2L DualJet MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 628000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0005-00000004",
        "name": "ZXi Plus 1.2L AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 738000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0005-00000005",
        "name": "LXi S-CNG 1.0L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 644500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "57 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000006",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Dzire",
    "slug": "maruti-suzuki-dzire",
    "body_type": "Compact Sedan",
    "image_url": "https://www.spinny.com/blog/wp-content/uploads/2024/11/New-Maruti-Suzuki-Dzire-1-jpg.webp",
    "is_active": true,
    "min_price": 679000,
    "max_price": 1014000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0006-00000001",
        "name": "LXi 1.2L Z-Series MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 679000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0006-00000002",
        "name": "VXi 1.2L Z-Series MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 779000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0006-00000003",
        "name": "ZXi 1.2L AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 889000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0006-00000004",
        "name": "ZXi Plus 1.2L AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 1014000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0006-00000005",
        "name": "VXi S-CNG 1.2L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 874000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "70 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000007",
    "brand_id": "b0000000-0000-0000-0000-000000000004",
    "brand_name": "Hyundai",
    "category_slug": "car",
    "name": "Hyundai Creta",
    "slug": "hyundai-creta",
    "body_type": "Mid-size SUV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTeE54tQtEGGH_3t6ylCcZ8idM2YjLpUx3qyq68iYLLIJX4O-T1KqT43MxU&s=10",
    "is_active": true,
    "min_price": 1100000,
    "max_price": 2015000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0007-00000001",
        "name": "E 1.5L MPi Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1100000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0007-00000002",
        "name": "EX 1.5L MPi Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1221000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0007-00000003",
        "name": "S(O) 1.5L Petrol IVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1438000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0007-00000004",
        "name": "SX 1.5L CRDi Diesel AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1820000,
        "engine_cc_or_battery_kwh": "1493 cc",
        "specifications": {
          "power": "116 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0007-00000005",
        "name": "SX(O) 1.5L Turbo Petrol DCT",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 2015000,
        "engine_cc_or_battery_kwh": "1482 cc Turbo",
        "specifications": {
          "power": "160 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000008",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Swift",
    "slug": "maruti-suzuki-swift",
    "body_type": "Hatchback",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqPufqmyo-UJOHWK5jrsKi9CoLc7V-peHEGJYjd5kqLQ&s=10",
    "is_active": true,
    "min_price": 649000,
    "max_price": 959500,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0008-00000001",
        "name": "LXi 1.2L Z-Series MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 649000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0008-00000002",
        "name": "VXi 1.2L Z-Series MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 729500,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0008-00000003",
        "name": "ZXi 1.2L AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 875000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0008-00000004",
        "name": "ZXi Plus 1.2L AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 959500,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "82 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0008-00000005",
        "name": "VXi S-CNG 1.2L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 819500,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "70 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000009",
    "brand_id": "b0000000-0000-0000-0000-000000000003",
    "brand_name": "Mahindra",
    "category_slug": "car",
    "name": "Mahindra Scorpio",
    "slug": "mahindra-scorpio-n",
    "body_type": "Mid-size SUV",
    "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Mahindra/Scorpio-N/13740/1785926288341/front-left-side-47.jpg",
    "is_active": true,
    "min_price": 1360000,
    "max_price": 2454000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0009-00000001",
        "name": "Z2 2.2L mHawk Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1360000,
        "engine_cc_or_battery_kwh": "2198 cc",
        "specifications": {
          "power": "132 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0009-00000002",
        "name": "Z4 2.2L mHawk Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1585000,
        "engine_cc_or_battery_kwh": "2198 cc",
        "specifications": {
          "power": "175 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0009-00000003",
        "name": "Z8 2.0L mStallion Petrol AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2049000,
        "engine_cc_or_battery_kwh": "1997 cc Turbo",
        "specifications": {
          "power": "203 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0009-00000004",
        "name": "Z8L 2.2L mHawk 4x4 AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2454000,
        "engine_cc_or_battery_kwh": "2198 cc",
        "specifications": {
          "power": "175 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000010",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Ertiga",
    "slug": "maruti-suzuki-ertiga",
    "body_type": "MPV",
    "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-ertiga_600x400.jpg",
    "is_active": true,
    "min_price": 869000,
    "max_price": 1303000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0010-00000001",
        "name": "LXi 1.5L Smart Hybrid MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 869000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0010-00000002",
        "name": "VXi 1.5L Smart Hybrid MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 983000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0010-00000003",
        "name": "ZXi 1.5L Smart Hybrid AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1233000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0010-00000004",
        "name": "ZXi Plus 1.5L AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1303000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0010-00000005",
        "name": "VXi S-CNG 1.5L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1078000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "88 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000011",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Brezza",
    "slug": "maruti-brezza",
    "body_type": "Compact SUV",
    "image_url": "https://imgd.aeplcdn.com/664x374/n/cw/ec/212741/2026-brezza-exterior-left-rear-three-quarter-2.jpeg?isig=0&q=80&q=80",
    "is_active": true,
    "min_price": 834000,
    "max_price": 1398000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0011-00000001",
        "name": "LXi 1.5L Smart Hybrid MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 834000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0011-00000002",
        "name": "VXi 1.5L Smart Hybrid MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 970000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0011-00000003",
        "name": "ZXi 1.5L Smart Hybrid AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1254000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0011-00000004",
        "name": "ZXi Plus 1.5L AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1398000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0011-00000005",
        "name": "VXi S-CNG 1.5L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1065000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "88 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000012",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Celerio",
    "slug": "maruti-suzuki-celerio",
    "body_type": "Hatchback",
    "image_url": "https://media.zigcdn.com/media/model/2026/Aug/maruti-suzuki-celerio_600x400.jpg",
    "is_active": true,
    "min_price": 536500,
    "max_price": 709500,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0012-00000001",
        "name": "LXi 1.0L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 536500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0012-00000002",
        "name": "VXi 1.0L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 583500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0012-00000003",
        "name": "ZXi 1.0L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 611500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0012-00000004",
        "name": "ZXi Plus 1.0L AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 709500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0012-00000005",
        "name": "VXi S-CNG 1.0L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 673500,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "57 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000013",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Eeco",
    "slug": "maruti-suzuki-eeco",
    "body_type": "Van / MPV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS1Us6EROvGM0sAe03ew63plLcX61l_4qNYTVTMT-NmGzaBo6GfOrMWLEo&s=10",
    "is_active": true,
    "min_price": 532000,
    "max_price": 658000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0013-00000001",
        "name": "5-Seater Standard MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 532000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "81 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0013-00000002",
        "name": "7-Seater Standard MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 561000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "81 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0013-00000003",
        "name": "5-Seater AC MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 568000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "81 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0013-00000004",
        "name": "5-Seater AC S-CNG MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 658000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "72 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000014",
    "brand_id": "b0000000-0000-0000-0000-000000000004",
    "brand_name": "Hyundai",
    "category_slug": "car",
    "name": "Hyundai Venue",
    "slug": "hyundai-venue",
    "body_type": "Compact SUV",
    "image_url": "https://imgd.aeplcdn.com/1280x720/n/cw/ec/195343/venue-exterior-left-front-three-quarter.jpeg?isig=0",
    "is_active": true,
    "min_price": 794000,
    "max_price": 1348000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0014-00000001",
        "name": "E 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 794000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0014-00000002",
        "name": "S 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 911000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0014-00000003",
        "name": "SX 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1105000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0014-00000004",
        "name": "SX(O) 1.0L Turbo DCT",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1348000,
        "engine_cc_or_battery_kwh": "998 cc Turbo",
        "specifications": {
          "power": "120 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0014-00000005",
        "name": "SX 1.5L CRDi Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1242000,
        "engine_cc_or_battery_kwh": "1493 cc",
        "specifications": {
          "power": "116 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000015",
    "brand_id": "b0000000-0000-0000-0000-000000000005",
    "brand_name": "Kia",
    "category_slug": "car",
    "name": "Kia Seltos",
    "slug": "kia-seltos",
    "body_type": "Mid-size SUV",
    "image_url": "https://www.kia.com/us/en/vehicles/seltos-hybrid/2027/_jcr_content/root/responsivegrid/fiftyfifty_copy_428320636.coreimg.jpeg/1780513367695/my27-seltos-hev-mep-lite-5050-feature-highlights.jpeg",
    "is_active": true,
    "min_price": 1090000,
    "max_price": 2035000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0015-00000001",
        "name": "HTE 1.5L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1090000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0015-00000002",
        "name": "HTK Plus 1.5L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1360000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0015-00000003",
        "name": "HTX 1.5L Petrol IVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1660000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0015-00000004",
        "name": "GTX Plus 1.5L Turbo DCT",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 2000000,
        "engine_cc_or_battery_kwh": "1482 cc Turbo",
        "specifications": {
          "power": "160 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0015-00000005",
        "name": "X-Line 1.5L Diesel AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2035000,
        "engine_cc_or_battery_kwh": "1493 cc",
        "specifications": {
          "power": "116 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000016",
    "brand_id": "b0000000-0000-0000-0000-000000000003",
    "brand_name": "Mahindra",
    "category_slug": "car",
    "name": "Mahindra Thar",
    "slug": "mahindra-thar",
    "body_type": "Off-Road SUV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsR9UcpPWhGdBJfDtIUOnV0Y08SN5QqWxos0JoMI3pVg&s=10",
    "is_active": true,
    "min_price": 1135000,
    "max_price": 1760000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0016-00000001",
        "name": "AX(O) 1.5L RWD Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1135000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "118 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0016-00000002",
        "name": "LX 1.5L RWD Diesel MT HardTop",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1285000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "118 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0016-00000003",
        "name": "LX 2.0L 4x4 Petrol AT HardTop",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1660000,
        "engine_cc_or_battery_kwh": "1997 cc Turbo",
        "specifications": {
          "power": "152 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0016-00000004",
        "name": "LX 2.2L 4x4 Diesel AT HardTop",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1760000,
        "engine_cc_or_battery_kwh": "2184 cc",
        "specifications": {
          "power": "132 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000017",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Alto K10",
    "slug": "maruti-suzuki-alto-k10",
    "body_type": "Hatchback",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSK2bmE3xRadnVUx9CAB6Wn0j38uxopJHdr_uakC2sd_A&s=10",
    "is_active": true,
    "min_price": 399000,
    "max_price": 596000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0017-00000001",
        "name": "Std 1.0L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 399000,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0017-00000002",
        "name": "LXi 1.0L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 483000,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0017-00000003",
        "name": "VXi 1.0L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 506000,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0017-00000004",
        "name": "VXi Plus 1.0L AGS",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 585000,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "67 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0017-00000005",
        "name": "VXi S-CNG 1.0L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 596000,
        "engine_cc_or_battery_kwh": "998 cc",
        "specifications": {
          "power": "57 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000018",
    "brand_id": "b0000000-0000-0000-0000-000000000005",
    "brand_name": "Kia",
    "category_slug": "car",
    "name": "Kia Sonet",
    "slug": "kia-sonet",
    "body_type": "Compact SUV",
    "image_url": "https://imgcdn.zigwheels.vn/large/gallery/exterior/12/1065/kia-sonet-21269.jpg",
    "is_active": true,
    "min_price": 799000,
    "max_price": 1575000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0018-00000001",
        "name": "HTE 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 799000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0018-00000002",
        "name": "HTK Plus 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 990000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0018-00000003",
        "name": "HTX 1.0L Turbo iMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 1150000,
        "engine_cc_or_battery_kwh": "998 cc Turbo",
        "specifications": {
          "power": "120 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0018-00000004",
        "name": "GTX Plus 1.0L Turbo DCT",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1475000,
        "engine_cc_or_battery_kwh": "998 cc Turbo",
        "specifications": {
          "power": "120 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0018-00000005",
        "name": "X-Line 1.5L Diesel AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1575000,
        "engine_cc_or_battery_kwh": "1493 cc",
        "specifications": {
          "power": "116 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000019",
    "brand_id": "b0000000-0000-0000-0000-000000000003",
    "brand_name": "Mahindra",
    "category_slug": "car",
    "name": "Mahindra Bolero",
    "slug": "mahindra-bolero",
    "body_type": "Rugged SUV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYLB1p5A_3KOAKc4dfuY6z06SfCD_-t5mOX3hcLTrvv_4M6oDqVWsMDaM&s=10",
    "is_active": true,
    "min_price": 979000,
    "max_price": 1091000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0019-00000001",
        "name": "B4 1.5L mHawk75 MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 979000,
        "engine_cc_or_battery_kwh": "1498 cc",
        "specifications": {
          "power": "75 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0019-00000002",
        "name": "B6 1.5L mHawk75 MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1000000,
        "engine_cc_or_battery_kwh": "1498 cc",
        "specifications": {
          "power": "75 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0019-00000003",
        "name": "B6(O) 1.5L mHawk75 MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1091000,
        "engine_cc_or_battery_kwh": "1498 cc",
        "specifications": {
          "power": "75 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000020",
    "brand_id": "b0000000-0000-0000-0000-000000000006",
    "brand_name": "Toyota",
    "category_slug": "car",
    "name": "Toyota Innova",
    "slug": "toyota-innova",
    "body_type": "Premium MPV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4ylvUdR-fpNSWJoTnYqG9h7wqKHv6IEZjSJLYgAZdTA&s",
    "is_active": true,
    "min_price": 1999000,
    "max_price": 3098000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0020-00000001",
        "name": "GX 2.4L Diesel MT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1999000,
        "engine_cc_or_battery_kwh": "2393 cc",
        "specifications": {
          "power": "150 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0020-00000002",
        "name": "VX 2.4L Diesel MT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 2464000,
        "engine_cc_or_battery_kwh": "2393 cc",
        "specifications": {
          "power": "150 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0020-00000003",
        "name": "ZX 2.4L Diesel MT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 2630000,
        "engine_cc_or_battery_kwh": "2393 cc",
        "specifications": {
          "power": "150 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0020-00000004",
        "name": "Hycross VX Hybrid e-Drive",
        "fuel_type": "HYBRID",
        "transmission": "CVT",
        "reference_ex_showroom": 2597000,
        "engine_cc_or_battery_kwh": "1987 cc Hybrid",
        "specifications": {
          "power": "186 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0020-00000005",
        "name": "Hycross ZX(O) Hybrid",
        "fuel_type": "HYBRID",
        "transmission": "CVT",
        "reference_ex_showroom": 3098000,
        "engine_cc_or_battery_kwh": "1987 cc Hybrid",
        "specifications": {
          "power": "186 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000021",
    "brand_id": "b0000000-0000-0000-0000-000000000003",
    "brand_name": "Mahindra",
    "category_slug": "car",
    "name": "Mahindra XUV 3XO",
    "slug": "mahindra-xuv-3xo",
    "body_type": "Compact SUV",
    "image_url": "https://imgd.aeplcdn.com/1920x1080/n/cw/ec/156405/xuv-3xo-exterior-right-front-three-quarter-492.jpeg?isig=0&q=80&q=80",
    "is_active": true,
    "min_price": 779000,
    "max_price": 1549000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0021-00000001",
        "name": "MX1 1.2L mStallion Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 779000,
        "engine_cc_or_battery_kwh": "1197 cc Turbo",
        "specifications": {
          "power": "111 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0021-00000002",
        "name": "MX2 Pro 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 899000,
        "engine_cc_or_battery_kwh": "1197 cc Turbo",
        "specifications": {
          "power": "111 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0021-00000003",
        "name": "AX5 1.2L Turbo AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1219000,
        "engine_cc_or_battery_kwh": "1197 cc Turbo",
        "specifications": {
          "power": "130 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0021-00000004",
        "name": "AX7 Luxury 1.2L TGDi AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1549000,
        "engine_cc_or_battery_kwh": "1197 cc Turbo",
        "specifications": {
          "power": "130 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000022",
    "brand_id": "b0000000-0000-0000-0000-000000000003",
    "brand_name": "Mahindra",
    "category_slug": "car",
    "name": "Mahindra XUV700",
    "slug": "mahindra-xuv700",
    "body_type": "Mid-size SUV",
    "image_url": "https://mc.bajajfinserv.in/media/catalog/product/a/x/ax7l_everest_white_1366x443_.jpeg",
    "is_active": true,
    "min_price": 1399000,
    "max_price": 2699000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0022-00000001",
        "name": "MX 2.0L Petrol MT 5-Str",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1399000,
        "engine_cc_or_battery_kwh": "1997 cc Turbo",
        "specifications": {
          "power": "200 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0022-00000002",
        "name": "AX5 2.2L Diesel MT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1879000,
        "engine_cc_or_battery_kwh": "2198 cc",
        "specifications": {
          "power": "185 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0022-00000003",
        "name": "AX7 2.2L Diesel AT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2399000,
        "engine_cc_or_battery_kwh": "2198 cc",
        "specifications": {
          "power": "185 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0022-00000004",
        "name": "AX7L AWD Diesel AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2699000,
        "engine_cc_or_battery_kwh": "2198 cc",
        "specifications": {
          "power": "185 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000023",
    "brand_id": "b0000000-0000-0000-0000-000000000002",
    "brand_name": "Maruti Suzuki",
    "category_slug": "car",
    "name": "Maruti Suzuki Grand Vitara",
    "slug": "maruti-suzuki-grand-vitara",
    "body_type": "Mid-size SUV",
    "image_url": "https://media.zigcdn.com/media/model/2026/Mar/maruti-grandvitara_600x400.jpg",
    "is_active": true,
    "min_price": 1099000,
    "max_price": 2009000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0023-00000001",
        "name": "Sigma 1.5L Smart Hybrid MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1099000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0023-00000002",
        "name": "Delta 1.5L Smart Hybrid MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1219000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0023-00000003",
        "name": "Zeta 1.5L Smart Hybrid AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1539000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0023-00000004",
        "name": "Alpha 1.5L AllGrip 4x4 MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1701000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0023-00000005",
        "name": "Alpha Plus Strong Hybrid e-CVT",
        "fuel_type": "HYBRID",
        "transmission": "CVT",
        "reference_ex_showroom": 2009000,
        "engine_cc_or_battery_kwh": "1490 cc Hybrid",
        "specifications": {
          "power": "116 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000024",
    "brand_id": "b0000000-0000-0000-0000-000000000001",
    "brand_name": "Tata Motors",
    "category_slug": "car",
    "name": "Tata Tiago",
    "slug": "tata-tiago",
    "body_type": "Hatchback",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSV6W8E6oAI3xqfg50L9ZGSQ3PrjDbp9jtHQWZduI8kIAwpdUcI5RFc2lZe&s=10",
    "is_active": true,
    "min_price": 500000,
    "max_price": 780000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0024-00000001",
        "name": "XE 1.2L Revotron MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 500000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0024-00000002",
        "name": "XT 1.2L Revotron MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 600000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0024-00000003",
        "name": "XZ Plus 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 780000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0024-00000004",
        "name": "XT iCNG Twin Cylinder",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 695000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "73.5 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000025",
    "brand_id": "b0000000-0000-0000-0000-000000000006",
    "brand_name": "Toyota",
    "category_slug": "car",
    "name": "Toyota Urban Cruiser Hyryder",
    "slug": "toyota-urban-cruiser-hyryder",
    "body_type": "Mid-size SUV",
    "image_url": "https://cdn-s3.autocarindia.com/Toyota/urban-cruiser-taisor/_AAB2126.jpg",
    "is_active": true,
    "min_price": 1114000,
    "max_price": 1999000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0025-00000001",
        "name": "E NeoDrive 1.5L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1114000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0025-00000002",
        "name": "S NeoDrive 1.5L AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1381000,
        "engine_cc_or_battery_kwh": "1462 cc",
        "specifications": {
          "power": "103 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0025-00000003",
        "name": "G Strong Hybrid e-CVT",
        "fuel_type": "HYBRID",
        "transmission": "CVT",
        "reference_ex_showroom": 1849000,
        "engine_cc_or_battery_kwh": "1490 cc Hybrid",
        "specifications": {
          "power": "116 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0025-00000004",
        "name": "V Strong Hybrid e-CVT",
        "fuel_type": "HYBRID",
        "transmission": "CVT",
        "reference_ex_showroom": 1999000,
        "engine_cc_or_battery_kwh": "1490 cc Hybrid",
        "specifications": {
          "power": "116 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000026",
    "brand_id": "b0000000-0000-0000-0000-000000000004",
    "brand_name": "Hyundai",
    "category_slug": "car",
    "name": "Hyundai Aura",
    "slug": "hyundai-aura",
    "body_type": "Compact Sedan",
    "image_url": "https://media.zigcdn.com/media/model/2026/Feb/hyundai_aura_600x400.jpg",
    "is_active": true,
    "min_price": 649000,
    "max_price": 905000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0026-00000001",
        "name": "E 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 649000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0026-00000002",
        "name": "S 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 733000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0026-00000003",
        "name": "SX Plus 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 890000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0026-00000004",
        "name": "SX 1.2L Bi-Fuel CNG",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 905000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "69 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000027",
    "brand_id": "b0000000-0000-0000-0000-000000000005",
    "brand_name": "Kia",
    "category_slug": "car",
    "name": "Kia Carens",
    "slug": "kia-carens",
    "body_type": "MPV",
    "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Kia/Carens/11623/1772787448187/front-left-side-47.jpg",
    "is_active": true,
    "min_price": 1052000,
    "max_price": 1967000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0027-00000001",
        "name": "Premium 1.5L Petrol MT 7-Str",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1052000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0027-00000002",
        "name": "Prestige Plus 1.5L Turbo iMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 1495000,
        "engine_cc_or_battery_kwh": "1482 cc Turbo",
        "specifications": {
          "power": "160 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0027-00000003",
        "name": "Luxury Plus 1.5L Turbo DCT 6-Str",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1895000,
        "engine_cc_or_battery_kwh": "1482 cc Turbo",
        "specifications": {
          "power": "160 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0027-00000004",
        "name": "Luxury Plus 1.5L Diesel AT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1967000,
        "engine_cc_or_battery_kwh": "1493 cc",
        "specifications": {
          "power": "116 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000028",
    "brand_id": "b0000000-0000-0000-0000-000000000004",
    "brand_name": "Hyundai",
    "category_slug": "car",
    "name": "Hyundai i20",
    "slug": "hyundai-i20",
    "body_type": "Premium Hatchback",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT51_PnPJj-zUbpBk1at8ltAdrMbOotb4eW17tdjY9osFscjr-tiVBuqD4&s=10",
    "is_active": true,
    "min_price": 704000,
    "max_price": 1121000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0028-00000001",
        "name": "Era 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 704000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0028-00000002",
        "name": "Magna 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 775000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0028-00000003",
        "name": "Sportz 1.2L IVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 943000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "88 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0028-00000004",
        "name": "Asta(O) 1.2L IVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1121000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "88 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000029",
    "brand_id": "b0000000-0000-0000-0000-000000000001",
    "brand_name": "Tata Motors",
    "category_slug": "car",
    "name": "Tata Altroz",
    "slug": "tata-altroz",
    "body_type": "Premium Hatchback",
    "image_url": "https://cdn-s3.autocarindia.com/legacy/cdni/Galleries/20250522033443_New_Tata_Altroz_Front_Quarter_Static.jpg",
    "is_active": true,
    "min_price": 665000,
    "max_price": 1080000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0029-00000001",
        "name": "XE 1.2L Revotron Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 665000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0029-00000002",
        "name": "XM Plus 1.2L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 760000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0029-00000003",
        "name": "XZ Plus 1.2L DCA Automatic",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1000000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0029-00000004",
        "name": "XZ Plus 1.5L Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1080000,
        "engine_cc_or_battery_kwh": "1497 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0029-00000005",
        "name": "XM Plus iCNG Twin Cylinder",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 845000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "73.5 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000030",
    "brand_id": "b0000000-0000-0000-0000-000000000012",
    "brand_name": "Honda",
    "category_slug": "car",
    "name": "Honda Amaze",
    "slug": "honda-amaze",
    "body_type": "Compact Sedan",
    "image_url": "https://imgd.aeplcdn.com/664x374/n/cw/ec/184377/amaze-2024-exterior-left-rear-three-quarter.jpeg?isig=0&q=80&q=80",
    "is_active": true,
    "min_price": 720000,
    "max_price": 996000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0030-00000001",
        "name": "E 1.2L i-VTEC MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 720000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0030-00000002",
        "name": "S 1.2L i-VTEC MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 787000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0030-00000003",
        "name": "S 1.2L i-VTEC CVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 877000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0030-00000004",
        "name": "VX 1.2L i-VTEC CVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 996000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "90 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000031",
    "brand_id": "b0000000-0000-0000-0000-000000000001",
    "brand_name": "Tata Motors",
    "category_slug": "car",
    "name": "Tata Tigor",
    "slug": "tata-tigor",
    "body_type": "Compact Sedan",
    "image_url": "https://www.lakshmitata.co.in/blog/wp-content/uploads/2025/07/tata-tigor-compact-sedan.webp",
    "is_active": true,
    "min_price": 630000,
    "max_price": 895000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0031-00000001",
        "name": "XE 1.2L Revotron MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 630000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0031-00000002",
        "name": "XM 1.2L Revotron MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 680000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0031-00000003",
        "name": "XZ Plus 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 850000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "86 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0031-00000004",
        "name": "XZ Plus iCNG Twin Cylinder",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 895000,
        "engine_cc_or_battery_kwh": "1199 cc",
        "specifications": {
          "power": "73.5 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000032",
    "brand_id": "b0000000-0000-0000-0000-000000000004",
    "brand_name": "Hyundai",
    "category_slug": "car",
    "name": "Hyundai Grand i10 Nios",
    "slug": "hyundai-grand-i10-nios",
    "body_type": "Hatchback",
    "image_url": "https://cdn-s3.autocarindia.com/legacy/cdni/ExtraImages/20190807103020_2019-Hyundai-Grand-i10.jpg",
    "is_active": true,
    "min_price": 592000,
    "max_price": 856000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0032-00000001",
        "name": "Era 1.2L Kappa MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 592000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0032-00000002",
        "name": "Magna 1.2L Kappa MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 678000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0032-00000003",
        "name": "Sportz 1.2L Kappa AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 793000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0032-00000004",
        "name": "Asta 1.2L Kappa AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 856000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0032-00000005",
        "name": "Magna Bi-Fuel CNG MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 775000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "69 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000033",
    "brand_id": "b0000000-0000-0000-0000-000000000001",
    "brand_name": "Tata Motors",
    "category_slug": "car",
    "name": "Tata Safari",
    "slug": "tata-safari",
    "body_type": "3-Row Premium SUV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtl9uety5UF8xSOll0KoM56sAv7XRtZeR85gG7oHQ6MdbNYlhXKNCFolM&s=10",
    "is_active": true,
    "min_price": 1619000,
    "max_price": 2734000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0033-00000001",
        "name": "Smart 2.0L Kryotec Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1619000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0033-00000002",
        "name": "Pure Plus 2.0L Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1939000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0033-00000003",
        "name": "Adventure Plus Dark AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2349000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0033-00000004",
        "name": "Accomplished Plus Dark 6-Str AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2734000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000034",
    "brand_id": "b0000000-0000-0000-0000-000000000001",
    "brand_name": "Tata Motors",
    "category_slug": "car",
    "name": "Tata Harrier",
    "slug": "tata-harrier",
    "body_type": "Mid-size SUV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRPQzRrGxwXht-CKPDCZPDnytCPrQq8i8Dpp9SDHTJlVPsOBSSbA2MwTIt4&s=10",
    "is_active": true,
    "min_price": 1549000,
    "max_price": 2644000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0034-00000001",
        "name": "Smart 2.0L Kryotec Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1549000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0034-00000002",
        "name": "Pure Plus 2.0L Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1869000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0034-00000003",
        "name": "Adventure Plus Dark AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2329000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0034-00000004",
        "name": "Fearless Plus Dark AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2644000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000035",
    "brand_id": "b0000000-0000-0000-0000-000000000013",
    "brand_name": "Skoda",
    "category_slug": "car",
    "name": "Skoda Kylaq",
    "slug": "skoda-kylaq",
    "body_type": "Compact SUV",
    "image_url": "https://www.motorbeam.com/wp-content/uploads/Skoda-Kylaq-Anniversary-Edition-front.jpg",
    "is_active": true,
    "min_price": 789000,
    "max_price": 1440000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0035-00000001",
        "name": "Classic 1.0L TSI MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 789000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0035-00000002",
        "name": "Signature 1.0L TSI MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 959000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0035-00000003",
        "name": "Signature Plus 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1140000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0035-00000004",
        "name": "Prestige 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1440000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000036",
    "brand_id": "b0000000-0000-0000-0000-000000000004",
    "brand_name": "Hyundai",
    "category_slug": "car",
    "name": "Hyundai Exter",
    "slug": "hyundai-exter",
    "body_type": "Micro SUV",
    "image_url": "https://media.zigcdn.com/media/content/2023/May/64589ce676e8d.jpg?tr=w-420",
    "is_active": true,
    "min_price": 613000,
    "max_price": 1043000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0036-00000001",
        "name": "EX 1.2L Kappa Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 613000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0036-00000002",
        "name": "S 1.2L Kappa Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 750000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0036-00000003",
        "name": "SX 1.2L Kappa Smart AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 890000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0036-00000004",
        "name": "SX(O) Connect 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 1043000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "83 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0036-00000005",
        "name": "S Dual-Cylinder Hy-CNG",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 843000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "69 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000037",
    "brand_id": "b0000000-0000-0000-0000-000000000012",
    "brand_name": "Honda",
    "category_slug": "car",
    "name": "Honda Elevate",
    "slug": "honda-elevate",
    "body_type": "Mid-size SUV",
    "image_url": "https://akm-img-a-in.tosshub.com/indiatoday/images/story/202610/honda-elevate-facelift-065047535-16x9.jpg?VersionId=mOVv0oAjkNUV4_cyJJv5wfWO2wgmwkad&size=1280:720",
    "is_active": true,
    "min_price": 1169000,
    "max_price": 1631000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0037-00000001",
        "name": "SV 1.5L i-VTEC MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1169000,
        "engine_cc_or_battery_kwh": "1498 cc",
        "specifications": {
          "power": "121 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0037-00000002",
        "name": "V 1.5L i-VTEC CVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1351000,
        "engine_cc_or_battery_kwh": "1498 cc",
        "specifications": {
          "power": "121 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0037-00000003",
        "name": "VX 1.5L i-VTEC MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1399000,
        "engine_cc_or_battery_kwh": "1498 cc",
        "specifications": {
          "power": "121 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0037-00000004",
        "name": "ZX 1.5L i-VTEC CVT ADAS",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1631000,
        "engine_cc_or_battery_kwh": "1498 cc",
        "specifications": {
          "power": "121 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000038",
    "brand_id": "b0000000-0000-0000-0000-000000000014",
    "brand_name": "Volkswagen",
    "category_slug": "car",
    "name": "Volkswagen Virtus",
    "slug": "volkswagen-virtus",
    "body_type": "Premium Sedan",
    "image_url": "https://assets.volkswagen.com/is/image/volkswagenag/Virtus_Price%20Section%201920x1080?Zm10PXBuZy1hbHBoYSZ3aWQ9ODAwJmJmYz1vZmYmMGFmYw==",
    "is_active": true,
    "min_price": 1156000,
    "max_price": 1941000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0038-00000001",
        "name": "Comfortline 1.0L TSI MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1156000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0038-00000002",
        "name": "Highline 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1488000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0038-00000003",
        "name": "Topline 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1685000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0038-00000004",
        "name": "GT Plus 1.5L TSI DSG",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1941000,
        "engine_cc_or_battery_kwh": "1498 cc Turbo",
        "specifications": {
          "power": "150 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000039",
    "brand_id": "b0000000-0000-0000-0000-000000000013",
    "brand_name": "Skoda",
    "category_slug": "car",
    "name": "Skoda Slavia",
    "slug": "skoda-slavia",
    "body_type": "Premium Sedan",
    "image_url": "https://asset.autocarindia.com/static/news/images/20261006_064415_070fff14.jpg",
    "is_active": true,
    "min_price": 1163000,
    "max_price": 1912000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0039-00000001",
        "name": "Classic 1.0L TSI MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1163000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0039-00000002",
        "name": "Signature 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1499000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0039-00000003",
        "name": "Prestige 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1699000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0039-00000004",
        "name": "Monte Carlo 1.5L TSI DSG",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1912000,
        "engine_cc_or_battery_kwh": "1498 cc Turbo",
        "specifications": {
          "power": "150 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000040",
    "brand_id": "b0000000-0000-0000-0000-000000000006",
    "brand_name": "Toyota",
    "category_slug": "car",
    "name": "Toyota Glanza",
    "slug": "toyota-glanza",
    "body_type": "Premium Hatchback",
    "image_url": "https://imgd.aeplcdn.com/1920x1080/n/cw/ec/221362/glanza-facelift-exterior-right-front-three-quarter-6.jpeg?isig=0&q=80&q=80",
    "is_active": true,
    "min_price": 686000,
    "max_price": 1000000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0040-00000001",
        "name": "E 1.2L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 686000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0040-00000002",
        "name": "S 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 823000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0040-00000003",
        "name": "G 1.2L MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 878000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0040-00000004",
        "name": "V 1.2L AMT",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 1000000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "90 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0040-00000005",
        "name": "S E-CNG 1.2L MT",
        "fuel_type": "CNG",
        "transmission": "MANUAL",
        "reference_ex_showroom": 865000,
        "engine_cc_or_battery_kwh": "1197 cc",
        "specifications": {
          "power": "77.5 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000041",
    "brand_id": "b0000000-0000-0000-0000-000000000014",
    "brand_name": "Volkswagen",
    "category_slug": "car",
    "name": "Volkswagen Taigun",
    "slug": "volkswagen-taigun",
    "body_type": "Mid-size SUV",
    "image_url": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Volkswagen/Taigun/13468/1778063618610/front-view-118.jpg",
    "is_active": true,
    "min_price": 1170000,
    "max_price": 2000000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0041-00000001",
        "name": "Comfortline 1.0L TSI MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1170000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0041-00000002",
        "name": "Highline 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1540000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0041-00000003",
        "name": "Topline 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1760000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0041-00000004",
        "name": "GT Plus Edge 1.5L DSG",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 2000000,
        "engine_cc_or_battery_kwh": "1498 cc Turbo",
        "specifications": {
          "power": "150 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000042",
    "brand_id": "b0000000-0000-0000-0000-000000000013",
    "brand_name": "Skoda",
    "category_slug": "car",
    "name": "Skoda Kushaq",
    "slug": "skoda-kushaq",
    "body_type": "Mid-size SUV",
    "image_url": "https://cdn-s3.autocarindia.com/Skoda/kushaq/Skoda-Kushaq-front-quarter.jpg?w=728&q=75&fm=auto",
    "is_active": true,
    "min_price": 1189000,
    "max_price": 2049000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0042-00000001",
        "name": "Classic 1.0L TSI MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1189000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0042-00000002",
        "name": "Signature 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1559000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0042-00000003",
        "name": "Prestige 1.0L TSI AT",
        "fuel_type": "PETROL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 1789000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "115 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0042-00000004",
        "name": "Monte Carlo 1.5L TSI DSG",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 2049000,
        "engine_cc_or_battery_kwh": "1498 cc Turbo",
        "specifications": {
          "power": "150 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000043",
    "brand_id": "b0000000-0000-0000-0000-000000000015",
    "brand_name": "MG Motor",
    "category_slug": "car",
    "name": "MG Hector",
    "slug": "mg-hector",
    "body_type": "Mid-size SUV",
    "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/MG/Hector/13125/1765801652897/exterior-image-164.jpg",
    "is_active": true,
    "min_price": 1399000,
    "max_price": 2245000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0043-00000001",
        "name": "Style 1.5L Turbo MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1399000,
        "engine_cc_or_battery_kwh": "1451 cc Turbo",
        "specifications": {
          "power": "143 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0043-00000002",
        "name": "Shine Pro 1.5L CVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1717000,
        "engine_cc_or_battery_kwh": "1451 cc Turbo",
        "specifications": {
          "power": "143 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0043-00000003",
        "name": "Sharp Pro 2.0L Diesel MT",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 2170000,
        "engine_cc_or_battery_kwh": "1956 cc",
        "specifications": {
          "power": "170 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0043-00000004",
        "name": "Savvy Pro 1.5L CVT ADAS",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 2245000,
        "engine_cc_or_battery_kwh": "1451 cc Turbo",
        "specifications": {
          "power": "143 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000044",
    "brand_id": "b0000000-0000-0000-0000-000000000015",
    "brand_name": "MG Motor",
    "category_slug": "electric-vehicle",
    "name": "MG Windsor EV",
    "slug": "mg-windsor-ev",
    "body_type": "Electric Crossover",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQdatfWSPwzrydW8b36K1Orp1RWujgpK53XocHo917nsO69bQ7G5q6lbq4b&s=10",
    "is_active": true,
    "min_price": 1350000,
    "max_price": 1550000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0044-00000001",
        "name": "Excite 38 kWh EV",
        "fuel_type": "ELECTRIC",
        "transmission": "SINGLE_SPEED_EV",
        "reference_ex_showroom": 1350000,
        "engine_cc_or_battery_kwh": "38 kWh",
        "specifications": {
          "power": "136 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0044-00000002",
        "name": "Exclusive 38 kWh EV",
        "fuel_type": "ELECTRIC",
        "transmission": "SINGLE_SPEED_EV",
        "reference_ex_showroom": 1450000,
        "engine_cc_or_battery_kwh": "38 kWh",
        "specifications": {
          "power": "136 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0044-00000003",
        "name": "Essence 38 kWh EV",
        "fuel_type": "ELECTRIC",
        "transmission": "SINGLE_SPEED_EV",
        "reference_ex_showroom": 1550000,
        "engine_cc_or_battery_kwh": "38 kWh",
        "specifications": {
          "power": "136 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000045",
    "brand_id": "b0000000-0000-0000-0000-000000000003",
    "brand_name": "Mahindra",
    "category_slug": "car",
    "name": "Mahindra Scorpio Classic",
    "slug": "mahindra-scorpio-classic",
    "body_type": "Mid-size SUV",
    "image_url": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Mahindra/Scorpio/10764/1778474504907/front-left-side-47.jpg",
    "is_active": true,
    "min_price": 1362000,
    "max_price": 1742000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0045-00000001",
        "name": "Classic S 2.2L mHawk MT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1362000,
        "engine_cc_or_battery_kwh": "2184 cc",
        "specifications": {
          "power": "132 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0045-00000002",
        "name": "Classic S11 2.2L mHawk MT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1742000,
        "engine_cc_or_battery_kwh": "2184 cc",
        "specifications": {
          "power": "132 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000046",
    "brand_id": "b0000000-0000-0000-0000-000000000017",
    "brand_name": "Nissan",
    "category_slug": "car",
    "name": "Nissan Magnite",
    "slug": "nissan-magnite",
    "body_type": "Compact SUV",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUG5jjeKcy7L-F15v5LPdp03K5OkMUw1eB7HUKXOPZCoIGMBcy27Eg4c29&s=10",
    "is_active": true,
    "min_price": 599000,
    "max_price": 1150000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0046-00000001",
        "name": "Visia 1.0L B4D Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 599000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0046-00000002",
        "name": "Acenta 1.0L Petrol MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 714000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0046-00000003",
        "name": "N-Connecta 1.0L Turbo CVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 979000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "100 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0046-00000004",
        "name": "Tekna Plus 1.0L Turbo CVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1150000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "100 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000047",
    "brand_id": "b0000000-0000-0000-0000-000000000016",
    "brand_name": "Renault",
    "category_slug": "car",
    "name": "Renault Triber",
    "slug": "renault-triber",
    "body_type": "Compact MPV",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/2021_Renault_Triber_RXZ_%28Indonesia%29_front_view.jpg?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=original",
    "is_active": true,
    "min_price": 600000,
    "max_price": 897000,
    "active_groups_count": 4,
    "variants": [
      {
        "id": "v0000000-0000-0000-0047-00000001",
        "name": "RXE 1.0L Energy MT 7-Str",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 600000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0047-00000002",
        "name": "RXL 1.0L Energy MT 7-Str",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 680000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0047-00000003",
        "name": "RXT 1.0L EASY-R AMT 7-Str",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 788000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0047-00000004",
        "name": "RXZ 1.0L EASY-R AMT 7-Str",
        "fuel_type": "PETROL",
        "transmission": "AMT",
        "reference_ex_showroom": 897000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000048",
    "brand_id": "b0000000-0000-0000-0000-000000000016",
    "brand_name": "Renault",
    "category_slug": "car",
    "name": "Renault Kiger",
    "slug": "renault-kiger",
    "body_type": "Compact SUV",
    "image_url": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Renault/Kiger/12295/1764934839670/front-left-side-47.jpg",
    "is_active": true,
    "min_price": 600000,
    "max_price": 1123000,
    "active_groups_count": 1,
    "variants": [
      {
        "id": "v0000000-0000-0000-0048-00000001",
        "name": "RXE 1.0L Energy MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 600000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0048-00000002",
        "name": "RXT(O) 1.0L Energy MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 800000,
        "engine_cc_or_battery_kwh": "999 cc",
        "specifications": {
          "power": "72 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0048-00000003",
        "name": "RXZ 1.0L Turbo CVT",
        "fuel_type": "PETROL",
        "transmission": "CVT",
        "reference_ex_showroom": 1123000,
        "engine_cc_or_battery_kwh": "999 cc Turbo",
        "specifications": {
          "power": "100 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000049",
    "brand_id": "b0000000-0000-0000-0000-000000000006",
    "brand_name": "Toyota",
    "category_slug": "car",
    "name": "Toyota Fortuner",
    "slug": "toyota-fortuner",
    "body_type": "Full-size SUV",
    "image_url": "https://auto.economictimes.indiatimes.com/files/retail_files/fortuner-1665472907-prod-var.jpg",
    "is_active": true,
    "min_price": 3343000,
    "max_price": 5144000,
    "active_groups_count": 2,
    "variants": [
      {
        "id": "v0000000-0000-0000-0049-00000001",
        "name": "2.7L Petrol 4x2 MT",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 3343000,
        "engine_cc_or_battery_kwh": "2694 cc",
        "specifications": {
          "power": "166 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0049-00000002",
        "name": "2.8L Diesel 4x2 AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 3821000,
        "engine_cc_or_battery_kwh": "2755 cc",
        "specifications": {
          "power": "204 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0049-00000003",
        "name": "2.8L Diesel 4x4 AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 4232000,
        "engine_cc_or_battery_kwh": "2755 cc",
        "specifications": {
          "power": "204 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0049-00000004",
        "name": "Legender 2.8L 4x4 AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 4764000,
        "engine_cc_or_battery_kwh": "2755 cc",
        "specifications": {
          "power": "204 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0049-00000005",
        "name": "GR-S 2.8L 4x4 AT",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 5144000,
        "engine_cc_or_battery_kwh": "2755 cc",
        "specifications": {
          "power": "204 PS"
        }
      }
    ]
  },
  {
    "id": "m0000000-0000-0000-0000-000000000050",
    "brand_id": "b0000000-0000-0000-0000-000000000004",
    "brand_name": "Hyundai",
    "category_slug": "car",
    "name": "Hyundai Alcazar",
    "slug": "hyundai-alcazar",
    "body_type": "3-Row Premium SUV",
    "image_url": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Hyundai/Alcazar/9246/1758802404168/front-left-side-47.jpg",
    "is_active": true,
    "min_price": 1499000,
    "max_price": 2155000,
    "active_groups_count": 3,
    "variants": [
      {
        "id": "v0000000-0000-0000-0050-00000001",
        "name": "Executive 1.5L Turbo Petrol MT 7-Str",
        "fuel_type": "PETROL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1499000,
        "engine_cc_or_battery_kwh": "1482 cc Turbo",
        "specifications": {
          "power": "160 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0050-00000002",
        "name": "Prestige 1.5L CRDi Diesel MT 7-Str",
        "fuel_type": "DIESEL",
        "transmission": "MANUAL",
        "reference_ex_showroom": 1599000,
        "engine_cc_or_battery_kwh": "1493 cc",
        "specifications": {
          "power": "116 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0050-00000003",
        "name": "Platinum 1.5L Turbo DCT 6-Str",
        "fuel_type": "PETROL",
        "transmission": "DCT",
        "reference_ex_showroom": 1960000,
        "engine_cc_or_battery_kwh": "1482 cc Turbo",
        "specifications": {
          "power": "160 PS"
        }
      },
      {
        "id": "v0000000-0000-0000-0050-00000004",
        "name": "Signature 1.5L CRDi Diesel AT 6-Str",
        "fuel_type": "DIESEL",
        "transmission": "AUTOMATIC",
        "reference_ex_showroom": 2155000,
        "engine_cc_or_battery_kwh": "1493 cc",
        "specifications": {
          "power": "116 PS"
        }
      }
    ]
  }
];

export async function apiFetch<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('gaadilelo_token') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  // If endpoint starts with /api/v1, normalize it so base + endpoint doesn't duplicate
  if (cleanEndpoint.startsWith('/api/v1/')) {
    cleanEndpoint = cleanEndpoint.replace(/^\/api\/v1/, '');
  } else if (cleanEndpoint === '/api/v1') {
    cleanEndpoint = '';
  }

  // Build candidate URLs:
  // 0. Explicit configured NEXT_PUBLIC_API_URL (defaults to Production Render backend)
  // 1. Same-origin relative path (e.g. /api/v1/...) via Next.js server rewrite (Zero CORS / IPv6 issues)
  // 2. Direct 127.0.0.1:8000
  // 3. Fallback localhost:8000
  const isBrowser = typeof window !== 'undefined';
  const candidateUrls: string[] = [];

  const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://gaadilelo-backend-3fgo.onrender.com/api/v1';
  let cleanBase = configuredApiUrl.replace(/\/+$/, '');
  if (!cleanBase.endsWith('/api/v1')) {
    cleanBase = `${cleanBase}/api/v1`;
  }
  candidateUrls.push(`${cleanBase}${cleanEndpoint}`);

  if (isBrowser) {
    if (cleanBase.includes('localhost') || cleanBase.includes('127.0.0.1')) {
      candidateUrls.push(`/api/v1${cleanEndpoint}`);
      candidateUrls.push(`http://127.0.0.1:8000/api/v1${cleanEndpoint}`);
      candidateUrls.push(`http://localhost:8000/api/v1${cleanEndpoint}`);
    }
  } else {
    if (cleanBase.includes('localhost') || cleanBase.includes('127.0.0.1')) {
      candidateUrls.push(`http://127.0.0.1:8000/api/v1${cleanEndpoint}`);
      candidateUrls.push(`http://localhost:8000/api/v1${cleanEndpoint}`);
    }
  }

  let lastError: any = null;

  for (const url of candidateUrls) {
    try {
      const res = await fetch(url, {
        ...options,
        headers,
      });

      if (res.status === 401) {
        if (isBrowser && !cleanEndpoint.includes('/auth/login')) {
          localStorage.removeItem('gaadilelo_token');
          localStorage.removeItem('gaadilelo_user');
        }
      }

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        // If it's a 500/502/503/504 gateway error, Next.js rewrite or proxy couldn't reach backend
        if (res.status >= 500) {
          throw new Error(`Failed to fetch: Server proxy returned ${res.status}`);
        }
        let errorMsg = `Request failed with status ${res.status}`;
        if (typeof data?.detail === 'string') {
          errorMsg = data.detail;
        } else if (Array.isArray(data?.detail) && data.detail.length > 0) {
          errorMsg = data.detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join(', ');
        } else if (data?.message) {
          errorMsg = data.message;
        }
        throw new Error(errorMsg);
      }

      // If backend returns an empty array for catalog metadata (e.g. before initial DB seed),
      // gracefully fall back so the UI displays the vehicle showcase and filters without disruption
      if (Array.isArray(data) && data.length === 0) {
        if (cleanEndpoint === '/catalog/categories') return FALLBACK_CATEGORIES as unknown as T;
        if (cleanEndpoint === '/catalog/cities') return FALLBACK_CITIES as unknown as T;
        if (cleanEndpoint.startsWith('/catalog/brands')) return FALLBACK_BRANDS as unknown as T;
        if (cleanEndpoint.startsWith('/catalog/models')) return FALLBACK_MODELS as unknown as T;
      }

      return data as T;
    } catch (err: any) {
      lastError = err;
      // If it was a 4xx client application error (e.g. 400 Bad Request, 401 Unauthorized), don't try alternate URLs
      if (err.message && !err.message.includes('Failed to fetch') && !err.message.includes('NetworkError') && !err.message.includes('ECONNREFUSED')) {
        throw err;
      }
    }
  }

  // Graceful fallback for catalog metadata if backend is offline/starting up
  if (cleanEndpoint.startsWith('/catalog/categories')) {
    return FALLBACK_CATEGORIES as unknown as T;
  }
  if (cleanEndpoint.startsWith('/catalog/cities')) {
    return FALLBACK_CITIES as unknown as T;
  }
  if (cleanEndpoint.startsWith('/catalog/brands')) {
    return FALLBACK_BRANDS as unknown as T;
  }
  if (cleanEndpoint.startsWith('/catalog/models/')) {
    const rawId = cleanEndpoint.replace('/catalog/models/', '').split('?')[0];
    const match = FALLBACK_MODELS.find(
      (m) => m.id === rawId || m.slug === rawId || m.name.toLowerCase() === rawId.toLowerCase()
    );
    if (match) return match as unknown as T;
    return {
      id: rawId,
      name: 'Selected Model',
      slug: rawId,
      variants: [
        {
          id: `var-${rawId}-std`,
          name: 'Standard All Trims Eligible (Bulk Discount)',
          fuel_type: 'PETROL',
          transmission: 'MANUAL',
          reference_ex_showroom: 1100000,
          specifications: {}
        }
      ]
    } as unknown as T;
  }
  if (cleanEndpoint.startsWith('/catalog/models')) {
    return FALLBACK_MODELS as unknown as T;
  }

  console.error(`API Error on ${endpoint}:`, lastError?.message || 'Connection refused');
  throw lastError || new Error(`Failed to fetch from ${endpoint}`);
}
