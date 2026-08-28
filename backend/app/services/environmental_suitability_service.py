"""
Environmental Suitability Service for the "No Soil Report" crop recommendation flow.

Evaluates real environmental and geographic factors:
- Open-Meteo current temperature & relative humidity
- Open-Meteo ERA5-Land previous complete calendar year annual rainfall
- SoilGrids coordinate-based pH and texture at 0-5cm depth
- Farmer-selected soil type (Sandy Soil, Black Soil, Red Soil, Alluvial Soil)
- Current agricultural season (Kharif, Rabi, Zaid)

Criteria are derived from published ICAR and FAO agronomic benchmarks (app/data/crop_agronomic_rules.json).
This service NEVER invokes an ML model and NEVER produces pseudo-ML percentage confidences.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

RULES_FILE = Path(__file__).resolve().parent.parent / "data" / "crop_agronomic_rules.json"


class EnvironmentalSuitabilityService:
    def __init__(self):
        self._rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        try:
            if RULES_FILE.exists():
                with open(RULES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("crops", [])
        except Exception as e:
            logger.error("failed_to_load_crop_agronomic_rules", exc_info=e)
        return []

    def evaluate(
        self,
        temperature_c: Optional[float],
        humidity_percent: Optional[float],
        annual_rainfall_mm: Optional[float],
        soil_type: Optional[str],
        ph: Optional[float],
        texture: Optional[Dict[str, float]],
        season: Optional[str],
        state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Evaluate real environmental inputs against agronomic knowledge base.
        Returns candidate crops categorized by suitability level with clear factor breakdowns.
        """
        results = []

        for crop in self._rules:
            crop_name = crop.get("crop_name", "")
            hindi_name = crop.get("hindi_name", "")
            suitable_seasons = crop.get("suitable_seasons", [])
            suitable_soil_types = crop.get("suitable_soil_types", [])

            score_points = 0.0
            max_possible_points = 0.0
            contributing_factors: List[str] = []
            management_notes: List[str] = []

            # 1. Season Evaluation (Critical Weight: 25 points)
            max_possible_points += 25.0
            if season:
                if season in suitable_seasons:
                    score_points += 25.0
                    contributing_factors.append(f"Current {season} season matches optimal crop sowing window.")
                else:
                    score_points += 0.0
                    management_notes.append(f"Not the primary growing season ({', '.join(suitable_seasons)} recommended).")
            else:
                score_points += 15.0

            # 2. Temperature Evaluation (Weight: 25 points)
            max_possible_points += 25.0
            if temperature_c is not None:
                temp_opt_min = crop.get("temp_opt_min_c", 15.0)
                temp_opt_max = crop.get("temp_opt_max_c", 35.0)
                temp_min = crop.get("temp_min_c", 10.0)
                temp_max = crop.get("temp_max_c", 40.0)

                if temp_opt_min <= temperature_c <= temp_opt_max:
                    score_points += 25.0
                    contributing_factors.append(f"Current temperature ({temperature_c:.1f}°C) is in optimal range ({temp_opt_min:.0f}-{temp_opt_max:.0f}°C).")
                elif temp_min <= temperature_c <= temp_max:
                    score_points += 15.0
                    contributing_factors.append(f"Current temperature ({temperature_c:.1f}°C) is tolerable ({temp_min:.0f}-{temp_max:.0f}°C).")
                else:
                    score_points += 0.0
                    management_notes.append(f"Temperature ({temperature_c:.1f}°C) is outside typical range ({temp_min:.0f}-{temp_max:.0f}°C).")
            else:
                score_points += 12.0

            # 3. Annual Rainfall Evaluation (Weight: 25 points)
            max_possible_points += 25.0
            if annual_rainfall_mm is not None:
                rain_opt_min = crop.get("rainfall_annual_opt_min_mm", 400.0)
                rain_opt_max = crop.get("rainfall_annual_opt_max_mm", 1200.0)
                rain_min = crop.get("rainfall_annual_min_mm", 200.0)
                rain_max = crop.get("rainfall_annual_max_mm", 2500.0)

                if rain_opt_min <= annual_rainfall_mm <= rain_opt_max:
                    score_points += 25.0
                    contributing_factors.append(f"Annual rainfall ({annual_rainfall_mm:.1f} mm) meets optimal precipitation requirements ({rain_opt_min:.0f}-{rain_opt_max:.0f} mm).")
                elif rain_min <= annual_rainfall_mm <= rain_max:
                    score_points += 15.0
                    contributing_factors.append(f"Annual rainfall ({annual_rainfall_mm:.1f} mm) is within viable crop threshold ({rain_min:.0f}-{rain_max:.0f} mm).")
                elif annual_rainfall_mm < rain_min:
                    score_points += 5.0
                    management_notes.append(f"Annual rainfall ({annual_rainfall_mm:.1f} mm) is lower than ideal ({rain_opt_min:.0f} mm); supplemental irrigation needed.")
                else:
                    # Excess rainfall
                    score_points += 10.0
                    management_notes.append(f"High annual rainfall ({annual_rainfall_mm:.1f} mm); ensure proper drainage to prevent waterlogging.")
            else:
                score_points += 12.0

            # 4. Soil Type & Texture Evaluation (Weight: 25 points)
            max_possible_points += 25.0
            if soil_type:
                # Normalize soil type name
                is_direct_match = any(st.lower() in soil_type.lower() for st in suitable_soil_types)
                if is_direct_match:
                    score_points += 25.0
                    contributing_factors.append(f"Selected {soil_type} is highly suitable for root growth and nutrient exchange.")
                elif "sandy" in soil_type.lower() and crop_name in ["Rice (Paddy)", "Sugarcane", "Banana", "Jute"]:
                    score_points += 0.0
                    management_notes.append(f"Sandy soil is unsuitable for {crop_name} due to excessive water percolation and inability to retain moisture.")
                elif "black" in soil_type.lower() and crop_name in ["Groundnut (Peanut)", "Potato"]:
                    score_points += 8.0
                    management_notes.append(f"Heavy black clay can hinder pegging/tuber expansion; requires aeration and drainage management.")
                else:
                    score_points += 10.0
                    management_notes.append(f"{soil_type} is manageable with tailored organic manure and irrigation management.")
            else:
                score_points += 12.0

            # 5. SoilGrids pH Evaluation (Bonus / Modifier: up to 10 points)
            if ph is not None:
                max_possible_points += 10.0
                ph_opt_min = crop.get("ph_opt_min", 6.0)
                ph_opt_max = crop.get("ph_opt_max", 7.5)
                ph_min = crop.get("ph_min", 5.5)
                ph_max = crop.get("ph_max", 8.5)

                if ph_opt_min <= ph <= ph_opt_max:
                    score_points += 10.0
                    contributing_factors.append(f"SoilGrids pH ({ph:.1f}) is in the optimal range ({ph_opt_min}-{ph_opt_max}).")
                elif ph_min <= ph <= ph_max:
                    score_points += 6.0
                    contributing_factors.append(f"SoilGrids pH ({ph:.1f}) is within acceptable tolerance.")
                else:
                    score_points += 0.0
                    management_notes.append(f"SoilGrids pH ({ph:.1f}) is slightly acidic/alkaline for optimal growth.")

            # Calculate normalized suitability score
            normalized_score = round(score_points / max_possible_points, 3) if max_possible_points > 0 else 0.0

            # Assign categorical suitability level
            if normalized_score >= 0.80 and (not season or season in suitable_seasons):
                level = "Highly Suitable"
            elif normalized_score >= 0.65:
                level = "Suitable"
            elif normalized_score >= 0.48:
                level = "Moderately Suitable"
            else:
                level = "Not Recommended"

            if level != "Not Recommended":
                results.append({
                    "crop_name": crop_name,
                    "hindi_name": hindi_name,
                    "suitability_level": level,
                    "suitability_score": normalized_score,
                    "season": season or "Any",
                    "water_requirement": crop.get("water_requirement", "Moderate"),
                    "soil_notes": crop.get("soil_notes", ""),
                    "contributing_factors": contributing_factors,
                    "management_notes": management_notes,
                })

        # Sort by suitability score descending
        results.sort(key=lambda x: x["suitability_score"], reverse=True)
        return results


# Module-level singleton
environmental_suitability_service = EnvironmentalSuitabilityService()
