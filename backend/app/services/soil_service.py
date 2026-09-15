"""
Soil Service - "No Soil Report" case.

Provides soil data (pH, texture) from latitude/longitude using the SoilGrids API
(ISRIC - World Soil Information). This replaces the unverified SIS India endpoint.

Hard rules:
- We NEVER invent soil values.
- If the API is not configured, unreachable, times out, or returns an
  incomplete/invalid payload, we return ``success=False`` with a descriptive
  error instead of fabricating N/P/K/pH.
- SoilGrids N/P/K are NOT used as direct replacements for the model's N/P/K
  because they represent different scientific quantities (concentration vs.
  stock) and require additional assumptions (bulk density, depth, mineralization)
  that are not scientifically defensible without ground-truth calibration.
- If N/P/K cannot be obtained from a source compatible with the model's training
  semantics (kg/ha plant-available nutrients), we fail gracefully.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings, Settings

logger = logging.getLogger(__name__)

# SoilGrids property codes and their expected units (from ISRIC documentation)
# phh: pH in H2O (0-14), stored as *10
# clay, sand, silt: weight fraction in % (0-100), stored as *10
# bdod: bulk density in g/cm3 (100 kg/m3) * 100
# nitrogen: total N in g/kg (cg/kg * 10)
# phosphorus: Olsen P in mg/kg (mg/kg * 10)
# potassium: exchangeable K in cmolc/kg (cmolc/kg * 10)
SOILGRIDS_PROPERTIES = ["phh2o", "clay", "sand", "silt", "bdod"]
SOILGRIDS_DEPTHS = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]


class SoilService:
    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self) -> None:
        self.settings: Settings = get_settings()
        self._base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_property(payload: Dict[str, Any], property_name: str, depth: str = "0-5cm") -> Optional[float]:
        """
        Extract a property value from SoilGrids API response for a specific depth.
        
        Response structure: {"properties": {"layers": [{"name": "phh", "depths": [{"name": "0-5cm", "values": {"mean": 6.3}}]}]}}
        """
        try:
            layers = payload.get("properties", {}).get("layers", [])
            for layer in layers:
                if layer.get("name") == property_name:
                    depths = layer.get("depths", [])
                    for d in depths:
                        if d.get("label") == depth or d.get("name") == depth:
                            values = d.get("values", {})
                            mean_val = values.get("mean")
                            if mean_val is not None:
                                return float(mean_val)
        except (AttributeError, TypeError, KeyError):
            pass
        return None

    async def get_soil_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch soil data (pH, texture) for the coordinates from SoilGrids.
        
        Returns:
            {
                "success": True,
                "ph": 6.3,
                "texture": {"clay": 25.0, "sand": 45.0, "silt": 30.0},
                "texture_class": "loam",
                "source": "SoilGrids (ISRIC)",
                "depth_used": "0-5cm",
                "warnings": ["pH and texture from SoilGrids; N/P/K not available from this source."]
            }
            or {"success": False, "source": "SoilGrids", "error": ...}
        """
        cache_key = f"{round(latitude, 2)}_{round(longitude, 2)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        params = [
            ("lon", longitude),
            ("lat", latitude),
            ("property", "phh2o"),
            ("property", "clay"),
            ("property", "sand"),
            ("property", "silt"),
            ("depth", "0-5cm"),
            ("value", "mean"),
        ]

        try:
            timeout = httpx.Timeout(8.0)
            async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
                response = await client.get(self._base_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException:
            logger.warning("soilgrids_timeout lat=%s lon=%s", latitude, longitude)
            return {
                "success": False,
                "soil_data_available": False,
                "source": "SoilGrids",
                "error": "SoilGrids API timed out.",
            }
        except httpx.HTTPStatusError as exc:
            logger.warning("soilgrids_http_error status=%s", exc.response.status_code)
            return {
                "success": False,
                "soil_data_available": False,
                "source": "SoilGrids",
                "error": f"SoilGrids API returned HTTP {exc.response.status_code}.",
            }
        except httpx.HTTPError as exc:
            logger.warning("soilgrids_http_failure: %s", exc)
            return {
                "success": False,
                "soil_data_available": False,
                "source": "SoilGrids",
                "error": f"SoilGrids API request failed: {exc}.",
            }
        except (ValueError, TypeError):
            return {
                "success": False,
                "soil_data_available": False,
                "source": "SoilGrids",
                "error": "SoilGrids API returned an invalid (non-JSON) response.",
            }

        # Extract pH (phh2o / phh is in pH * 10 units in SoilGrids v2, so divide by 10)
        ph_raw = self._extract_property(payload, "phh2o", "0-5cm")
        if ph_raw is None:
            ph_raw = self._extract_property(payload, "phh", "0-5cm")
        if ph_raw is not None:
            ph = ph_raw / 10.0
        else:
            ph = None

        # Extract texture components (stored as % * 10 in SoilGrids v2)
        clay_raw = self._extract_property(payload, "clay", "0-5cm")
        sand_raw = self._extract_property(payload, "sand", "0-5cm")
        silt_raw = self._extract_property(payload, "silt", "0-5cm")

        clay = clay_raw / 10.0 if clay_raw is not None else None
        sand = sand_raw / 10.0 if sand_raw is not None else None
        silt = silt_raw / 10.0 if silt_raw is not None else None

        # Validate pH
        if not self._sanitize_value("ph", ph):
            return {
                "success": False,
                "soil_data_available": False,
                "source": "SoilGrids",
                "error": "SoilGrids API returned invalid pH value.",
            }

        texture_class = self._classify_texture(clay, sand, silt)

        warnings = [
            "pH and texture from SoilGrids (ISRIC); N/P/K not available from this source.",
            "SoilGrids N/P/K represent concentration (g/kg, mg/kg, cmolc/kg), not kg/ha stock. They are NOT used.",
        ]

        result = {
            "success": True,
            "soil_data_available": True,
            "ph": float(ph),
            "ph_source": "SoilGrids (ISRIC)",
            "texture": {
                "clay": float(clay) if clay is not None else None,
                "sand": float(sand) if sand is not None else None,
                "silt": float(silt) if silt is not None else None,
            },
            "texture_class": texture_class,
            "source": "SoilGrids (ISRIC)",
            "depth_used": "0-5cm",
            "warnings": warnings,
        }
        self._cache[cache_key] = result
        return result

    async def get_soil_nutrients(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch soil data for the No-Soil-Report flow.
        
        Since no scientifically compatible N/P/K source is available via coordinates,
        N/P/K are returned as null with status 'UNAVAILABLE'.
        """
        soil_data = await self.get_soil_data(latitude, longitude)
        
        if not soil_data.get("success"):
            return {
                "success": False,
                "soil_data_available": False,
                "source": soil_data.get("source", "SoilGrids"),
                "error": soil_data.get("error", "SoilGrids unavailable"),
                "warnings": ["SoilGrids data unavailable for this location."],
                "N": {"value": None, "source": None, "status": "UNAVAILABLE"},
                "P": {"value": None, "source": None, "status": "UNAVAILABLE"},
                "K": {"value": None, "source": None, "status": "UNAVAILABLE"},
                "npk_available": False,
            }
        
        return {
            "success": True,
            "soil_data_available": True,
            "ph": soil_data.get("ph"),
            "ph_source": "SoilGrids (ISRIC)",
            "texture": soil_data.get("texture"),
            "texture_class": soil_data.get("texture_class"),
            "source": soil_data.get("source", "SoilGrids (ISRIC)"),
            "depth_used": soil_data.get("depth_used", "0-5cm"),
            "warnings": soil_data.get("warnings", []),
            "N": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "P": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "K": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "npk_available": False,
        }

    @staticmethod
    def _sanitize_value(key: str, value: float) -> bool:
        if value is None:
            return False
        if value < 0:
            return False
        if key == "ph" and not (0.0 <= value <= 14.0):
            return False
        if key in ("N", "P", "K") and value > 10000:
            return False
        return True

    @staticmethod
    def _classify_texture(clay: Optional[float], sand: Optional[float], silt: Optional[float]) -> Optional[str]:
        """
        Classify soil texture using USDA texture triangle simplified logic.
        Returns texture class name or None if components unavailable.
        """
        if clay is None or sand is None or silt is None:
            return None
        
        total = clay + sand + silt
        if total == 0:
            return None
        clay_n = clay / total * 100
        sand_n = sand / total * 100
        silt_n = silt / total * 100
        
        if clay_n >= 40:
            if sand_n >= 45:
                return "sandy_clay"
            elif silt_n >= 40:
                return "silty_clay"
            else:
                return "clay"
        elif clay_n >= 27:
            if sand_n >= 45:
                return "sandy_clay_loam"
            elif silt_n >= 28:
                return "silty_clay_loam"
            else:
                return "clay_loam"
        elif clay_n >= 15:
            if sand_n >= 65:
                return "sandy_loam"
            elif silt_n >= 30:
                return "silt_loam"
            else:
                return "loam"
        elif clay_n >= 7:
            # Clay 7-15%: includes sandy loam, loam, silt loam
            if sand_n >= 65:
                return "sandy_loam"
            elif silt_n >= 50:
                return "silt_loam"
            elif sand_n >= 45:
                return "loam"
            else:
                return "silt_loam"
        else:
            # Clay < 7%: sand, loamy sand, silt
            if sand_n >= 85:
                return "sand"
            elif silt_n >= 80:
                return "silt"
            else:
                return "loamy_sand"


soil_service = SoilService()
