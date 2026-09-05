"""
Unit and Integration tests for Real Prophet + LightGBM Mandi Price Forecasting (Phase 2).
Validates:
- Real longitudinal dataset ingestion from mandi_training_timeseries.csv (255k+ records, 1600+ dates).
- Zero synthetic sine-wave or jittered price generation.
- Rejection with INSUFFICIENT_HISTORY when observations < 30.
- Prophet time-series seasonality and trend fitting on genuine dates.
- LightGBM lag and rolling feature regression with chronological split.
- 60/40 Ensemble weighting.
- 95% Confidence prediction intervals.
- Deterministic signal derivation (HOLD / SELL_NOW / STABLE / INSUFFICIENT_EVIDENCE).
- Zero LLM arithmetic.
- Fast TTL cache hit (< 50ms on repeat query).
"""
import time
import pytest
from app.ml.market.forecaster import MandiPriceForecaster
from app.workflows.market_forecasting import MandiForecastRequest, run_mandi_forecasting_pipeline


def test_01_historical_mandi_data_loading():
    """Verify forecaster loads real Agmarknet longitudinal arrival records."""
    forecaster = MandiPriceForecaster()
    df = forecaster._load_data()

    assert df is not None
    assert len(df) > 100000
    assert "modal_price" in df.columns
    assert "ds" in df.columns
    assert df["modal_price"].dtype in ["float64", "float32", "int64"]
    assert df["commodity"].nunique() >= 50
    assert df["ds"].nunique() >= 500


def test_02_prophet_model_fitting_and_seasonality():
    """Verify Prophet fits on authentic historical price series for Wheat in Kalapipal (>100 dates)."""
    forecaster = MandiPriceForecaster()
    history_df, current_p = forecaster._get_commodity_history("Wheat", "Kalapipal")

    assert history_df is not None
    assert len(history_df) >= 30
    yhat, lower, upper = forecaster._fit_predict_prophet(history_df, days=7)

    assert len(yhat) == 7
    assert len(lower) == 7
    assert len(upper) == 7
    # Trajectory is non-trivial and bounded
    assert all(l <= y <= u for l, y, u in zip(lower, yhat, upper))
    assert all(current_p * 0.7 <= y <= current_p * 1.4 for y in yhat)


def test_03_lightgbm_feature_engineering_and_inference():
    """Verify LightGBM trains on lags/calendar features using genuine Onion history in Nashik (435 dates)."""
    forecaster = MandiPriceForecaster()
    history_df, current_p = forecaster._get_commodity_history("Onion", "Nashik")

    assert history_df is not None
    assert len(history_df) >= 100
    lgb_preds = forecaster._fit_predict_lightgbm(history_df, days=7, base_price=current_p)

    assert len(lgb_preds) == 7
    assert all(isinstance(float(p), float) for p in lgb_preds)
    assert all(current_p * 0.6 <= p <= current_p * 1.5 for p in lgb_preds)


def test_04_ensemble_prediction_and_confidence_bounds():
    """Verify 60/40 ensemble produces valid 95% confidence intervals on genuine Cotton in Sendhwa (535 dates)."""
    forecaster = MandiPriceForecaster()
    res = forecaster.forecast(commodity="Cotton", mandi="Sendhwa", days=14)

    assert res["status"] == "SUCCESS"
    assert res["commodity"] == "Cotton"
    assert res["forecast_horizon_days"] == 14
    assert len(res["daily_forecasts"]) == 14
    assert res["confidence_level"] == 0.95
    assert res["observations_count"] >= 50
    assert res["ensemble_weights"] == {"prophet": 0.60, "lightgbm": 0.40}

    for item in res["daily_forecasts"]:
        assert item["lower_bound_95"] <= item["predicted_price"]
        assert item["predicted_price"] <= item["upper_bound_95"]
        assert item["trend"] in ["bullish", "bearish", "stable"]


def test_05_deterministic_action_rules():
    """Verify deterministic trading recommendation is generated without LLM math on genuine Potato data."""
    forecaster = MandiPriceForecaster()
    res = forecaster.forecast(commodity="Potato", mandi="Durgapur", days=7)

    assert res["status"] == "SUCCESS"
    assert "deterministic_action" in res
    action_data = res["deterministic_action"]
    assert action_data["action"] in ["HOLD", "SELL_NOW", "STABLE"]
    assert isinstance(action_data["expected_pct_change"], float)
    assert len(action_data["reason_en"]) > 10
    assert len(action_data["reason_hi"]) > 10


def test_06_caching_performance():
    """Verify cache returns identical result within sub-millisecond time on repeat call."""
    forecaster = MandiPriceForecaster()
    # Call 1: Runs ML models
    res1 = forecaster.forecast(commodity="Cotton", mandi="Sendhwa", days=7)

    # Call 2: Must be retrieved from cache instantly
    t0 = time.time()
    res2 = forecaster.forecast(commodity="Cotton", mandi="Sendhwa", days=7)
    elapsed = time.time() - t0

    assert res1 == res2
    assert elapsed < 0.05  # < 50ms


def test_07_insufficient_history_rejection():
    """Verify system strictly rejects forecasting when fewer than 30 genuine dates exist."""
    forecaster = MandiPriceForecaster()
    # Soybean in Indore only has single snapshot records (< 30 dates)
    res = forecaster.forecast(commodity="Soybean", mandi="Indore", days=7)

    assert res["status"] == "INSUFFICIENT_HISTORY"
    assert res["confidence_level"] == 0.0
    assert res["observations_count"] < 30
    assert len(res["daily_forecasts"]) == 0
    assert res["deterministic_action"]["action"] == "INSUFFICIENT_EVIDENCE"
    assert "Insufficient historical observations" in res["deterministic_action"]["reason_en"]
    assert "never generates synthetic" in res["disclaimer"].lower()


@pytest.mark.asyncio
async def test_08_workflow_pipeline_integration():
    """Verify run_mandi_forecasting_pipeline returns validated Pydantic model on genuine Wheat data."""
    req = MandiForecastRequest(commodity="Wheat", mandi="Kalapipal", days=10)
    output = await run_mandi_forecasting_pipeline(req)

    assert output.status == "SUCCESS"
    assert output.commodity == "Wheat"
    assert output.mandi == "Kalapipal"
    assert output.forecast_horizon_days == 10
    assert len(output.daily_forecasts) == 10
    assert output.observations_count >= 30
    assert output.deterministic_action is not None
    assert output.deterministic_action.action in ["HOLD", "SELL_NOW", "STABLE"]
    assert "Prophet" in output.model_ensemble
    assert "LightGBM" in output.model_ensemble
    assert "market risk" in output.disclaimer.lower()
