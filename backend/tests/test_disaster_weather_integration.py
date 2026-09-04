"""
Comprehensive Integration and Regression Test Suite for Phase G:
DisasterPredictorAI + Weather Page + Vobiz Calling Agent Alerting.
"""

import pytest
import time
from httpx import AsyncClient, ASGITransport
from main import app
from app.ml.disaster.inference import disaster_predictor
from app.services.disaster_alert_service import disaster_alert_service


@pytest.mark.asyncio
async def test_01_disaster_model_inference_all_classes():
    """Verify disaster model inference across all 4 disaster types."""
    # 1. Flood Risk
    flood_res = disaster_predictor.predict(
        temperature=27.0,
        humidity=92.0,
        rainfall=110.0,
        wind_speed=25.0,
        pressure=995.0,
        crop_name="Rice"
    )
    assert flood_res["disaster_type"] == "Flood Risk"
    assert flood_res["risk_level"] in ["HIGH", "CRITICAL"]
    assert flood_res["risk_score"] >= 75.0
    assert 0.0 <= flood_res["confidence"] <= 1.0
    assert 0.0 <= flood_res["probability"] <= 1.0
    assert any("precipitation" in f.lower() or "rain" in f.lower() for f in flood_res["trigger_factors"])

    # 2. Cyclone Risk
    cyclone_res = disaster_predictor.predict(
        temperature=28.0,
        humidity=88.0,
        rainfall=65.0,
        wind_speed=65.0,
        pressure=955.0,
        crop_name="Banana"
    )
    assert cyclone_res["disaster_type"] == "Cyclone Risk"
    assert cyclone_res["risk_level"] in ["HIGH", "CRITICAL"]
    assert cyclone_res["risk_score"] >= 75.0
    assert any("wind" in f.lower() or "depression" in f.lower() for f in cyclone_res["trigger_factors"])

    # 3. Drought Risk
    drought_res = disaster_predictor.predict(
        temperature=43.0,
        humidity=18.0,
        rainfall=0.0,
        wind_speed=14.0,
        pressure=1010.0,
        crop_name="Millet"
    )
    assert drought_res["disaster_type"] == "Drought Risk"
    assert drought_res["risk_score"] >= 40.0

    # 4. Low Risk
    low_res = disaster_predictor.predict(
        temperature=24.0,
        humidity=60.0,
        rainfall=15.0,
        wind_speed=10.0,
        pressure=1013.0,
        crop_name="Wheat"
    )
    assert low_res["disaster_type"] == "Low Risk"
    assert low_res["risk_level"] == "LOW"
    assert low_res["risk_score"] <= 40.0


@pytest.mark.asyncio
async def test_02_rest_api_disaster_risk_endpoint_flood_scenario():
    """Verify POST /api/v1/weather/disaster-risk with high rainfall flood scenario."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "lat": 26.91,
            "lon": 75.78,
            "location_name": "Jaipur North",
            "farmer_name": "Ram Lal",
            "farmer_phone": "+919999999991",
            "crop_name": "Paddy",
            "language": "hi",
            "temperature": 26.5,
            "humidity": 95.0,
            "rainfall": 130.0,
            "wind_speed": 30.0,
            "pressure": 990.0
        }
        resp = await client.post("/api/v1/weather/disaster-risk", json=payload)
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["location"]["name"] == "Jaipur North"
        assert len(data["predictions"]) >= 1

        pred = data["predictions"][0]
        assert pred["disaster_type"] == "Flood Risk"
        assert pred["risk_level"] in ["HIGH", "CRITICAL"]
        assert 0.0 <= pred["confidence"] <= 1.0
        assert 0.0 <= pred["probability"] <= 1.0
        assert pred["prediction_horizon"] == "24-48 hours"
        assert len(pred["trigger_factors"]) > 0
        assert len(pred["recommendations"]) > 0

        # Alert decision
        assert data["alert"]["should_alert"] is True
        assert data["alert"]["severity"] in ["HIGH", "CRITICAL"]
        assert data["alert"]["alert_status"] == "TRIGGERED"
        assert "बाढ़" in data["alert"]["alert_message"]


@pytest.mark.asyncio
async def test_03_rest_api_disaster_risk_low_scenario_display_only():
    """Verify LOW risk produces display-only output without triggering telephony."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "lat": 26.91,
            "lon": 75.78,
            "location_name": "Jaipur Low Risk",
            "farmer_name": "Sita Ram",
            "farmer_phone": "+919999999992",
            "crop_name": "Mustard",
            "language": "hi",
            "temperature": 22.0,
            "humidity": 55.0,
            "rainfall": 10.0,
            "wind_speed": 12.0,
            "pressure": 1014.0
        }
        resp = await client.post("/api/v1/weather/disaster-risk", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        pred = data["predictions"][0]
        assert pred["risk_level"] == "LOW"
        assert pred["risk_score"] < 40.0
        assert data["alert"]["should_alert"] is False
        assert data["alert"]["alert_status"] == "DISPLAY_ONLY"


@pytest.mark.asyncio
async def test_04_missing_phone_number_behavior():
    """Verify disaster prediction succeeds with warning banner but suppresses phone call if no phone is given."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "lat": 26.91,
            "lon": 75.78,
            "location_name": "Jaipur Unlinked Farm",
            "farmer_name": "Anonymous",
            "farmer_phone": None,  # No phone number
            "crop_name": "Wheat",
            "temperature": 26.0,
            "humidity": 95.0,
            "rainfall": 120.0,
            "wind_speed": 28.0,
            "pressure": 994.0
        }
        resp = await client.post("/api/v1/weather/disaster-risk", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["predictions"][0]["risk_level"] in ["HIGH", "CRITICAL"]
        assert data["alert"]["should_alert"] is False
        assert data["alert"]["alert_status"] == "NO_PHONE"
        assert "no verified farmer phone" in data["alert"]["reason"].lower()


@pytest.mark.asyncio
async def test_05_duplicate_alert_suppression_and_escalation():
    """Verify duplicate alert suppression within cooldown window and immediate escalation on severity change."""
    test_phone = "+919876543299"
    test_loc = "Kota Farm"

    # Step 1: Dispatch HIGH flood alert
    high_pred = {
        "disaster_type": "Flood Risk",
        "risk_level": "HIGH",
        "risk_score": 78.0,
        "confidence": 0.85,
        "trigger_factors": ["High rainfall"]
    }
    dec1 = disaster_alert_service.evaluate_alert_decision(
        prediction=high_pred,
        farmer_phone=test_phone,
        farmer_name="Kisan Test",
        location_name=test_loc,
        language="en"
    )
    assert dec1["should_alert"] is True
    assert dec1["alert_status"] == "ELIGIBLE"

    # Simulate recorded call in dedup cache
    dedup_key = disaster_alert_service._build_dedup_key(test_phone, "Flood Risk", test_loc)
    disaster_alert_service.alert_history[dedup_key] = (time.time(), "HIGH", "call-id-test-1")

    # Step 2: Repeat same HIGH alert immediately -> must be suppressed
    dec2 = disaster_alert_service.evaluate_alert_decision(
        prediction=high_pred,
        farmer_phone=test_phone,
        farmer_name="Kisan Test",
        location_name=test_loc,
        language="en"
    )
    assert dec2["should_alert"] is False
    assert dec2["alert_status"] == "SKIPPED_COOLDOWN"
    assert dec2["cooldown_remaining_seconds"] > 0

    # Step 3: Risk escalates from HIGH to CRITICAL -> escalation bypasses cooldown immediately!
    crit_pred = {
        "disaster_type": "Flood Risk",
        "risk_level": "CRITICAL",
        "risk_score": 96.0,
        "confidence": 0.98,
        "trigger_factors": ["Catastrophic rainfall"]
    }
    dec3 = disaster_alert_service.evaluate_alert_decision(
        prediction=crit_pred,
        farmer_phone=test_phone,
        farmer_name="Kisan Test",
        location_name=test_loc,
        language="en"
    )
    assert dec3["should_alert"] is True
    assert dec3["alert_status"] == "ELIGIBLE"
    assert dec3["severity"] == "CRITICAL"


@pytest.mark.asyncio
async def test_06_multilingual_alert_message_generation():
    """Verify localized voice alert generation across languages."""
    hi_msg = disaster_alert_service._generate_localized_alert_message("Flood Risk", "hi")
    assert "बाढ़" in hi_msg

    gu_msg = disaster_alert_service._generate_localized_alert_message("Flood Risk", "gu")
    assert "પૂર" in gu_msg

    mr_msg = disaster_alert_service._generate_localized_alert_message("Flood Risk", "mr")
    assert "महापुरा" in mr_msg or "धोका" in mr_msg

    en_msg = disaster_alert_service._generate_localized_alert_message("Flood Risk", "en")
    assert "flood" in en_msg.lower()


@pytest.mark.asyncio
async def test_07_open_meteo_live_weather_integration():
    """Verify disaster endpoint automatically queries Open-Meteo when coordinates are provided without manual weather numbers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "lat": 26.9124,
            "lon": 75.7873,
            "location_name": "Jaipur Live",
            "farmer_phone": "+919999999994",
            "language": "en"
        }
        resp = await client.post("/api/v1/weather/disaster-risk", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert "temperature" in data["weather_metrics"]
        assert "humidity" in data["weather_metrics"]
        assert "rainfall" in data["weather_metrics"]
        assert "wind_speed" in data["weather_metrics"]
        assert "pressure" in data["weather_metrics"]
        assert data["predictions"][0]["disaster_type"] in ["Low Risk", "Flood Risk", "Cyclone Risk", "Drought Risk"]
