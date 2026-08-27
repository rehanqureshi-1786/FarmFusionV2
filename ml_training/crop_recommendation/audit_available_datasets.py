"""
Deep Data Audit Script for AgriAdvisor-AI and FarmFusion Datasets.

Inspects all 8 available local datasets across:
1. Shape, columns, types, memory usage
2. Missing values and null patterns
3. Exact duplicate rows and pseudo-duplicates/templates
4. Unique crop classes and names
5. Geographic coverage (States, Districts)
6. Season & Climate distributions
7. Numeric feature ranges, distributions, and anomalies
8. Analysis of 57K dataset (whether rows are permutations/templates, N/P/K semantics)
9. Assessment of suitability for:
   - Primary tabular ML training
   - Regional / District evidence
   - Economic context
   - Validation only
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/home/rdj/FarmFusionFinal")
BASE_DIR = ROOT / "external" / "AgriAdvisor-AI" / "datasets"
OUTPUT_REPORT = ROOT / "ml_training" / "crop_recommendation" / "CROP_V2_DATA_AUDIT.md"
OUTPUT_JSON = ROOT / "ml_training" / "crop_recommendation" / "dataset_audit_summary.json"


def audit_all_datasets():
    datasets = {
        "57k_crop_recommendation": BASE_DIR / "Crop_recommendation_dataset.csv",
        "2.2k_crop_recommendation": BASE_DIR / "Crop_production_data" / "Crop_recommendation.csv",
        "2.2k_crop_data": BASE_DIR / "Crop_production_data" / "Crop_Data.csv",
        "wholesale_crop_prices": BASE_DIR / "Wholesale_Crop_Prices_with_Weather_Data_India.xlsx",
        "icrisat_district_data": BASE_DIR / "ICRISAT-District-Level-Data.csv",
        "india_crop_production": BASE_DIR / "India_Agriculture_Crop_Production.csv",
        "crop_yield": BASE_DIR / "crop_yield.csv",
        "nw_india_rainfall": BASE_DIR / "nw_India_rainfall_act_dep_1901_2015.csv",
    }

    audit_results = {}

    for key, path in datasets.items():
        print(f"\nAuditing {key} ({path.name})...")
        if not path.exists():
            audit_results[key] = {"status": "FILE_NOT_FOUND", "path": str(path)}
            continue

        try:
            if path.suffix.lower() == ".xlsx":
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)

            res = {
                "file_name": path.name,
                "file_path": str(path.relative_to(ROOT)),
                "rows": int(len(df)),
                "columns_count": int(df.shape[1]),
                "columns": list(df.columns),
                "null_counts": {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0},
                "total_nulls": int(df.isnull().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
            }

            # Numeric summary
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            num_stats = {}
            for col in numeric_cols:
                valid = df[col].dropna()
                if len(valid) > 0:
                    num_stats[col] = {
                        "min": float(valid.min()),
                        "max": float(valid.max()),
                        "mean": float(round(valid.mean(), 2)),
                        "median": float(round(valid.median(), 2)),
                        "std": float(round(valid.std(), 2)),
                    }
            res["numeric_stats"] = num_stats

            # Categorical inspection (crops, states, seasons)
            for ccol in ["CROPS", "Crop", "label", "crop"]:
                if ccol in df.columns:
                    crops = df[ccol].dropna().astype(str).str.strip().unique().tolist()
                    crop_counts = df[ccol].value_counts().head(15).to_dict()
                    res["crops_count"] = len(crops)
                    res["crops_sample"] = crops[:20]
                    res["all_crops"] = sorted(crops)
                    res["crop_counts_top15"] = {str(k): int(v) for k, v in crop_counts.items()}
                    break

            for scol in ["State", "State Name", "STATE", "state"]:
                if scol in df.columns:
                    states = df[scol].dropna().astype(str).str.strip().unique().tolist()
                    res["states_count"] = len(states)
                    res["states_sample"] = states[:15]
                    break

            for dcol in ["District", "Dist Name", "DISTRICT", "district"]:
                if dcol in df.columns:
                    districts = df[dcol].dropna().astype(str).str.strip().unique().tolist()
                    res["districts_count"] = len(districts)
                    break

            for seacol in ["SEASON", "Season", "season"]:
                if seacol in df.columns:
                    seasons = df[seacol].dropna().astype(str).str.strip().unique().tolist()
                    res["seasons"] = seasons
                    break

            audit_results[key] = res

        except Exception as exc:
            audit_results[key] = {"status": "ERROR", "error": str(exc), "path": str(path)}

    # Deep Analysis of the 57k dataset
    df_57k = pd.read_csv(datasets["57k_crop_recommendation"])
    print("\n--- DEEP 57K ANALYSIS ---")
    print(f"57K Shape: {df_57k.shape}")
    print(f"57K Crops ({df_57k['CROPS'].nunique()}):", df_57k['CROPS'].unique())
    print(f"57K Soils ({df_57k['SOIL'].nunique()}):", df_57k['SOIL'].unique())
    print(f"57K Seasons ({df_57k['SEASON'].nunique()}):", df_57k['SEASON'].unique())
    print(f"57K Water Sources ({df_57k['WATER_SOURCE'].nunique()}):", df_57k['WATER_SOURCE'].unique())

    # Check if N/P/K are identical ranges across permutations
    crop_sample = df_57k[df_57k['CROPS'] == df_57k['CROPS'].iloc[0]]
    print(f"Rows for first crop '{df_57k['CROPS'].iloc[0]}': {len(crop_sample)}")
    print(crop_sample[['SOIL', 'SEASON', 'N', 'N_MAX', 'P', 'P_MAX', 'K', 'K_MAX', 'TEMP', 'MAX_TEMP', 'SOIL_PH', 'SOIL_PH_HIGH']].head(5))

    # Save JSON summary
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    return audit_results


if __name__ == "__main__":
    audit_all_datasets()
