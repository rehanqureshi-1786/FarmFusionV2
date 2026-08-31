"""
Pydantic v2 schemas for Mandi Price Intelligence, Comparisons, Alerts, and Advisory.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# 1. BASE PRICE SCHEMAS
# =============================================================================

class MarketPriceResponse(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
    arrival_date: str
    min_price: float
    max_price: float
    modal_price: float
    source: str = "Agmarknet Live"

    model_config = ConfigDict(from_attributes=True)


class MarketPriceListResponse(BaseModel):
    data: List[MarketPriceResponse]
    count: int
    region: str


class PricePredictionPoint(BaseModel):
    month: str
    predicted_price: float
    trend: str
    confidence: float


class MarketPredictionRequest(BaseModel):
    commodity: str
    state: str
    district: Optional[str] = None
    current_price: Optional[float] = None
    prediction_months: int = 3


class MarketPredictionResponse(BaseModel):
    commodity: str
    region: str
    current_price: float
    predictions: List[PricePredictionPoint]
    best_time_to_sell: str
    ai_analysis: str
    source: str


# =============================================================================
# 2. FEATURE 1: BEST MANDI NEAR ME SCHEMAS
# =============================================================================

class MandiProximityItem(BaseModel):
    market_id: Optional[str] = None
    market: str
    district: str
    state: str
    distance_km: Optional[float] = None
    modal_price: float
    min_price: float
    max_price: float
    arrival_date: str
    unit: str = "₹/Quintal"
    source: str
    freshness_status: str = "FRESH"  # FRESH, RECENT, STALE
    practical_score: float = 0.0
    ranking_reason: str = ""
    is_best_practical: bool = False
    is_highest_price: bool = False
    wording_label: str = "सबसे अधिक दर्ज भाव"


class BestMandiResponse(BaseModel):
    commodity: str
    reference_location: Dict[str, Any]
    best_mandi: Optional[MandiProximityItem] = None
    best_practical_mandi: Optional[MandiProximityItem] = None
    highest_price_mandi: Optional[MandiProximityItem] = None
    ranked_mandis: List[MandiProximityItem]
    total_found: int
    status: str = "SUCCESS"  # SUCCESS, LOCATION_REQUIRED, NO_DATA
    disclaimer: str = (
        "यह स्कोर केवल दर्ज भाव, दूरी और डेटा ताजगी पर आधारित व्यावहारिक रैंकिंग है। "
        "वास्तविक लाभ दूरी, परिवहन और तुलाई खर्च पर निर्भर करता है।"
    )


# =============================================================================
# 3. FEATURE 2: MANDI COMPARISON SCHEMAS
# =============================================================================

class MarketComparisonItem(BaseModel):
    market: str
    district: Optional[str] = None
    state: Optional[str] = None
    modal_price: float
    min_price: float
    max_price: float
    arrival_date: str
    unit: str = "₹/Quintal"
    source: str


class MandiComparisonDetail(BaseModel):
    higher_market: str  # market name or "EQUAL" or "NOT_FOUND"
    price_difference: float
    percentage_difference: float
    unit: str = "₹/Quintal"
    summary_hi: str
    summary_en: str


class MandiComparisonResponse(BaseModel):
    commodity: str
    market_a: MarketComparisonItem
    market_b: MarketComparisonItem
    comparison: MandiComparisonDetail


# =============================================================================
# 4. FEATURE 3: PRICE OPPORTUNITY ALERT SCHEMAS
# =============================================================================

class PriceAlertCreate(BaseModel):
    commodity: str = Field(..., description="Crop or commodity name, e.g. Wheat, Mustard")
    market: Optional[str] = Field(default=None, description="Optional specific mandi location")
    target_price: Optional[float] = Field(default=None, description="Target absolute price threshold in ₹/Quintal")
    direction: str = Field(default="ABOVE", description="ABOVE or BELOW")
    target_percentage_change: Optional[float] = Field(default=None, description="Percentage change threshold e.g. 5.0")
    user_id: Optional[str] = Field(default="default_user", description="User or device identifier")


class PriceAlertResponse(BaseModel):
    id: int
    user_id: str
    commodity: str
    market: Optional[str]
    target_price: Optional[float]
    direction: str
    target_percentage_change: Optional[float]
    base_price: float
    status: str
    created_at: str
    triggered_at: Optional[str] = None
    notification_status: str

    model_config = ConfigDict(from_attributes=True)


class PriceAlertListResponse(BaseModel):
    total: int
    alerts: List[PriceAlertResponse]


# =============================================================================
# 5. FEATURE 4 & 6: SELL-NOW VS WAIT ADVISORY SCHEMAS
# =============================================================================

class AdvisoryObserved(BaseModel):
    price: float
    date: str
    market: str
    source: str
    unit: str = "₹/Quintal"


class AdvisoryForecast(BaseModel):
    horizon_days: int
    projected_price: float
    expected_change: float
    percentage_change: float
    trend: str  # bullish, bearish, stable
    confidence_level: float
    lower_bound_95: float
    upper_bound_95: float
    model_name: str


class AdvisoryDetail(BaseModel):
    signal: str  # FAVORABLE_TO_SELL, POSSIBLE_UPSIDE, STABLE, INSUFFICIENT_EVIDENCE
    recommendation_hi: str
    recommendation_en: str
    reasoning_factors: List[str]


class MandiAdvisoryResponse(BaseModel):
    commodity: str
    market: str
    observed: AdvisoryObserved
    forecast: AdvisoryForecast
    advisory: AdvisoryDetail
    disclaimer: str = (
        "मॉडल केवल ऐतिहासिक रुझानों और सांख्यिकीय संकेतों के आधार पर अनुमान प्रस्तुत करता है। "
        "यह कोई निश्चित वित्तीय गारंटी नहीं है।"
    )


# =============================================================================
# 6. FEATURE 5: FORECAST EXPLANATION SCHEMAS
# =============================================================================

class ForecastFactor(BaseModel):
    factor_name: str
    signal_type: str  # MOMENTUM, SEASONAL, ARRIVAL, RESIDUAL
    description_hi: str
    description_en: str
    impact: str  # POSITIVE, NEGATIVE, NEUTRAL


class ForecastExplanationResponse(BaseModel):
    commodity: str
    market: str
    forecast_trend: str
    confidence_level: float
    factors: List[ForecastFactor]
    disclaimer: str
