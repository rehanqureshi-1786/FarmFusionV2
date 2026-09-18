"""
FarmFusion Cold Storage API - Fast & Intelligent Agricultural Preservation Finder
Serves real Indian cold storage facilities, Haversine GPS proximity search,
area/city/district/pincode geocoded search, radius filtering (10, 25, 50, 100 km),
state/district search, and suitable crop matching.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/cold-storage", tags=["cold-storage"])

# Resolve data directory reliably
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DATA_DIR_CANDIDATES = [
    _REPO_ROOT / "cold_storage" / "backend" / "data",
    Path(__file__).resolve().parents[3] / "cold_storage" / "backend" / "data",
    Path.cwd() / "cold_storage" / "backend" / "data",
]
DATA_DIR = next((p for p in _DATA_DIR_CANDIDATES if p.exists()), _REPO_ROOT / "cold_storage" / "backend" / "data")
SAMPLE_STORAGES_FILE = DATA_DIR / "sample_storages.json"
LOCATIONS_FILE = DATA_DIR / "india_locations.json"
VILLAGES_FILE = DATA_DIR / "rural_villages.json"

_CACHED_STORAGES: List[Dict[str, Any]] = []
_CACHED_LOCATIONS: Dict[str, Any] = {}
_CACHED_VILLAGES: Dict[str, Any] = {}

# Indian Postal 6-digit PIN Code & 2-digit Circle Mapping for high precision geocoding
PIN_CODE_MAP: Dict[str, Dict[str, Any]] = {
    # Rajasthan
    '302001': {'lat': 26.9196, 'lng': 75.8010, 'area': 'Jaipur GPO'},
    '302029': {'lat': 26.8041, 'lng': 75.7482, 'area': 'Muhana Mandi, Jaipur'},
    '303702': {'lat': 27.1724, 'lng': 75.7214, 'area': 'Chomu, Jaipur'},
    '303301': {'lat': 26.8333, 'lng': 76.0500, 'area': 'Bassi, Jaipur'},
    '303007': {'lat': 26.8167, 'lng': 75.5500, 'area': 'Bagru, Jaipur'},
    '303103': {'lat': 27.3833, 'lng': 75.9667, 'area': 'Shahpura, Jaipur'},
    '303901': {'lat': 26.6000, 'lng': 75.9500, 'area': 'Chaksu, Jaipur'},
    '303328': {'lat': 26.9667, 'lng': 75.3833, 'area': 'Jobner, Jaipur'},
    '303712': {'lat': 27.2333, 'lng': 75.6500, 'area': 'Govindgarh, Jaipur'},
    '303338': {'lat': 27.1500, 'lng': 75.3667, 'area': 'Renwal, Jaipur'},
    '303008': {'lat': 26.6833, 'lng': 75.2333, 'area': 'Dudu, Jaipur'},
    '303108': {'lat': 27.7000, 'lng': 76.2000, 'area': 'Kotputli, Jaipur'},
    '342001': {'lat': 26.2918, 'lng': 73.0168, 'area': 'Jodhpur City'},
    '342005': {'lat': 26.2210, 'lng': 73.0110, 'area': 'Bhagat Ki Kothi, Jodhpur'},
    '342301': {'lat': 27.1333, 'lng': 72.3667, 'area': 'Phalodi, Jodhpur'},
    '342303': {'lat': 26.7333, 'lng': 72.9000, 'area': 'Osian, Jodhpur'},
    '342601': {'lat': 26.3833, 'lng': 73.5333, 'area': 'Pipar City, Jodhpur'},
    '342602': {'lat': 26.1833, 'lng': 73.7000, 'area': 'Bilara, Jodhpur'},
    '342305': {'lat': 26.5333, 'lng': 73.0167, 'area': 'Mathania, Jodhpur'},
    '324005': {'lat': 25.1420, 'lng': 75.8390, 'area': 'Anantpura / Bhamashah Mandi, Kota'},
    '326519': {'lat': 24.6500, 'lng': 75.9500, 'area': 'Ramganj Mandi, Kota'},
    '325601': {'lat': 24.9167, 'lng': 76.2833, 'area': 'Sangod, Kota'},
    '301001': {'lat': 27.5530, 'lng': 76.6346, 'area': 'Alwar City'},
    '301030': {'lat': 27.5670, 'lng': 76.6890, 'area': 'MIA Industrial Area, Alwar'},
    '301411': {'lat': 27.9333, 'lng': 76.8500, 'area': 'Tijara, Alwar'},
    '335001': {'lat': 29.9140, 'lng': 73.8920, 'area': 'Sri Ganganagar'},
    '321001': {'lat': 27.2152, 'lng': 77.5030, 'area': 'Bharatpur'},
    '334001': {'lat': 28.0229, 'lng': 73.3119, 'area': 'Bikaner'},
    # Delhi & NCR
    '110033': {'lat': 28.7120, 'lng': 77.1720, 'area': 'Azadpur Mandi, Delhi'},
    '110040': {'lat': 28.8527, 'lng': 77.0931, 'area': 'Narela, Delhi'},
    '110020': {'lat': 28.5355, 'lng': 77.2711, 'area': 'Okhla, Delhi'},
    '131029': {'lat': 28.9320, 'lng': 77.0890, 'area': 'Rai Food Park, Sonipat'},
    '132001': {'lat': 29.6910, 'lng': 76.9820, 'area': 'Karnal'},
    # Uttar Pradesh
    '282007': {'lat': 27.2341, 'lng': 77.8821, 'area': 'Runkata, Agra'},
    '283111': {'lat': 27.1350, 'lng': 78.1120, 'area': 'Kundol / Fatehabad, Agra'},
    '283126': {'lat': 27.3110, 'lng': 78.0790, 'area': 'Khandauli, Agra'},
    '283125': {'lat': 27.0167, 'lng': 78.1167, 'area': 'Shamshabad, Agra'},
    '283105': {'lat': 27.1833, 'lng': 77.7667, 'area': 'Achhnera, Agra'},
    '209502': {'lat': 27.5500, 'lng': 79.3500, 'area': 'Kaimganj, Farrukhabad'},
    '209625': {'lat': 27.3826, 'lng': 79.5804, 'area': 'Fatehgarh / Farrukhabad'},
    '209721': {'lat': 27.1500, 'lng': 79.5200, 'area': 'Chhibramau, Kannauj'},
    '204101': {'lat': 27.5968, 'lng': 78.0519, 'area': 'Hathras City'},
    '204215': {'lat': 27.4400, 'lng': 77.9900, 'area': 'Sadabad, Hathras'},
    '283203': {'lat': 27.1592, 'lng': 78.3957, 'area': 'Firozabad'},
    '281001': {'lat': 27.4924, 'lng': 77.6737, 'area': 'Mathura City'},
    '221001': {'lat': 25.3176, 'lng': 82.9739, 'area': 'Varanasi City'},
    # Maharashtra
    '422001': {'lat': 19.9975, 'lng': 73.7898, 'area': 'Nashik'},
    '422207': {'lat': 20.1025, 'lng': 73.8420, 'area': 'Mohadi, Nashik'},
    '422209': {'lat': 20.1740, 'lng': 73.9870, 'area': 'Pimpalgaon Baswant, Nashik'},
    '422306': {'lat': 20.1461, 'lng': 74.2289, 'area': 'Lasalgaon, Nashik'},
    '422303': {'lat': 20.0833, 'lng': 74.1167, 'area': 'Niphad, Nashik'},
    '425001': {'lat': 21.0077, 'lng': 75.5626, 'area': 'Jalgaon'},
    '413304': {'lat': 17.6700, 'lng': 75.3300, 'area': 'Pandharpur, Solapur'},
    '410505': {'lat': 19.1200, 'lng': 73.9700, 'area': 'Narayangaon, Pune'},
    '413102': {'lat': 18.1500, 'lng': 74.5800, 'area': 'Baramati, Pune'},
    # Punjab & Haryana
    '144001': {'lat': 31.3260, 'lng': 75.5762, 'area': 'Jalandhar City'},
    '144026': {'lat': 31.2590, 'lng': 75.5210, 'area': 'Lambra, Jalandhar'},
    '141120': {'lat': 30.8410, 'lng': 75.9890, 'area': 'Sahnewal, Ludhiana'},
    '152116': {'lat': 30.1400, 'lng': 74.1900, 'area': 'Abohar, Fazilka'},
    # Gujarat
    '385535': {'lat': 24.2580, 'lng': 72.1810, 'area': 'Deesa, Banaskantha'},
    '385001': {'lat': 24.1724, 'lng': 72.4346, 'area': 'Palanpur, Banaskantha'},
    '384002': {'lat': 23.6010, 'lng': 72.3920, 'area': 'Mehsana'},
    # Madhya Pradesh
    '452015': {'lat': 22.7750, 'lng': 75.8340, 'area': 'Sanwer Road, Indore'},
    '458664': {'lat': 24.2300, 'lng': 75.0000, 'area': 'Piplia Mandi, Mandsaur'},
    '458001': {'lat': 24.0722, 'lng': 75.0688, 'area': 'Mandsaur City'},
    # Karnataka & Andhra
    '563101': {'lat': 13.1250, 'lng': 78.1420, 'area': 'Kolar APMC Mandi'},
    '522001': {'lat': 16.3190, 'lng': 80.4580, 'area': 'Guntur Mirchi Yard'},
}

PIN_CIRCLE_PREFIXES: Dict[str, Dict[str, Any]] = {
    '11': {'state': 'Delhi NCR', 'lat': 28.6139, 'lng': 77.2090},
    '12': {'state': 'Haryana', 'lat': 29.0588, 'lng': 76.0856},
    '13': {'state': 'Haryana', 'lat': 29.9695, 'lng': 76.8783},
    '14': {'state': 'Punjab', 'lat': 31.1471, 'lng': 75.3412},
    '15': {'state': 'Punjab', 'lat': 30.2110, 'lng': 74.9455},
    '20': {'state': 'Uttar Pradesh', 'lat': 27.8974, 'lng': 78.0880},
    '28': {'state': 'Uttar Pradesh (Agra/West)', 'lat': 27.1767, 'lng': 78.0081},
    '30': {'state': 'Rajasthan (Jaipur)', 'lat': 26.9124, 'lng': 75.7873},
    '31': {'state': 'Rajasthan (Udaipur)', 'lat': 24.5854, 'lng': 73.7125},
    '32': {'state': 'Rajasthan (Kota)', 'lat': 25.2138, 'lng': 75.8648},
    '33': {'state': 'Rajasthan (Bikaner)', 'lat': 28.0229, 'lng': 73.3119},
    '34': {'state': 'Rajasthan (Jodhpur)', 'lat': 26.2389, 'lng': 73.0243},
    '38': {'state': 'Gujarat', 'lat': 23.0225, 'lng': 72.5714},
    '41': {'state': 'Maharashtra (Pune)', 'lat': 18.5204, 'lng': 73.8567},
    '42': {'state': 'Maharashtra (Nashik)', 'lat': 19.9975, 'lng': 73.7898},
    '45': {'state': 'Madhya Pradesh (Indore)', 'lat': 22.7196, 'lng': 75.8577},
}


def _load_storage_data() -> List[Dict[str, Any]]:
    global _CACHED_STORAGES
    if _CACHED_STORAGES:
        return _CACHED_STORAGES

    if not SAMPLE_STORAGES_FILE.exists():
        logger.warning("cold_storage_data_not_found", path=str(SAMPLE_STORAGES_FILE))
        return []

    try:
        with open(SAMPLE_STORAGES_FILE, "r", encoding="utf-8") as f:
            _CACHED_STORAGES = json.load(f)
            logger.info("cold_storages_loaded", count=len(_CACHED_STORAGES))
    except Exception as e:
        logger.error("failed_loading_cold_storages", error=str(e))
        _CACHED_STORAGES = []

    return _CACHED_STORAGES


def _load_locations_data() -> Dict[str, Any]:
    global _CACHED_LOCATIONS
    if _CACHED_LOCATIONS:
        return _CACHED_LOCATIONS

    if not LOCATIONS_FILE.exists():
        return {}

    try:
        with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
            _CACHED_LOCATIONS = json.load(f)
    except Exception as e:
        logger.error("failed_loading_locations", error=str(e))
        _CACHED_LOCATIONS = {}

    return _CACHED_LOCATIONS


def _load_villages_data() -> Dict[str, Any]:
    global _CACHED_VILLAGES
    if _CACHED_VILLAGES:
        return _CACHED_VILLAGES

    if not VILLAGES_FILE.exists():
        return {}

    try:
        with open(VILLAGES_FILE, "r", encoding="utf-8") as f:
            _CACHED_VILLAGES = json.load(f)
    except Exception as e:
        logger.error("failed_loading_villages", error=str(e))
        _CACHED_VILLAGES = {}

    return _CACHED_VILLAGES


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance in kilometers using the Haversine formula."""
    R = 6371.0  # Earth's radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def estimate_road_transit(straight_km: float) -> Dict[str, Any]:
    """Estimates road transit distance and drive time using rural transport multipliers."""
    road_km = round(straight_km * 1.22, 1)
    avg_speed_kmh = 42.0  # Tractor/small commercial truck average speed
    time_minutes = max(5, round((road_km / avg_speed_kmh) * 60))

    if time_minutes >= 60:
        hrs = time_minutes // 60
        mins = time_minutes % 60
        time_text = f"{hrs} hr {mins} min" if mins > 0 else f"{hrs} hr"
    else:
        time_text = f"{time_minutes} mins"

    return {
        "road_distance_km": road_km,
        "drive_time_minutes": time_minutes,
        "drive_time_text": time_text,
    }


def clean_rural_term(term: str) -> str:
    """Strips common administrative keywords like tehsil, mandi, vill, etc."""
    if not term:
        return ""
    cleaned = re.sub(
        r'\b(vill|village|gram|panchayat|gp|tehsil|taluk|taluka|block|mandi|krishi mandi|subzi mandi|post|p\.o\.|po|district|dist|road|bypass|khurd|kalan|basti|dhani|gaon)\b',
        ' ',
        term,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r'[,\.\-\_\/\\#]', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip().lower()


def resolve_search_area(
    query: str,
    locations: Dict[str, Any],
    storages: List[Dict[str, Any]],
    villages: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Intelligently resolves a text search query into a geographic center point (lat, lng, name).
    Recognizes 6-digit Indian PIN codes, villages/tehsils/mandis, districts, and states.
    """
    q_raw = query.strip()
    q_clean = q_raw.lower()
    if not q_clean:
        return None

    # 1. Check 6-digit PIN code in PIN_CODE_MAP
    pin_match = re.search(r'\b([1-9][0-9]{5})\b', q_clean)
    if pin_match:
        pin = pin_match.group(1)
        if pin in PIN_CODE_MAP:
            info = PIN_CODE_MAP[pin]
            return {
                "name": f"{info['area']} (PIN {pin})",
                "latitude": float(info["lat"]),
                "longitude": float(info["lng"]),
                "type": "pincode"
            }

        # Check in sample_storages
        pin_storages = [s for s in storages if str(s.get("pincode", "")).strip() == pin and s.get("latitude")]
        if pin_storages:
            avg_lat = sum(float(s["latitude"]) for s in pin_storages) / len(pin_storages)
            avg_lng = sum(float(s["longitude"]) for s in pin_storages) / len(pin_storages)
            first = pin_storages[0]
            return {
                "name": f"PIN {pin} ({first.get('district', '')}, {first.get('state', '')})",
                "latitude": avg_lat,
                "longitude": avg_lng,
                "type": "pincode"
            }

        # Check 2-digit PIN prefix circle
        prefix2 = pin[:2]
        if prefix2 in PIN_CIRCLE_PREFIXES:
            circ = PIN_CIRCLE_PREFIXES[prefix2]
            return {
                "name": f"PIN {pin} ({circ['state']})",
                "latitude": float(circ["lat"]),
                "longitude": float(circ["lng"]),
                "type": "pincode_circle"
            }

    # 2. Check rural villages, tehsils, and mandis dictionary
    if villages:
        c_term = clean_rural_term(q_raw)
        for st_name, dist_dict in villages.items():
            for d_name, v_dict in dist_dict.items():
                for v_name, coords in v_dict.items():
                    v_low = v_name.split('(')[0].strip().lower()
                    if v_low == q_clean or v_low == c_term or (len(c_term) >= 4 and c_term in v_low):
                        return {
                            "name": f"{v_name} ({d_name}, {st_name})",
                            "latitude": float(coords["lat"]),
                            "longitude": float(coords["lng"]),
                            "type": "village"
                        }

    # 3. Check exact district match in india_locations.json
    for state_name, districts in locations.items():
        for dist_name, coords in districts.items():
            clean_d = dist_name.split('(')[0].strip().lower()
            if clean_d == q_clean or q_clean == dist_name.lower():
                return {
                    "name": f"{dist_name}, {state_name}",
                    "latitude": float(coords["lat"]),
                    "longitude": float(coords["lng"]),
                    "type": "district"
                }

    # 4. Check substring / word district match
    for state_name, districts in locations.items():
        for dist_name, coords in districts.items():
            clean_d = dist_name.split('(')[0].strip().lower()
            if q_clean in clean_d or clean_d in q_clean or q_clean in dist_name.lower():
                return {
                    "name": f"{dist_name}, {state_name}",
                    "latitude": float(coords["lat"]),
                    "longitude": float(coords["lng"]),
                    "type": "district"
                }

    # 5. Check state name match
    for state_name, districts in locations.items():
        if q_clean == state_name.lower() or q_clean in state_name.lower():
            if districts:
                coords_list = [c for c in districts.values() if "lat" in c and "lng" in c]
                if coords_list:
                    c_lat = sum(float(c["lat"]) for c in coords_list) / len(coords_list)
                    c_lng = sum(float(c["lng"]) for c in coords_list) / len(coords_list)
                    return {
                        "name": f"{state_name}, India",
                        "latitude": c_lat,
                        "longitude": c_lng,
                        "type": "state"
                    }

    # 6. Check sample_storages.json for matching district, village_or_area, or city
    matched = [
        s for s in storages
        if q_clean == str(s.get("district", "")).strip().lower()
        or q_clean == str(s.get("village_or_area", "")).strip().lower()
        or q_clean in str(s.get("district", "")).strip().lower()
        or q_clean in str(s.get("village_or_area", "")).strip().lower()
    ]
    if matched:
        valid_coords = [m for m in matched if m.get("latitude") and m.get("longitude")]
        if valid_coords:
            c_lat = sum(float(m["latitude"]) for m in valid_coords) / len(valid_coords)
            c_lng = sum(float(m["longitude"]) for m in valid_coords) / len(valid_coords)
            first = valid_coords[0]
            display = f"{first.get('district', q_raw.title())}, {first.get('state', '')}"
            return {
                "name": display,
                "latitude": c_lat,
                "longitude": c_lng,
                "type": "area"
            }

    return None


@router.get("/search")
async def search_cold_storages(
    query: Optional[str] = Query(None, description="Search query (city, district, town, pincode, or facility name)"),
    latitude: Optional[float] = Query(None, description="Farmer latitude coordinate"),
    longitude: Optional[float] = Query(None, description="Farmer longitude coordinate"),
    radius: float = Query(50.0, description="Search radius in kilometers (10, 25, 50, 100)", ge=5.0, le=500.0),
    crop: Optional[str] = Query(None, description="Crop filter (e.g. Potato, Onion, Garlic, Fruits)"),
    limit: int = Query(50, description="Max results", ge=1, le=100),
):
    """
    Intelligent Search for Cold Storage Facilities:
    - If 'query' is provided: resolves the searched area, centers search there,
      calculates distances, and filters by radius.
    - If 'query' is empty: finds facilities around the farmer's current location.
    - Supports radius filters and crop filtering.
    """
    storages = _load_storage_data()
    locations = _load_locations_data()
    villages = _load_villages_data()

    # Sanitize query parameters safely
    crop_term = crop.strip().lower() if isinstance(crop, str) and crop.strip() else None
    clean_q = query.strip() if isinstance(query, str) else ""
    radius_km = float(radius) if isinstance(radius, (int, float)) else 50.0
    limit_count = int(limit) if isinstance(limit, int) else 50

    user_lat = latitude if isinstance(latitude, (int, float)) and latitude != 0.0 else None
    user_lng = longitude if isinstance(longitude, (int, float)) and longitude != 0.0 else None

    # CASE A: Query is provided
    if clean_q:
        search_area = resolve_search_area(clean_q, locations, storages, villages)

        if search_area:
            center_lat = search_area["latitude"]
            center_lng = search_area["longitude"]
            searched_area_name = search_area["name"]

            results = []
            for item in storages:
                try:
                    s_lat = float(item.get("latitude", 0.0))
                    s_lng = float(item.get("longitude", 0.0))
                except (ValueError, TypeError):
                    continue

                if s_lat == 0.0 and s_lng == 0.0:
                    continue

                dist_from_center = haversine_distance(center_lat, center_lng, s_lat, s_lng)

                # Filter by crop
                if crop_term:
                    suitable = str(item.get("suitable_crops", "")).lower()
                    name = str(item.get("name", "")).lower()
                    desc = str(item.get("description", "")).lower()
                    if crop_term not in suitable and crop_term not in name and crop_term not in desc:
                        continue

                transit = estimate_road_transit(dist_from_center)
                rec = dict(item)
                rec["distance_km"] = dist_from_center
                rec["road_distance_km"] = transit["road_distance_km"]
                rec["drive_time_minutes"] = transit["drive_time_minutes"]
                rec["drive_time_text"] = transit["drive_time_text"]
                rec["searched_area"] = searched_area_name

                if user_lat is not None and user_lng is not None:
                    rec["user_distance_km"] = haversine_distance(user_lat, user_lng, s_lat, s_lng)
                    rec["google_maps_url"] = (
                        f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lng}&destination={s_lat},{s_lng}"
                    )
                else:
                    rec["google_maps_url"] = (
                        f"https://www.google.com/maps/dir/?api=1&origin={center_lat},{center_lng}&destination={s_lat},{s_lng}"
                    )

                results.append(rec)

            results.sort(key=lambda x: x["distance_km"])
            filtered = [r for r in results if r["distance_km"] <= radius_km]

            return {
                "success": True,
                "query": clean_q,
                "searchedArea": searched_area_name,
                "searchRadiusKm": radius_km,
                "autoExpanded": False,
                "count": len(filtered[:limit_count]),
                "results": filtered[:limit_count],
            }

        # Query did not match a geographic area -> keyword search in name, address, crops
        q_low = clean_q.lower()
        matched_by_text = []
        for item in storages:
            name_str = str(item.get("name", "")).lower()
            addr_str = str(item.get("address", "")).lower()
            crop_str = str(item.get("suitable_crops", "")).lower()
            desc_str = str(item.get("description", "")).lower()

            if q_low in name_str or q_low in addr_str or q_low in crop_str or q_low in desc_str:
                if crop_term and crop_term not in crop_str and crop_term not in name_str:
                    continue

                try:
                    s_lat = float(item.get("latitude", 0.0))
                    s_lng = float(item.get("longitude", 0.0))
                except (ValueError, TypeError):
                    s_lat, s_lng = 0.0, 0.0

                rec = dict(item)
                rec["searched_area"] = clean_q.title()

                ref_lat = user_lat or 26.9124
                ref_lng = user_lng or 75.7873
                dist = haversine_distance(ref_lat, ref_lng, s_lat, s_lng) if s_lat and s_lng else 0.0
                transit = estimate_road_transit(dist)
                rec["distance_km"] = dist
                rec["road_distance_km"] = transit["road_distance_km"]
                rec["drive_time_text"] = transit["drive_time_text"]
                rec["google_maps_url"] = (
                    f"https://www.google.com/maps/dir/?api=1&origin={ref_lat},{ref_lng}&destination={s_lat},{s_lng}"
                )
                matched_by_text.append(rec)

        matched_by_text.sort(key=lambda x: x["distance_km"])
        return {
            "success": True,
            "query": clean_q,
            "searchedArea": clean_q.title(),
            "searchRadiusKm": radius_km,
            "autoExpanded": False,
            "count": len(matched_by_text[:limit_count]),
            "results": matched_by_text[:limit_count],
        }

    # CASE B: No query provided -> search around user's GPS coordinates
    origin_lat = user_lat or 26.9124
    origin_lng = user_lng or 75.7873

    results = []
    for item in storages:
        try:
            s_lat = float(item.get("latitude", 0.0))
            s_lng = float(item.get("longitude", 0.0))
        except (ValueError, TypeError):
            continue

        if s_lat == 0.0 and s_lng == 0.0:
            continue

        dist_km = haversine_distance(origin_lat, origin_lng, s_lat, s_lng)

        # Filter by crop
        if crop_term:
            suitable = str(item.get("suitable_crops", "")).lower()
            name = str(item.get("name", "")).lower()
            desc = str(item.get("description", "")).lower()
            if crop_term not in suitable and crop_term not in name and crop_term not in desc:
                continue

        transit = estimate_road_transit(dist_km)
        rec = dict(item)
        rec["distance_km"] = dist_km
        rec["road_distance_km"] = transit["road_distance_km"]
        rec["drive_time_minutes"] = transit["drive_time_minutes"]
        rec["drive_time_text"] = transit["drive_time_text"]
        rec["google_maps_url"] = (
            f"https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lng}&destination={s_lat},{s_lng}"
        )
        results.append(rec)

    results.sort(key=lambda x: x["distance_km"])
    filtered = [r for r in results if r["distance_km"] <= radius_km]

    return {
        "success": True,
        "query": None,
        "searchedArea": None,
        "origin": {"latitude": origin_lat, "longitude": origin_lng},
        "searchRadiusKm": radius_km,
        "autoExpanded": False,
        "count": len(filtered[:limit_count]),
        "results": filtered[:limit_count],
    }


@router.get("/nearby")
async def get_nearby_cold_storages(
    latitude: float = Query(..., description="Farmer latitude"),
    longitude: float = Query(..., description="Farmer longitude"),
    radius: float = Query(50.0, description="Search radius in kilometers", ge=5.0, le=500.0),
    crop: Optional[str] = Query(None, description="Optional crop filter (e.g. Potato, Onion, Apple)"),
    limit: int = Query(25, description="Maximum number of results to return", ge=1, le=100),
):
    """
    Find cold storage facilities near the farmer's GPS coordinates.
    """
    return await search_cold_storages(
        query=None,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        crop=crop if isinstance(crop, str) else None,
        limit=limit if isinstance(limit, int) else 25
    )


@router.get("/district")
async def get_district_cold_storages(
    state: str = Query(..., description="Indian state name (e.g. Rajasthan, Uttar Pradesh)"),
    district: str = Query(..., description="District name (e.g. Jaipur, Agra, Indore)"),
    crop: Optional[str] = Query(None, description="Optional crop filter"),
    limit: int = Query(50, description="Max results", ge=1, le=100),
):
    """
    Search cold storages by State and District.
    """
    storages = _load_storage_data()
    clean_state = state.strip().lower()
    clean_dist = district.strip().lower()
    crop_term = crop.strip().lower() if isinstance(crop, str) and crop.strip() else None

    matched = []
    for item in storages:
        s_state = str(item.get("state", "")).strip().lower()
        s_dist = str(item.get("district", "")).strip().lower()

        state_ok = clean_state in s_state or s_state in clean_state
        dist_ok = clean_dist in s_dist or s_dist in clean_dist

        if state_ok and dist_ok:
            if crop_term:
                suitable = str(item.get("suitable_crops", "")).lower()
                if crop_term not in suitable:
                    continue
            matched.append(item)

    limit_val = int(limit) if isinstance(limit, int) else 50
    return {
        "success": True,
        "state": state,
        "district": district,
        "count": len(matched[:limit_val]),
        "results": matched[:limit_val],
    }


@router.get("/villages")
async def get_villages_suggest(
    q: Optional[str] = Query(None, description="Village or mandi search term"),
    query: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None)
):
    """Suggests villages, mandis, and tehsils for auto-complete."""
    term = clean_rural_term(q or query or "")
    if len(term) < 2:
        return {"success": True, "count": 0, "suggestions": []}

    villages = _load_villages_data()
    suggestions = []

    for st_name, districts in villages.items():
        if state and state.lower() not in st_name.lower():
            continue
        for d_name, v_dict in districts.items():
            if district and district.lower() not in d_name.lower():
                continue
            for v_name, coords in v_dict.items():
                if term in v_name.lower() or term in clean_rural_term(v_name):
                    suggestions.append({
                        "name": v_name,
                        "village": v_name,
                        "district": d_name,
                        "state": st_name,
                        "latitude": coords["lat"],
                        "longitude": coords["lng"],
                        "type": coords.get("type", "Village")
                    })
                    if len(suggestions) >= 20:
                        break
            if len(suggestions) >= 20:
                break
        if len(suggestions) >= 20:
            break

    return {"success": True, "count": len(suggestions), "suggestions": suggestions}


@router.get("/pincode/{pin}")
async def get_pincode_info(pin: str):
    """Direct PIN code lookup for geographic coordinates."""
    clean_pin = pin.strip()
    if clean_pin in PIN_CODE_MAP:
        info = PIN_CODE_MAP[clean_pin]
        return {
            "success": True,
            "pincode": clean_pin,
            "area": info["area"],
            "latitude": info["lat"],
            "longitude": info["lng"]
        }

    prefix2 = clean_pin[:2]
    if prefix2 in PIN_CIRCLE_PREFIXES:
        circ = PIN_CIRCLE_PREFIXES[prefix2]
        return {
            "success": True,
            "pincode": clean_pin,
            "area": circ["state"],
            "latitude": circ["lat"],
            "longitude": circ["lng"]
        }

    raise HTTPException(status_code=404, detail=f"PIN {clean_pin} not found in database.")


@router.get("/locations")
async def get_locations():
    """Returns available Indian states and districts for cold storage filtering."""
    locations = _load_locations_data()
    return {
        "success": True,
        "locations": locations,
    }


@router.get("/{storage_id}")
async def get_cold_storage_detail(storage_id: str):
    """Get single cold storage facility details by ID."""
    storages = _load_storage_data()
    for item in storages:
        if str(item.get("id")) == storage_id:
            return {
                "success": True,
                "cold_storage": item,
            }

    raise HTTPException(status_code=404, detail=f"Cold storage facility '{storage_id}' not found.")

