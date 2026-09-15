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

_CACHED_STORAGES: List[Dict[str, Any]] = []
_CACHED_LOCATIONS: Dict[str, Any] = {}


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


def resolve_search_area(
    query: str,
    locations: Dict[str, Any],
    storages: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Intelligently resolves a text search query into a geographic center point (lat, lng, name).
    Recognizes 6-digit Indian PIN codes, districts and states in India, and rural towns/mandis.
    """
    q_clean = query.strip().lower()
    if not q_clean:
        return None

    # 1. Check 6-digit PIN code
    pin_match = re.search(r'\b([1-9][0-9]{5})\b', q_clean)
    if pin_match:
        pin = pin_match.group(1)
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

    # 2. Check exact district match in india_locations.json
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

    # 3. Check substring / word district match
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

    # 4. Check state name match
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

    # 5. Check sample_storages.json for matching district, village_or_area, or city
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
            display = f"{first.get('district', q_clean.title())}, {first.get('state', '')}"
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
    - If 'query' is provided: resolves the searched area (even if far away from user),
      centers search there, calculates distances from that searched center, and filters by radius.
    - If 'query' is empty: finds facilities around the farmer's current location (latitude, longitude).
    - Always supports 10km, 25km, 50km, 100km radius filters and optional crop filtering.
    """
    storages = _load_storage_data()
    locations = _load_locations_data()
    crop_term = crop.strip().lower() if crop else None
    clean_q = query.strip() if query else ""

    # Determine user location if available
    user_lat = latitude if latitude is not None and latitude != 0.0 else None
    user_lng = longitude if longitude is not None and longitude != 0.0 else None

    # CASE A: Query is provided
    if clean_q:
        search_area = resolve_search_area(clean_q, locations, storages)

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

                # If user GPS is provided, also compute user distance
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

            # Sort ascending by distance from searched center
            results.sort(key=lambda x: x["distance_km"])
            filtered = [r for r in results if r["distance_km"] <= radius]

            return {
                "success": True,
                "query": clean_q,
                "searchedArea": searched_area_name,
                "searchRadiusKm": radius,
                "autoExpanded": False,
                "count": len(filtered[:limit]),
                "results": filtered[:limit],
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
            "searchRadiusKm": radius,
            "autoExpanded": False,
            "count": len(matched_by_text[:limit]),
            "results": matched_by_text[:limit],
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
    filtered = [r for r in results if r["distance_km"] <= radius]

    return {
        "success": True,
        "query": None,
        "searchedArea": None,
        "origin": {"latitude": origin_lat, "longitude": origin_lng},
        "searchRadiusKm": radius,
        "autoExpanded": False,
        "count": len(filtered[:limit]),
        "results": filtered[:limit],
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
        crop=crop,
        limit=limit
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
    crop_term = crop.strip().lower() if crop else None

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

    return {
        "success": True,
        "state": state,
        "district": district,
        "count": len(matched[:limit]),
        "results": matched[:limit],
    }


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
