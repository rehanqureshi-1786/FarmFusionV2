"""
Agriculture Database Repository.
Provides fast, thread-safe access to the local SQLite ICAR/CRIDA agronomic database.
"""
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "agriculture" / "farmfusion_agriculture.db"


class AgricultureRepository:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_crop_profiles(self) -> List[Dict[str, Any]]:
        """Fetch all ICAR crop profiles with parsed JSON attributes."""
        if not self.db_path.exists():
            return []

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM icar_crop_profiles")
            rows = cursor.fetchall()
            profiles = []
            for row in rows:
                p = dict(row)
                p["suitable_seasons"] = json.loads(p.get("suitable_seasons", "[]"))
                p["suitable_soil_types"] = json.loads(p.get("suitable_soil_types", "[]"))
                profiles.append(p)
            return profiles
        finally:
            conn.close()

    def get_crop_profile(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific ICAR crop profile by exact or fuzzy name match."""
        if not self.db_path.exists():
            return None

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM icar_crop_profiles WHERE LOWER(crop_name) = LOWER(?)", (crop_name.strip(),))
            row = cursor.fetchone()
            if not row:
                # Try LIKE query (e.g. "Rice" matches "Rice (Paddy)")
                cursor.execute("SELECT * FROM icar_crop_profiles WHERE LOWER(crop_name) LIKE LOWER(?)", (f"%{crop_name.strip()}%",))
                row = cursor.fetchone()

            if row:
                p = dict(row)
                p["suitable_seasons"] = json.loads(p.get("suitable_seasons", "[]"))
                p["suitable_soil_types"] = json.loads(p.get("suitable_soil_types", "[]"))
                return p
            return None
        finally:
            conn.close()

    def get_regional_suitability(self, state: str, crop_name: str) -> Optional[Dict[str, Any]]:
        """Fetch state-specific recommendation multiplier and CRIDA contingency advice."""
        if not self.db_path.exists() or not state:
            return None

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM regional_crop_suitability WHERE LOWER(state) = LOWER(?) AND LOWER(crop_name) LIKE LOWER(?)",
                (state.strip(), f"%{crop_name.strip()}%")
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_soil_compatibility(self, soil_type: str, crop_name: str) -> Optional[Dict[str, Any]]:
        """Fetch soil texture compatibility score and drainage advice."""
        if not self.db_path.exists() or not soil_type:
            return None

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM soil_texture_matrix WHERE LOWER(soil_type) LIKE LOWER(?) AND LOWER(crop_name) LIKE LOWER(?)",
                (f"%{soil_type.strip()}%", f"%{crop_name.strip()}%")
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_crop_economic_profile(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """Fetch economic yield and market demand profile."""
        if not self.db_path.exists():
            return None

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM crop_economic_profiles WHERE LOWER(crop_name) LIKE LOWER(?)",
                (f"%{crop_name.strip()}%",)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_candidates_for_season_and_region(self, season: str, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve viable crops matching season and state preferences."""
        profiles = self.get_all_crop_profiles()
        matching = []
        for p in profiles:
            seasons = p.get("suitable_seasons", [])
            if "Year-round" in seasons or season in seasons:
                matching.append(p)
        return matching


# Singleton repository instance
agriculture_repo = AgricultureRepository()
