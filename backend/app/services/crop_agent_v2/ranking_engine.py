"""
Multi-Factor Agronomic Ranking & Confidence Evaluation Engine.

Evaluates candidates against 6 dimensions:
1. Soil Suitability (NPK ranges, pH optimum, soil texture compatibility)
2. Temperature / Thermal Suitability (Optimum vs Min/Max thresholds)
3. Hydrological / Rainfall Suitability (Annual rainfall vs water requirements)
4. Seasonal Alignment (Kharif, Rabi, Zaid, Year-round fit)
5. Regional Agro-Climatic Fit (ICAR-CRIDA state/district priorities)
6. ML Probability (XGBoost model output for Mode A)

Calculates confidence tiers:
- high: >= 0.75
- medium: 0.45 - 0.74
- low: 0.30 - 0.44
- unclear: < 0.30

A recommendation is flagged as `is_reliable = True` if top confidence >= 0.45.
"""
from typing import Any, Dict, List, Optional, Tuple
from app.services.crop_agent_v2.agriculture_db import agriculture_repo


class AgronomicRankingEngine:
    # Configurable FarmFusion heuristic ranking weights (documented as heuristics)
    WEIGHTS_MODE_A: Dict[str, float] = {
        "ml_probability": 0.35,
        "season": 0.15,
        "temperature": 0.10,
        "rainfall": 0.10,
        "nutrients_and_ph": 0.20,
        "soil_texture": 0.10,
    }

    WEIGHTS_MODE_B: Dict[str, float] = {
        "season": 0.25,
        "temperature": 0.25,
        "rainfall": 0.20,
        "ph": 0.15,
        "soil_texture": 0.15,
    }

    @staticmethod
    def _evaluate_ph(ph: Optional[float], profile: Dict[str, Any]) -> Tuple[float, Optional[str]]:
        if ph is None:
            return 0.85, None

        ph_min = profile.get("ph_min", 5.0)
        ph_max = profile.get("ph_max", 8.5)
        ph_opt_min = profile.get("ph_opt_min", 6.0)
        ph_opt_max = profile.get("ph_opt_max", 7.5)

        if ph_opt_min <= ph <= ph_opt_max:
            return 1.0, f"Soil pH ({ph:.1f}) is in the optimal range ({ph_opt_min}-{ph_opt_max})."
        elif ph_min <= ph <= ph_max:
            return 0.75, f"Soil pH ({ph:.1f}) is within tolerable limits ({ph_min}-{ph_max})."
        else:
            return 0.35, f"Soil pH ({ph:.1f}) is outside favorable range ({ph_min}-{ph_max})."

    @staticmethod
    def _evaluate_temperature(temp_c: Optional[float], profile: Dict[str, Any]) -> Tuple[float, Optional[str]]:
        if temp_c is None:
            return 0.80, None

        t_min = profile.get("temp_min_c", 10.0)
        t_max = profile.get("temp_max_c", 40.0)
        t_opt_min = profile.get("temp_opt_min_c", 18.0)
        t_opt_max = profile.get("temp_opt_max_c", 32.0)

        if t_opt_min <= temp_c <= t_opt_max:
            return 1.0, f"Temperature ({temp_c:.1f}°C) is ideal ({t_opt_min}-{t_opt_max}°C)."
        elif t_min <= temp_c <= t_max:
            return 0.70, f"Temperature ({temp_c:.1f}°C) is within growth limits ({t_min}-{t_max}°C)."
        else:
            return 0.25, f"Temperature ({temp_c:.1f}°C) presents thermal stress (tolerable: {t_min}-{t_max}°C)."

    @staticmethod
    def _evaluate_rainfall(rainfall_mm: Optional[float], profile: Dict[str, Any]) -> Tuple[float, Optional[str]]:
        if rainfall_mm is None or rainfall_mm <= 0:
            return 0.80, None

        r_min = profile.get("rainfall_annual_min_mm", 300.0)
        r_max = profile.get("rainfall_annual_max_mm", 2500.0)
        r_opt_min = profile.get("rainfall_annual_opt_min_mm", 500.0)
        r_opt_max = profile.get("rainfall_annual_opt_max_mm", 1200.0)

        if r_opt_min <= rainfall_mm <= r_opt_max:
            return 1.0, f"Annual rainfall ({rainfall_mm:.0f} mm) matches optimal water requirement."
        elif r_min <= rainfall_mm <= r_max:
            return 0.75, f"Annual rainfall ({rainfall_mm:.0f} mm) is adequate for growth."
        elif rainfall_mm < r_min:
            return 0.40, f"Annual rainfall ({rainfall_mm:.0f} mm) is below rainfed requirement ({r_min} mm); supplemental irrigation needed."
        else:
            return 0.50, f"Annual rainfall ({rainfall_mm:.0f} mm) exceeds normal threshold; requires good field drainage."

    @staticmethod
    def _evaluate_nutrients(
        nitrogen: Optional[float],
        phosphorus: Optional[float],
        potassium: Optional[float],
        profile: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        if nitrogen is None or phosphorus is None or potassium is None:
            return 0.80, []

        factors = []
        score = 1.0

        n_min = profile.get("n_min_kg_ha", 20.0)
        n_max = profile.get("n_max_kg_ha", 120.0)
        p_min = profile.get("p_min_kg_ha", 15.0)
        p_max = profile.get("p_max_kg_ha", 60.0)
        k_min = profile.get("k_min_kg_ha", 15.0)
        k_max = profile.get("k_max_kg_ha", 60.0)

        # Nitrogen check
        if nitrogen < n_min * 0.6:
            score -= 0.15
            factors.append(f"Low soil N ({nitrogen:.0f} kg/ha). Recommended top-dressing with urea/compost.")
        elif nitrogen >= n_min:
            factors.append(f"Adequate soil N ({nitrogen:.0f} kg/ha).")

        # Phosphorus check
        if phosphorus < p_min * 0.6:
            score -= 0.10
            factors.append(f"Low soil P ({phosphorus:.0f} kg/ha). DAP/SSP application advised.")
        elif phosphorus >= p_min:
            factors.append(f"Favorable soil P ({phosphorus:.0f} kg/ha).")

        # Potassium check
        if potassium < k_min * 0.6:
            score -= 0.10
            factors.append(f"Low soil K ({potassium:.0f} kg/ha). MOP application recommended.")
        elif potassium >= k_min:
            factors.append(f"Favorable soil K ({potassium:.0f} kg/ha).")

        return max(0.40, score), factors

    @classmethod
    def rank_candidates(
        cls,
        candidates: List[Dict[str, Any]],
        state: Optional[str] = None,
        season: Optional[str] = None,
        soil_type: Optional[str] = None,
        ph: Optional[float] = None,
        temperature_c: Optional[float] = None,
        rainfall_mm: Optional[float] = None,
        nitrogen: Optional[float] = None,
        phosphorus: Optional[float] = None,
        potassium: Optional[float] = None,
        is_mode_a: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Ranks candidate crops by running multi-factor agronomic evaluation.
        """
        ranked = []

        for cand in candidates:
            crop_name = cand.get("crop_name", "")
            profile = agriculture_repo.get_crop_profile(crop_name)
            if not profile:
                continue

            contributing_factors: List[str] = []
            management_notes: List[str] = []

            # 1. Season score
            season_score = 0.5
            suitable_seasons = profile.get("suitable_seasons", [])
            if season:
                if "Year-round" in suitable_seasons or season in suitable_seasons:
                    season_score = 1.0
                    contributing_factors.append(f"Current {season} season is the standard sowing window.")
                else:
                    season_score = 0.25
                    management_notes.append(f"Off-season: primary season is {', '.join(suitable_seasons)}.")
            else:
                season_score = 0.85

            # 2. Temperature score
            temp_score, temp_factor = cls._evaluate_temperature(temperature_c, profile)
            if temp_factor:
                if temp_score >= 0.7:
                    contributing_factors.append(temp_factor)
                else:
                    management_notes.append(temp_factor)

            # 3. Rainfall score
            rain_score, rain_factor = cls._evaluate_rainfall(rainfall_mm, profile)
            if rain_factor:
                if rain_score >= 0.7:
                    contributing_factors.append(rain_factor)
                else:
                    management_notes.append(rain_factor)

            # 4. Soil pH score
            ph_score, ph_factor = cls._evaluate_ph(ph, profile)
            if ph_factor:
                if ph_score >= 0.7:
                    contributing_factors.append(ph_factor)
                else:
                    management_notes.append(ph_factor)

            # 5. Soil Texture Matrix score
            texture_score = 0.80
            if soil_type:
                soil_mat = agriculture_repo.get_soil_compatibility(soil_type, crop_name)
                if soil_mat:
                    texture_score = float(soil_mat.get("compatibility_score", 0.80))
                    tip = soil_mat.get("special_management_tips")
                    if tip:
                        management_notes.append(tip)
                    if texture_score >= 0.8:
                        contributing_factors.append(f"Well-suited for {soil_type}.")
                    elif texture_score < 0.5:
                        management_notes.append(f"Sub-optimal compatibility with {soil_type}.")

            # 6. Nutrients score (Mode A)
            nutrient_score, nut_factors = cls._evaluate_nutrients(nitrogen, phosphorus, potassium, profile)
            contributing_factors.extend([f for f in nut_factors if "Adequate" in f or "Favorable" in f])
            management_notes.extend([f for f in nut_factors if "Low" in f])

            # 7. Regional Multiplier
            regional_mult = 1.0
            if state:
                reg_info = agriculture_repo.get_regional_suitability(state, crop_name)
                if reg_info:
                    regional_mult = float(reg_info.get("suitability_multiplier", 1.0))
                    zone = reg_info.get("agro_climatic_zone")
                    if zone:
                        contributing_factors.append(f"ICAR zone suitability: {zone}.")
                    crida_notes = reg_info.get("crida_contingency_notes")
                    if crida_notes:
                        management_notes.append(f"CRIDA note: {crida_notes}")

            # 8. ML Probability
            ml_prob = float(cand.get("probability", cand.get("model_probability", 0.75)))

            # Composite Score Calculation with Configurable Heuristic Weights
            if is_mode_a:
                w = cls.WEIGHTS_MODE_A
                raw_score = (
                    w["ml_probability"] * ml_prob +
                    w["season"] * season_score +
                    w["temperature"] * temp_score +
                    w["rainfall"] * rain_score +
                    w["nutrients_and_ph"] * ((nutrient_score + ph_score) / 2.0) +
                    w["soil_texture"] * texture_score
                ) * regional_mult
            else:
                w = cls.WEIGHTS_MODE_B
                raw_score = (
                    w["season"] * season_score +
                    w["temperature"] * temp_score +
                    w["rainfall"] * rain_score +
                    w["ph"] * ph_score +
                    w["soil_texture"] * texture_score
                ) * regional_mult

            final_confidence = min(0.98, max(0.10, round(raw_score, 4)))

            # Determine Confidence Tier
            if final_confidence >= 0.75:
                conf_tier = "high"
                suitability_level = "Highly Suitable"
            elif final_confidence >= 0.45:
                conf_tier = "medium"
                suitability_level = "Suitable"
            elif final_confidence >= 0.30:
                conf_tier = "low"
                suitability_level = "Moderately Suitable"
            else:
                conf_tier = "unclear"
                suitability_level = "Not Recommended"

            # Fetch economic info
            econ = agriculture_repo.get_crop_economic_profile(crop_name)
            market_demand = econ.get("market_demand_tier", "Medium") if econ else "Medium"
            profit_usd = econ.get("benchmark_gross_return_per_acre_usd", 350.0) if econ else 350.0
            profit_inr = econ.get("benchmark_gross_return_per_acre_inr", 28000.0) if econ else 28000.0
            econ_status = econ.get("economic_data_status", "benchmark_estimate_not_live_price") if econ else "benchmark_estimate_not_live_price"

            ranked.append({
                "crop_name": crop_name,
                "hindi_name": profile.get("hindi_name", ""),
                "confidence_score": final_confidence,
                "confidence_tier": conf_tier,
                "suitability_level": suitability_level,
                "category": profile.get("category", "cereal"),
                "water_requirement": profile.get("water_requirement_desc", "Moderate"),
                "sowing_window": f"{', '.join(suitable_seasons)} season",
                "growing_duration_months": round(profile.get("growing_duration_days_max", 120) / 30.0, 1),
                "expected_yield_tons": round((profile.get("expected_yield_min_tons", 2.0) + profile.get("expected_yield_max_tons", 4.0)) / 2.0, 2),
                "market_demand": market_demand.lower(),
                "estimated_profit_usd": profit_usd,
                "estimated_profit_inr": profit_inr,
                "benchmark_gross_return_usd": profit_usd,
                "benchmark_gross_return_inr": profit_inr,
                "economic_data_status": econ_status,
                "contributing_factors": contributing_factors,
                "management_notes": management_notes,
                "soil_notes": profile.get("soil_notes", ""),
                "regional_multiplier": regional_mult,
                "score_source": "farmfusion_heuristic",
                "agronomic_source": "ICAR Handbook of Agriculture / FAO Ecocrop",
                "model_probability": ml_prob if is_mode_a else None,
            })

        ranked.sort(key=lambda x: x["confidence_score"], reverse=True)
        for idx, item in enumerate(ranked, start=1):
            item["rank"] = idx

        return ranked


ranking_engine = AgronomicRankingEngine()
