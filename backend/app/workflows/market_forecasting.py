"""
Mandi Price Forecasting Workflow using real Prophet + LightGBM ensemble ML model.
Strictly adheres to Safety Rule #2:
"The LLM must NEVER predict mandi prices. Only the Prophet+LightGBM ML model produces
price forecasts. The LLM only narrates the model's output."
"""
from typing import Any, Dict, List, Optional
import structlog
from pydantic import BaseModel, Field

from app.ml.market.forecaster import mandi_forecaster

logger = structlog.get_logger(__name__)


class MandiForecastRequest(BaseModel):
    commodity: str = Field(..., description="Crop/Commodity name (e.g. Wheat, Mustard, Paddy)")
    mandi: str = Field(..., description="Mandi/Market location (e.g. Jaipur Mandi, Kota Mandi)")
    days: int = Field(default=7, ge=1, le=30, description="Forecast horizon in days")


class DailyPriceForecast(BaseModel):
    date: str
    predicted_price: float
    lower_bound_95: float
    upper_bound_95: float
    trend: str  # bullish, bearish, stable


class DeterministicTradingAction(BaseModel):
    action: str  # HOLD, SELL_NOW, STABLE
    expected_pct_change: float
    reason_en: str
    reason_hi: str


class MandiForecastResult(BaseModel):
    commodity: str
    mandi: str
    current_price: float
    forecast_horizon_days: int
    daily_forecasts: List[DailyPriceForecast]
    confidence_level: float = Field(default=0.95)
    model_ensemble: str
    ensemble_weights: Dict[str, float] = Field(default_factory=lambda: {"prophet": 0.60, "lightgbm": 0.40})
    deterministic_action: Optional[DeterministicTradingAction] = None
    disclaimer: str


async def run_mandi_forecasting_pipeline(request: MandiForecastRequest) -> MandiForecastResult:
    """
    Executes real Prophet + LightGBM ensemble model inference for mandi price forecasting.
    Includes 95% confidence bounds, deterministic recommendation signals, and strict safety disclaimer.
    """
    logger.info("mandi_price_forecast_pipeline_start", commodity=request.commodity, mandi=request.mandi, days=request.days)

    # Execute real Prophet + LightGBM ML forecaster
    ml_output = mandi_forecaster.forecast(
        commodity=request.commodity,
        mandi=request.mandi,
        days=request.days
    )

    daily_forecasts = [
        DailyPriceForecast(
            date=item["date"],
            predicted_price=item["predicted_price"],
            lower_bound_95=item["lower_bound_95"],
            upper_bound_95=item["upper_bound_95"],
            trend=item["trend"],
        )
        for item in ml_output["daily_forecasts"]
    ]

    action_obj = None
    if "deterministic_action" in ml_output:
        action_data = ml_output["deterministic_action"]
        action_obj = DeterministicTradingAction(
            action=action_data["action"],
            expected_pct_change=action_data["expected_pct_change"],
            reason_en=action_data["reason_en"],
            reason_hi=action_data["reason_hi"]
        )

    return MandiForecastResult(
        commodity=ml_output["commodity"],
        mandi=ml_output["mandi"],
        current_price=ml_output["current_price"],
        forecast_horizon_days=ml_output["forecast_horizon_days"],
        daily_forecasts=daily_forecasts,
        confidence_level=ml_output.get("confidence_level", 0.95),
        model_ensemble=ml_output["model_ensemble"],
        ensemble_weights=ml_output.get("ensemble_weights", {"prophet": 0.60, "lightgbm": 0.40}),
        deterministic_action=action_obj,
        disclaimer=ml_output["disclaimer"]
    )
