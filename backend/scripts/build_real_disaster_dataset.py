"""
Build Real Indian Disaster & Agricultural Weather Dataset
=========================================================
Downloads genuine historical weather observations from Open-Meteo Historical Archive
for verified Indian disaster events (Mumbai/Kerala/Chennai floods, Tauktae/Biparjoy/Amphan
cyclones, Marathwada/Bundelkhand droughts) and multi-year real agricultural weather
across 10 Indian states (Low Risk).
"""

import os
import time
import requests
import numpy as np
import pandas as pd

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml_training")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "real_indian_disaster_dataset.csv")

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_archive_range(lat: float, lon: float, start_date: str, end_date: str):
    """Fetch real historical daily weather from Open-Meteo Archive API."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "relative_humidity_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_max",
            "surface_pressure_mean",
        ],
        "timezone": "auto",
    }
    for attempt in range(3):
        try:
            resp = requests.get(ARCHIVE_URL, params=params, timeout=20)
            if resp.status_code == 200:
                data = resp.json().get("daily", {})
                times = data.get("time", [])
                temps = data.get("temperature_2m_max", [])
                humids = data.get("relative_humidity_2m_mean", [])
                precips = data.get("precipitation_sum", [])
                winds = data.get("wind_speed_10m_max", [])
                pressures = data.get("surface_pressure_mean", [])
                
                rows = []
                for i in range(len(times)):
                    if all(v[i] is not None for v in [temps, humids, precips, winds, pressures]):
                        rows.append({
                            "date": times[i],
                            "temperature": float(temps[i]),
                            "humidity": float(humids[i]),
                            "rainfall": float(precips[i]),
                            "wind_speed": float(winds[i]),
                            "pressure": float(pressures[i]),
                        })
                return rows
            time.sleep(1)
        except Exception as e:
            time.sleep(1)
    return []


def main():
    print("=" * 70)
    print("FETCHING REAL INDIAN DISASTER & NORMAL WEATHER DATA")
    print("=" * 70)

    # 1. Verified Indian Flood Events (Documented Deluges & Catastrophic Monsoons)
    flood_events = [
        {"name": "Mumbai Deluge 2005", "lat": 19.07, "lon": 72.87, "start": "2005-07-24", "end": "2005-07-31"},
        {"name": "Mumbai Floods 2017", "lat": 19.07, "lon": 72.87, "start": "2017-08-27", "end": "2017-09-02"},
        {"name": "Mumbai Floods 2019", "lat": 19.07, "lon": 72.87, "start": "2019-07-01", "end": "2019-07-06"},
        {"name": "Kerala Great Floods 2018", "lat": 9.93, "lon": 76.26, "start": "2018-08-07", "end": "2018-08-20"},
        {"name": "Idukki Kerala Floods 2018", "lat": 9.85, "lon": 76.97, "start": "2018-08-07", "end": "2018-08-20"},
        {"name": "Kerala Floods 2019", "lat": 9.93, "lon": 76.26, "start": "2019-08-06", "end": "2019-08-16"},
        {"name": "Chennai Floods 2015", "lat": 13.08, "lon": 80.27, "start": "2015-11-28", "end": "2015-12-06"},
        {"name": "Kolhapur Floods 2019", "lat": 16.70, "lon": 74.24, "start": "2019-08-02", "end": "2019-08-12"},
        {"name": "Mahad Konkan Deluge 2021", "lat": 18.08, "lon": 73.42, "start": "2021-07-20", "end": "2021-07-26"},
        {"name": "Assam Brahmaputra Floods 2022", "lat": 26.14, "lon": 91.73, "start": "2022-06-13", "end": "2022-06-25"},
        {"name": "Delhi Yamuna Floods 2023", "lat": 28.61, "lon": 77.23, "start": "2023-07-08", "end": "2023-07-14"},
        {"name": "Junagadh Flash Floods 2023", "lat": 21.52, "lon": 70.45, "start": "2023-07-20", "end": "2023-07-25"},
        {"name": "Kedarnath Cloudburst 2013", "lat": 30.31, "lon": 78.03, "start": "2013-06-14", "end": "2013-06-18"},
        {"name": "Wayanad Deluge 2024", "lat": 11.68, "lon": 76.13, "start": "2024-07-27", "end": "2024-08-02"},
    ]

    # 2. Verified Indian Cyclone Events (IMD Categorized Cyclonic Storms / Landfalls)
    cyclone_events = [
        {"name": "Cyclone Tauktae 2021 (Gujarat)", "lat": 20.90, "lon": 71.50, "start": "2021-05-16", "end": "2021-05-19"},
        {"name": "Cyclone Biparjoy 2023 (Kutch)", "lat": 23.23, "lon": 68.66, "start": "2023-06-13", "end": "2023-06-17"},
        {"name": "Cyclone Amphan 2020 (Bengal)", "lat": 22.57, "lon": 88.36, "start": "2020-05-19", "end": "2020-05-22"},
        {"name": "Cyclone Fani 2019 (Puri)", "lat": 19.81, "lon": 85.83, "start": "2019-05-02", "end": "2019-05-05"},
        {"name": "Cyclone Hudhud 2014 (Vizag)", "lat": 17.68, "lon": 83.21, "start": "2014-10-11", "end": "2014-10-14"},
        {"name": "Cyclone Nivar 2020 (Puducherry)", "lat": 11.94, "lon": 79.80, "start": "2020-11-24", "end": "2020-11-27"},
        {"name": "Cyclone Michaung 2023 (Chennai/AP)", "lat": 13.08, "lon": 80.27, "start": "2023-12-03", "end": "2023-12-06"},
        {"name": "Cyclone Yaas 2021 (Balasore)", "lat": 21.50, "lon": 87.00, "start": "2021-05-25", "end": "2021-05-28"},
        {"name": "Cyclone Ockhi 2017 (Kerala)", "lat": 8.52, "lon": 76.93, "start": "2017-11-29", "end": "2017-12-03"},
        {"name": "Cyclone Vardah 2016 (Chennai)", "lat": 13.08, "lon": 80.27, "start": "2016-12-11", "end": "2016-12-14"},
        {"name": "Cyclone Phailin 2013 (Odisha)", "lat": 19.30, "lon": 84.90, "start": "2013-10-11", "end": "2013-10-14"},
    ]

    # 3. Verified Indian Drought & Heatwave Events
    drought_events = [
        {"name": "Marathwada Latur 2016", "lat": 18.40, "lon": 76.56, "start": "2016-04-15", "end": "2016-06-15"},
        {"name": "Marathwada Beed 2019", "lat": 18.98, "lon": 75.76, "start": "2019-05-01", "end": "2019-06-15"},
        {"name": "Bundelkhand Jhansi 2019", "lat": 25.44, "lon": 78.56, "start": "2019-05-01", "end": "2019-06-15"},
        {"name": "Bundelkhand Banda 2018", "lat": 25.47, "lon": 80.33, "start": "2018-05-01", "end": "2018-06-15"},
        {"name": "Thar Desert Barmer 2018", "lat": 25.75, "lon": 71.39, "start": "2018-05-01", "end": "2018-06-15"},
        {"name": "Thar Desert Jaisalmer 2019", "lat": 26.91, "lon": 70.90, "start": "2019-05-15", "end": "2019-06-30"},
        {"name": "Vidarbha Nagpur 2016", "lat": 21.14, "lon": 79.08, "start": "2016-05-01", "end": "2016-06-10"},
        {"name": "Rayalaseema Anantapur 2017", "lat": 14.68, "lon": 77.60, "start": "2017-03-15", "end": "2017-05-30"},
    ]

    # 4. Multi-Year Real Agricultural Weather across Indian Agronomic Hubs (Low Risk)
    normal_locations = [
        {"name": "Jaipur (Rajasthan)", "lat": 26.91, "lon": 75.78},
        {"name": "Ludhiana (Punjab)", "lat": 30.90, "lon": 75.85},
        {"name": "Varanasi (UP)", "lat": 25.31, "lon": 82.97},
        {"name": "Pune (Maharashtra)", "lat": 18.52, "lon": 73.85},
        {"name": "Indore (MP)", "lat": 22.71, "lon": 75.85},
        {"name": "Karnal (Haryana)", "lat": 29.68, "lon": 76.99},
        {"name": "Patna (Bihar)", "lat": 25.59, "lon": 85.13},
        {"name": "Rajkot (Gujarat)", "lat": 22.30, "lon": 70.80},
        {"name": "Guntur (Andhra)", "lat": 16.30, "lon": 80.43},
        {"name": "Nagpur (Maharashtra)", "lat": 21.14, "lon": 79.08},
    ]

    dataset_rows = []

    print("\n[1/4] Fetching Real Flood Records...")
    for ev in flood_events:
        print(f"  -> Fetching {ev['name']} ({ev['start']} to {ev['end']})...")
        records = fetch_archive_range(ev["lat"], ev["lon"], ev["start"], ev["end"])
        for r in records:
            # During verified flood window, high rainfall days are Flood Risk
            if r["rainfall"] >= 45.0 or (r["rainfall"] >= 35.0 and r["humidity"] >= 80):
                label = "Flood Risk"
            else:
                label = "Low Risk"
            dataset_rows.append({**r, "label": label, "event_source": ev["name"]})

    print("\n[2/4] Fetching Real Cyclone Records...")
    for ev in cyclone_events:
        print(f"  -> Fetching {ev['name']} ({ev['start']} to {ev['end']})...")
        records = fetch_archive_range(ev["lat"], ev["lon"], ev["start"], ev["end"])
        for r in records:
            # Cyclonic storm conditions: high wind + pressure drop
            if r["wind_speed"] >= 35.0 or (r["wind_speed"] >= 25.0 and r["rainfall"] >= 40.0):
                label = "Cyclone Risk"
            elif r["rainfall"] >= 50.0:
                label = "Flood Risk"
            else:
                label = "Low Risk"
            dataset_rows.append({**r, "label": label, "event_source": ev["name"]})

    print("\n[3/4] Fetching Real Drought Records...")
    for ev in drought_events:
        print(f"  -> Fetching {ev['name']} ({ev['start']} to {ev['end']})...")
        records = fetch_archive_range(ev["lat"], ev["lon"], ev["start"], ev["end"])
        for r in records:
            # Severe heatwave + moisture deficit
            if r["temperature"] >= 38.0 and r["rainfall"] <= 2.0 and r["humidity"] <= 45.0:
                label = "Drought Risk"
            else:
                label = "Low Risk"
            dataset_rows.append({**r, "label": label, "event_source": ev["name"]})

    print("\n[4/4] Fetching Multi-Year Real Agricultural Weather across India (2022-2024)...")
    for loc in normal_locations:
        print(f"  -> Fetching {loc['name']} (2023-01-01 to 2024-10-01)...")
        records = fetch_archive_range(loc["lat"], loc["lon"], "2023-01-01", "2024-10-01")
        for r in records:
            # Classify purely by physical meteorological reality:
            # If a day happened to receive massive rainfall (>75mm), it's flood; if gale wind (>45km/h), cyclone; if scorching drought (>40C, 0 rain, <25% RH), drought.
            # ALL OTHER NORMAL AGRI DAYS (95%+) ARE LOW RISK!
            if r["rainfall"] >= 75.0:
                label = "Flood Risk"
            elif r["wind_speed"] >= 50.0:
                label = "Cyclone Risk"
            elif r["temperature"] >= 42.0 and r["rainfall"] == 0.0 and r["humidity"] <= 22.0:
                label = "Drought Risk"
            else:
                label = "Low Risk"
            dataset_rows.append({**r, "label": label, "event_source": loc["name"]})

    df = pd.DataFrame(dataset_rows)
    print(f"\nTotal Real Historical Records Collected: {len(df)}")
    print("\nClass Distribution:")
    print(df["label"].value_counts())

    # Save to disk
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved Real Indian Disaster Dataset to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
