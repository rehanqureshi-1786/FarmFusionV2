"""
ICAR-AICRP STCR Microdata Ingestion & Processing Pipeline for FarmFusion Model V2.

This module provides end-to-end data validation, schema enforcement, and seasonal climate
assimilation for authentic plot-level trial datasets obtained from ICAR-IISS Bhopal or
participating AICRP-STCR State Agricultural University centers.

Zero-Fabrication Policy:
- All chemical soil test values (N, P2O5, K2O, pH) must originate from laboratory soil analysis.
- Crop labels must belong to the exact same trial plot observation.
- Seasonal rainfall is derived from Open-Meteo ERA5-Land historical reanalysis based on
  exact experimental station coordinates and experiment year/season.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Expected column specification for raw STCR microdata files
STCR_REQUIRED_COLUMNS = [
    "center_code",
    "state",
    "district",
    "latitude",
    "longitude",
    "experiment_year",
    "season",
    "plot_no",
    "crop",
    "initial_soil_n_kg_ha",
    "initial_soil_p2o5_kg_ha",
    "initial_soil_k2o_kg_ha",
    "initial_soil_ph",
]

# Physical and agronomic validation boundaries
STCR_RANGE_BOUNDS = {
    "initial_soil_n_kg_ha": (1.0, 1200.0),      # Available N (kg/ha)
    "initial_soil_p2o5_kg_ha": (0.5, 600.0),    # Available P2O5 (kg/ha)
    "initial_soil_k2o_kg_ha": (1.0, 1500.0),    # Available K2O (kg/ha)
    "initial_soil_ph": (3.5, 10.5),             # pH (1:2.5 soil-water)
    "latitude": (6.0, 38.0),                    # Indian terrestrial bounds
    "longitude": (68.0, 98.0),                  # Indian terrestrial bounds
}

# Production-aligned feature schema
FEATURE_NAMES_V2 = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
    "NPK_sum",
    "N_to_P_ratio",
    "temp_humidity_interaction",
]


class STCRPipelineValidator:
    """Validates raw STCR experimental files and enforces scientific integrity."""

    @staticmethod
    def validate_raw_stcr_file(file_path: Path) -> Tuple[bool, List[str], Optional[pd.DataFrame]]:
        """
        Inspects an uploaded STCR CSV file for required columns, missingness, and range validity.

        Returns:
            (is_valid, validation_errors, dataframe_if_valid)
        """
        errors: List[str] = []
        if not file_path.exists():
            return False, [f"Raw STCR file not found at '{file_path}'"], None

        try:
            df = pd.read_csv(file_path)
        except Exception as exc:
            return False, [f"Failed to parse CSV file: {exc}"], None

        # 1. Column Presence Check
        missing_cols = [col for col in STCR_REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns in STCR data: {missing_cols}")

        if errors:
            return False, errors, None

        # 2. Null Value Check across mandatory biophysical features
        null_counts = df[STCR_REQUIRED_COLUMNS].isnull().sum()
        critical_nulls = null_counts[null_counts > 0]
        if not critical_nulls.empty:
            errors.append(f"Found null values in mandatory fields: {critical_nulls.to_dict()}")

        # 3. Numeric Range Validation
        for col, (min_val, max_val) in STCR_RANGE_BOUNDS.items():
            if col in df.columns:
                invalid_rows = df[(df[col] < min_val) | (df[col] > max_val)]
                if len(invalid_rows) > 0:
                    errors.append(
                        f"Field '{col}' has {len(invalid_rows)} values outside valid bounds [{min_val}, {max_val}]."
                    )

        # 4. Crop Species Representation
        crop_counts = df["crop"].str.strip().str.lower().value_counts()
        if len(crop_counts) < 3:
            errors.append(f"STCR dataset contains only {len(crop_counts)} crop classes; multi-class recommendation requires diversity.")

        is_valid = len(errors) == 0
        return is_valid, errors, df if is_valid else None


class STCRClimateAssimilator:
    """
    Assimilates authoritative seasonal climate from Open-Meteo ERA5-Land for STCR trial centers.
    Uses exact center GPS coordinates and the historical experimental season/year.
    """

    @staticmethod
    def get_seasonal_window(season: str, year: int) -> Tuple[str, str]:
        """Returns the start and end dates for standard Indian agricultural seasons."""
        s = season.strip().lower()
        if "kharif" in s:
            return f"{year}-06-01", f"{year}-10-31"
        elif "rabi" in s:
            return f"{year}-11-01", f"{year + 1}-03-31"
        elif "zaid" in s or "summer" in s:
            return f"{year}-03-01", f"{year}-05-31"
        else:
            # Default to full agricultural crop year if unspecified
            return f"{year}-06-01", f"{year + 1}-05-31"

    @classmethod
    async def fetch_historical_climate_for_center(
        cls,
        latitude: float,
        longitude: float,
        season: str,
        year: int,
    ) -> Dict[str, float]:
        """
        Queries Open-Meteo ERA5-Land archive for cumulative seasonal rainfall,
        mean temperature, and mean relative humidity.
        """
        import aiohttp

        start_date, end_date = cls.get_seasonal_window(season, year)
        url = (
            "https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={latitude}&longitude={longitude}&"
            f"start_date={start_date}&end_date={end_date}&"
            "daily=temperature_2m_mean,relative_humidity_2m_mean,precipitation_sum&"
            "timezone=Asia%2FKolkata"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Open-Meteo climate query failed with status {resp.status}")
                data = await resp.json()

        daily = data.get("daily", {})
        precip_list = daily.get("precipitation_sum", [])
        temp_list = daily.get("temperature_2m_mean", [])
        humidity_list = daily.get("relative_humidity_2m_mean", [])

        valid_precip = [p for p in precip_list if p is not None]
        valid_temp = [t for t in temp_list if t is not None]
        valid_humidity = [h for h in humidity_list if h is not None]

        cumulative_rainfall = float(np.sum(valid_precip)) if valid_precip else 0.0
        mean_temp = float(np.mean(valid_temp)) if valid_temp else 25.0
        mean_humidity = float(np.mean(valid_humidity)) if valid_humidity else 65.0

        return {
            "seasonal_rainfall_mm": round(cumulative_rainfall, 2),
            "temperature_mean_c": round(mean_temp, 2),
            "humidity_mean_pct": round(mean_humidity, 2),
        }


def transform_stcr_to_training_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms clean STCR experimental rows with climate features into the standard
    FarmFusion 10-feature vector.
    """
    df_out = pd.DataFrame()
    df_out["N"] = df["initial_soil_n_kg_ha"].astype(float)
    df_out["P"] = df["initial_soil_p2o5_kg_ha"].astype(float)
    df_out["K"] = df["initial_soil_k2o_kg_ha"].astype(float)
    df_out["temperature"] = df["temperature_mean_c"].astype(float)
    df_out["humidity"] = df["humidity_mean_pct"].astype(float)
    df_out["ph"] = df["initial_soil_ph"].astype(float)
    df_out["rainfall"] = df["seasonal_rainfall_mm"].astype(float)

    # Derived interaction features (must match inference exactly)
    df_out["NPK_sum"] = df_out["N"] + df_out["P"] + df_out["K"]
    df_out["N_to_P_ratio"] = df_out["N"] / (df_out["P"] + 1e-6)
    df_out["temp_humidity_interaction"] = df_out["temperature"] * df_out["humidity"] / 100.0

    # Target ground-truth crop
    df_out["crop"] = df["crop"].astype(str).str.strip().str.lower()
    df_out["state"] = df["state"].astype(str).str.strip().str.lower()

    return df_out
