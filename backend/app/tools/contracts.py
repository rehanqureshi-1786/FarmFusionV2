"""
Canonical Tool Contracts & Capability Normalization for FarmFusion.
Establishes the typed contract boundary between SemanticFrame required_capabilities
and FarmFusion's specialist execution tools.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field, field_validator

from app.schemas.semantic_frame import CapabilityType, RequiredInput


class ToolStatus(str, Enum):
    """Canonical status codes returned by all FarmFusion tools."""
    SUCCESS = "success"
    INVALID_INPUT = "invalid_input"
    MISSING_INPUT = "missing_input"
    REQUIRES_PHOTO = "requires_photo"
    INSUFFICIENT_DATA = "insufficient_data"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    SAFETY_BLOCKED = "safety_blocked"
    NETWORK_ERROR = "network_error"
    NOT_FOUND = "not_found"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    ERROR = "error"


class ProvenanceMetadata(BaseModel):
    """Provenance tracking for all numerical, factual, and algorithmic outputs."""
    source: str = Field(..., description="Authoritative source or API (e.g. Open-Meteo, Agmarknet, ICAR)")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model: Optional[str] = Field(default=None, description="ML/Statistical model name if applicable")
    model_version: Optional[str] = Field(default=None, description="Version tag of the model")
    confidence: Optional[float] = Field(default=None, description="Model or retrieval confidence score [0.0 - 1.0]")
    estimated: bool = Field(default=False, description="Whether value is forecasted/simulated vs measured")
    estimated_vs_measured: str = Field(default="measured", description="'measured', 'estimated', or 'unavailable'")
    data_age: Optional[str] = Field(default=None, description="Freshness of underlying observation")
    location: Optional[str] = Field(default=None, description="Geographic bounding of data")


class ToolResult(BaseModel):
    """Canonical envelope returned by every FarmFusion tool execution."""
    status: ToolStatus
    capability: Optional[str] = Field(default=None, description="Canonical CapabilityType executed")
    tool_name: Optional[str] = Field(default=None, description="Exact tool registered in registry")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Structured payload conforming to tool output schema")
    confidence: Optional[float] = Field(default=None, description="Overall tool execution confidence")
    provenance: ProvenanceMetadata
    message: str = Field(..., description="Human/LLM-readable English summary message")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings or caveats")
    localized_message: Optional[Dict[str, str]] = Field(default=None, description="Localized messages (hi, mr, gu, etc.)")


# =============================================================================
# 1. Weather Tool Schemas
# =============================================================================

class WeatherInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    location_name: Optional[str] = Field(default=None, description="Optional village or district name")


class WeatherOutput(BaseModel):
    temperature_c: float
    relative_humidity_pct: float
    rainfall_mm: float
    wind_speed_kmh: float
    weather_condition: str
    is_rainy: bool


# =============================================================================
# 2. Smart Irrigation Tool Schemas
# =============================================================================

class SmartIrrigationInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    crop: Optional[str] = Field(default=None, description="Crop name (e.g. Wheat, Cotton)")
    soil_moisture: Optional[float] = Field(default=None, description="Observed volumetric soil moisture percentage (0-100)")
    forecast_rain_mm: Optional[float] = Field(default=None, description="Forecasted rainfall in upcoming 24 hours")
    language: str = Field(default="hi")


class SmartIrrigationOutput(BaseModel):
    status: str  # DEFICIT, OPTIMAL, SATURATED
    irrigation_need_score: int  # 0 to 100
    status_badge: Optional[str] = None
    action: Optional[str] = None  # APPLY_IRRIGATION, HOLD_IRRIGATION, DRAIN_WATER
    actionable_advice: Optional[str] = None
    advice: Optional[str] = None
    next_irrigation_window: str
    root_zone_moisture_percent: Optional[float] = None
    watering_hours_recommended: Optional[float] = None
    next_24h_rain_sum_mm: Optional[float] = None



# =============================================================================
# 3. Disaster Risk Tool Schemas
# =============================================================================

class DisasterRiskInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    crop_name: Optional[str] = Field(default=None)
    days: int = Field(default=7, ge=1, le=14)
    location_name: Optional[str] = Field(default=None)


class DisasterRiskOutput(BaseModel):
    hazard_level: str  # LOW, MODERATE, HIGH, SEVERE
    active_hazards: List[str]  # FLOOD, DROUGHT, CYCLONE, HEATWAVE
    advisory: str
    risk_score: float


# =============================================================================
# 4. Crop Recommendation Tool Schemas
# =============================================================================

class CropRecommendationInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    soil_type: Optional[str] = Field(default=None, description="Soil classification (e.g. Sandy Soil, Black Soil)")
    nitrogen: Optional[float] = Field(default=None, ge=0.0)
    phosphorus: Optional[float] = Field(default=None, ge=0.0)
    potassium: Optional[float] = Field(default=None, ge=0.0)
    ph: Optional[float] = Field(default=None, ge=0.0, le=14.0)
    season: Optional[str] = Field(default=None, description="Kharif, Rabi, Zaid")
    state: Optional[str] = Field(default=None)


class RecommendedCropItem(BaseModel):
    crop_name: str
    suitability_score: float
    suitability_level: str
    contributing_factors: List[str] = Field(default_factory=list)


class CropRecommendationOutput(BaseModel):
    recommendations: List[RecommendedCropItem]
    mode: str  # MODE_A_XGBOOST, MODE_B_AGRONOMIC
    primary_crop: str


# =============================================================================
# 5. Disease Detection Tool Schemas
# =============================================================================

class DiseaseDetectionInput(BaseModel):
    image_bytes: Optional[bytes] = Field(default=None, description="Raw image bytes of infected leaf")
    image_path: Optional[str] = Field(default=None, description="File path or URL to image")
    crop: Optional[str] = Field(default=None, description="Crop name if known")
    language: str = Field(default="hi")


class DiseaseDetectionOutput(BaseModel):
    disease_name: str
    crop_name: str
    confidence: float
    confidence_tier: str  # high, medium, low, unclear
    treatment_steps: List[str] = Field(default_factory=list)
    prevention_tips: List[str] = Field(default_factory=list)
    farmer_message: str


# =============================================================================
# 6. Mandi Tools Schemas
# =============================================================================

class MandiCurrentPriceInput(BaseModel):
    crop: str = Field(..., min_length=1, description="Commodity/crop name")
    market: Optional[str] = Field(default=None, description="Specific APMC Mandi name")
    district: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)


class MandiCurrentPriceOutput(BaseModel):
    commodity: str
    market: str
    modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_unit: str = "Rs/Quintal"
    arrival_date: str


class MandiHistoryInput(BaseModel):
    crop: str = Field(..., min_length=1)
    market: Optional[str] = Field(default=None)
    days: int = Field(default=30, ge=1, le=365)


class MandiHistoryOutput(BaseModel):
    commodity: str
    market: str
    data_points: List[Dict[str, Any]]
    trend: str  # RISING, FALLING, STABLE


class MandiForecastInput(BaseModel):
    crop: str = Field(..., min_length=1)
    market: str = Field(..., min_length=1)
    forecast_days: int = Field(default=7, ge=1, le=30)


class MandiForecastOutput(BaseModel):
    commodity: str
    market: str
    forecast_days: int
    predicted_trend: str  # UPWARD, DOWNWARD, NEUTRAL
    predicted_modal_price_end: float
    daily_forecasts: List[Dict[str, Any]]


class MandiComparisonInput(BaseModel):
    crop: str = Field(..., min_length=1)
    market_a: str = Field(..., min_length=1)
    market_b: str = Field(..., min_length=1)


class MandiComparisonOutput(BaseModel):
    commodity: str
    market_a: str
    price_a: float
    market_b: str
    price_b: float
    price_difference: float
    better_market: str
    recommendation: str


class MandiDecisionInput(BaseModel):
    crop: str = Field(..., min_length=1)
    market: Optional[str] = Field(default=None)
    holding_days: int = Field(default=7, ge=1, le=30)


class MandiDecisionOutput(BaseModel):
    commodity: str
    market: str
    action: str  # SELL_NOW, HOLD
    confidence: float
    reason: str
    expected_gain_pct: float


# =============================================================================
# 7. RAG Knowledge & Government Scheme Tools Schemas
# =============================================================================

class RAGKnowledgeInput(BaseModel):
    query: str = Field(..., min_length=2)
    crop: Optional[str] = Field(default=None)
    doc_type: Optional[str] = Field(default=None, description="guideline, treatment, scheme")
    top_k: int = Field(default=3, ge=1, le=10)


class RAGKnowledgeOutput(BaseModel):
    matches: List[Dict[str, Any]]
    top_similarity: float
    primary_guidance: str


class GovernmentSchemeInput(BaseModel):
    query: str = Field(..., min_length=2)
    state: Optional[str] = Field(default=None)
    crop_name: Optional[str] = Field(default=None)


class GovernmentSchemeOutput(BaseModel):
    schemes: List[Dict[str, Any]]
    eligibility_summary: str
    application_portal: Optional[str] = None


# =============================================================================
# 8. Animal Intrusion IoT Schemas
# =============================================================================

class AnimalDetectionInput(BaseModel):
    device_id: Optional[str] = Field(default="NODE_01")


class AnimalDetectionOutput(BaseModel):
    overall_status: str  # ALL_CLEAR, INTRUSION_DETECTED, NODE_OFFLINE
    detected_sensors: List[str]
    offline_sensors: List[str]
    alert_message: str


# =============================================================================
# 9. Navigation Schemas (Strict Whitelist)
# =============================================================================

class AllowedNavigationDestination(str, Enum):
    DISEASE_SCAN = "DISEASE_SCAN"
    MANDI = "MANDI"
    WEATHER = "WEATHER"
    CROP_RECOMMENDATION = "CROP_RECOMMENDATION"
    FINANCIAL_SERVICES = "FINANCIAL_SERVICES"
    DASHBOARD = "DASHBOARD"


# Destination to Kotlin Android navigation route mapping
NAVIGATION_ROUTE_MAP = {
    AllowedNavigationDestination.DISEASE_SCAN: "crop_disease",
    AllowedNavigationDestination.MANDI: "mandi_rates",
    AllowedNavigationDestination.WEATHER: "weather_detail",
    AllowedNavigationDestination.CROP_RECOMMENDATION: "crop_recommendation",
    AllowedNavigationDestination.FINANCIAL_SERVICES: "financial_schemes",
    AllowedNavigationDestination.DASHBOARD: "dashboard",
}

# Alias resolution mapping for legacy or alternative strings
NAVIGATION_ALIAS_MAP = {
    "disease_scan": AllowedNavigationDestination.DISEASE_SCAN,
    "crop_disease": AllowedNavigationDestination.DISEASE_SCAN,
    "disease_detection": AllowedNavigationDestination.DISEASE_SCAN,
    "mandi": AllowedNavigationDestination.MANDI,
    "mandi_rates": AllowedNavigationDestination.MANDI,
    "market_prices": AllowedNavigationDestination.MANDI,
    "market": AllowedNavigationDestination.MANDI,
    "weather": AllowedNavigationDestination.WEATHER,
    "weather_detail": AllowedNavigationDestination.WEATHER,
    "crop_recommendation": AllowedNavigationDestination.CROP_RECOMMENDATION,
    "crops": AllowedNavigationDestination.CROP_RECOMMENDATION,
    "financial_services": AllowedNavigationDestination.FINANCIAL_SERVICES,
    "financial_schemes": AllowedNavigationDestination.FINANCIAL_SERVICES,
    "government_schemes": AllowedNavigationDestination.FINANCIAL_SERVICES,
    "schemes": AllowedNavigationDestination.FINANCIAL_SERVICES,
    "dashboard": AllowedNavigationDestination.DASHBOARD,
    "farm_dashboard": AllowedNavigationDestination.DASHBOARD,
    "home": AllowedNavigationDestination.DASHBOARD,
}


class NavigationInput(BaseModel):
    destination: str = Field(..., description="Target screen identifier")
    params: Optional[Dict[str, Any]] = Field(default=None)

    @field_validator("destination")
    @classmethod
    def validate_destination(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean in NAVIGATION_ALIAS_MAP or v.upper() in AllowedNavigationDestination.__members__:
            return v
        allowed = list(AllowedNavigationDestination.__members__.keys())
        raise ValueError(f"Destination '{v}' is not permitted. Whitelisted targets: {allowed}")


class NavigationOutput(BaseModel):
    action: str = "NAVIGATE"
    destination: AllowedNavigationDestination
    android_route: str
    required_input: Optional[RequiredInput] = None
    message: str


# =============================================================================
# 10. Calling Schemas (Vobiz Delegation)
# =============================================================================

class CallingInput(BaseModel):
    phone: str = Field(..., description="Farmer E.164 phone number (e.g. +919876543210)")
    farmer_name: str = Field(..., min_length=1)
    call_type: str = Field(default="general_advisory")
    language: str = Field(default="hi")
    location: Optional[str] = Field(default="India")
    crop_name: Optional[str] = Field(default=None)
    mandi_name: Optional[str] = Field(default=None)
    current_price: Optional[float] = Field(default=None)
    target_price: Optional[float] = Field(default=None)
    weather_summary: Optional[str] = Field(default=None)
    agent_instruction: Optional[str] = Field(default=None)


class CallingOutput(BaseModel):
    status: str  # success, error, cooldown_blocked
    call_id: Optional[str] = None
    message: str
    phone: str
    farmer_name: str


# =============================================================================
# Canonical Tool Contract Definition
# =============================================================================

class ToolContract(BaseModel):
    """Specification metadata and schemas for an executable FarmFusion tool."""
    capability: CapabilityType
    tool_name: str
    description: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    required_fields: List[str]
    optional_fields: List[str]
    provenance_source: str
    default_timeout_seconds: float = 10.0
    is_read_only: bool = True


# Master Capability-to-Contract Catalog
CAPABILITY_CONTRACTS: Dict[CapabilityType, ToolContract] = {
    CapabilityType.WEATHER: ToolContract(
        capability=CapabilityType.WEATHER,
        tool_name="weather_tool",
        description="Fetches real-time physical temperature, humidity, rainfall, and wind from Open-Meteo.",
        input_schema=WeatherInput,
        output_schema=WeatherOutput,
        required_fields=["latitude", "longitude"],
        optional_fields=["location_name"],
        provenance_source="Open-Meteo Physical NWP",
        default_timeout_seconds=5.0,
    ),
    CapabilityType.SMART_IRRIGATION: ToolContract(
        capability=CapabilityType.SMART_IRRIGATION,
        tool_name="smart_irrigation_tool",
        description="Computes deterministic agronomic soil-moisture deficit and 24h precipitation irrigation advisory.",
        input_schema=SmartIrrigationInput,
        output_schema=SmartIrrigationOutput,
        required_fields=["latitude", "longitude"],
        optional_fields=["crop", "soil_moisture", "forecast_rain_mm", "language"],
        provenance_source="Open-Meteo Volumetric Soil Moisture + Deterministic Agronomic Rules",
        default_timeout_seconds=6.0,
    ),
    CapabilityType.DISASTER_RISK: ToolContract(
        capability=CapabilityType.DISASTER_RISK,
        tool_name="disaster_risk_tool",
        description="Predicts flood, drought, cyclone, and heatwave hazards using 4-model ML ensemble.",
        input_schema=DisasterRiskInput,
        output_schema=DisasterRiskOutput,
        required_fields=["latitude", "longitude"],
        optional_fields=["crop_name", "days", "location_name"],
        provenance_source="DisasterPredictorAI 4-Model ML Ensemble + Open-Meteo NWP",
        default_timeout_seconds=8.0,
    ),
    CapabilityType.CROP_RECOMMENDATION: ToolContract(
        capability=CapabilityType.CROP_RECOMMENDATION,
        tool_name="crop_recommendation_tool",
        description="Recommends optimal agricultural crops using XGBoost V2 model or ICAR suitability rules.",
        input_schema=CropRecommendationInput,
        output_schema=CropRecommendationOutput,
        required_fields=["latitude", "longitude"],
        optional_fields=["soil_type", "nitrogen", "phosphorus", "potassium", "ph", "season", "state"],
        provenance_source="XGBoost Crop Model V2 / ICAR Agronomic Suitability Database",
        default_timeout_seconds=7.0,
    ),
    CapabilityType.DISEASE_DETECTION: ToolContract(
        capability=CapabilityType.DISEASE_DETECTION,
        tool_name="disease_detection_tool",
        description="Performs leaf disease diagnosis via EfficientNet-B3. Enforces photo gate if image missing.",
        input_schema=DiseaseDetectionInput,
        output_schema=DiseaseDetectionOutput,
        required_fields=[],
        optional_fields=["image_bytes", "image_path", "crop", "language"],
        provenance_source="EfficientNet-B3 38-Class Disease Model",
        default_timeout_seconds=10.0,
    ),
    CapabilityType.CURRENT_PRICE: ToolContract(
        capability=CapabilityType.CURRENT_PRICE,
        tool_name="mandi_current_price_tool",
        description="Retrieves authentic modal, min, and max market prices from longitudinal Agmarknet data.",
        input_schema=MandiCurrentPriceInput,
        output_schema=MandiCurrentPriceOutput,
        required_fields=["crop"],
        optional_fields=["market", "district", "state"],
        provenance_source="Agmarknet Government Mandi Records",
        default_timeout_seconds=5.0,
    ),
    CapabilityType.MANDI_CURRENT_PRICE: ToolContract(
        capability=CapabilityType.MANDI_CURRENT_PRICE,
        tool_name="mandi_current_price_tool",
        description="Retrieves authentic modal, min, and max market prices from longitudinal Agmarknet data.",
        input_schema=MandiCurrentPriceInput,
        output_schema=MandiCurrentPriceOutput,
        required_fields=["crop"],
        optional_fields=["market", "district", "state"],
        provenance_source="Agmarknet Government Mandi Records",
        default_timeout_seconds=5.0,
    ),
    CapabilityType.MANDI_HISTORY: ToolContract(
        capability=CapabilityType.MANDI_HISTORY,
        tool_name="mandi_history_tool",
        description="Retrieves historical price records and computed price trend over 1-365 days.",
        input_schema=MandiHistoryInput,
        output_schema=MandiHistoryOutput,
        required_fields=["crop"],
        optional_fields=["market", "days"],
        provenance_source="Agmarknet Longitudinal Historical Records",
        default_timeout_seconds=6.0,
    ),
    CapabilityType.MANDI_FORECAST: ToolContract(
        capability=CapabilityType.MANDI_FORECAST,
        tool_name="mandi_forecast_tool",
        description="Generates 1 to 30-day commodity price forecast using Prophet + LightGBM ensemble.",
        input_schema=MandiForecastInput,
        output_schema=MandiForecastOutput,
        required_fields=["crop", "market"],
        optional_fields=["forecast_days"],
        provenance_source="Prophet + LightGBM Mandi Forecast Pipeline",
        default_timeout_seconds=10.0,
    ),
    CapabilityType.MANDI_COMPARISON: ToolContract(
        capability=CapabilityType.MANDI_COMPARISON,
        tool_name="mandi_comparison_tool",
        description="Compares price spread, price differences, and net yield between two mandis.",
        input_schema=MandiComparisonInput,
        output_schema=MandiComparisonOutput,
        required_fields=["crop", "market_a", "market_b"],
        optional_fields=[],
        provenance_source="Agmarknet Market Differential Engine",
        default_timeout_seconds=6.0,
    ),
    CapabilityType.MANDI_DECISION: ToolContract(
        capability=CapabilityType.MANDI_DECISION,
        tool_name="mandi_decision_tool",
        description="Produces deterministic sell-now vs hold decision with projected return percentage.",
        input_schema=MandiDecisionInput,
        output_schema=MandiDecisionOutput,
        required_fields=["crop"],
        optional_fields=["market", "holding_days"],
        provenance_source="Deterministic Economic Threshold Engine + Mandi Forecaster",
        default_timeout_seconds=8.0,
    ),
    CapabilityType.RAG_KNOWLEDGE: ToolContract(
        capability=CapabilityType.RAG_KNOWLEDGE,
        tool_name="rag_knowledge_tool",
        description="Performs semantic search across 174+ ICAR documents using BGE-M3 embeddings and pgvector.",
        input_schema=RAGKnowledgeInput,
        output_schema=RAGKnowledgeOutput,
        required_fields=["query"],
        optional_fields=["crop", "doc_type", "top_k"],
        provenance_source="ICAR / Ministry of Agriculture Documents via pgvector HNSW",
        default_timeout_seconds=7.0,
    ),
    CapabilityType.GOVERNMENT_SCHEME: ToolContract(
        capability=CapabilityType.GOVERNMENT_SCHEME,
        tool_name="government_scheme_tool",
        description="Retrieves structured eligibility criteria, benefits, and portal URLs for welfare schemes.",
        input_schema=GovernmentSchemeInput,
        output_schema=GovernmentSchemeOutput,
        required_fields=["query"],
        optional_fields=["state", "crop_name"],
        provenance_source="Government Scheme Registry & Official Guidelines",
        default_timeout_seconds=6.0,
    ),
    CapabilityType.ANIMAL_ALERT: ToolContract(
        capability=CapabilityType.ANIMAL_ALERT,
        tool_name="animal_detection_tool",
        description="Queries IoT perimeter PIR/IR sensors for live wildlife/stray animal intrusion events.",
        input_schema=AnimalDetectionInput,
        output_schema=AnimalDetectionOutput,
        required_fields=[],
        optional_fields=["device_id"],
        provenance_source="ESP32 IoT Perimeter Hardware Telemetry",
        default_timeout_seconds=4.0,
    ),
    CapabilityType.ANIMAL_DETECTION: ToolContract(
        capability=CapabilityType.ANIMAL_DETECTION,
        tool_name="animal_detection_tool",
        description="Queries IoT perimeter PIR/IR sensors for live wildlife/stray animal intrusion events.",
        input_schema=AnimalDetectionInput,
        output_schema=AnimalDetectionOutput,
        required_fields=[],
        optional_fields=["device_id"],
        provenance_source="ESP32 IoT Perimeter Hardware Telemetry",
        default_timeout_seconds=4.0,
    ),
    CapabilityType.NAVIGATION: ToolContract(
        capability=CapabilityType.NAVIGATION,
        tool_name="navigation_tool",
        description="Validates and formats in-app navigation actions against the hardcoded Android whitelist.",
        input_schema=NavigationInput,
        output_schema=NavigationOutput,
        required_fields=["destination"],
        optional_fields=["params"],
        provenance_source="Kotlin Allowed Destinations Whitelist",
        default_timeout_seconds=1.0,
    ),
    CapabilityType.CALLING: ToolContract(
        capability=CapabilityType.CALLING,
        tool_name="calling_tool",
        description="Initiates outbound phone calls with automated agricultural voice advisory via Vobiz.",
        input_schema=CallingInput,
        output_schema=CallingOutput,
        required_fields=["phone", "farmer_name"],
        optional_fields=["call_type", "language", "location", "crop_name", "mandi_name", "current_price", "target_price", "weather_summary", "agent_instruction"],
        provenance_source="Vobiz Telephony Telecommunication Gateway",
        default_timeout_seconds=12.0,
        is_read_only=False,
    ),
}


# =============================================================================
# Helper Utilities
# =============================================================================

def get_tool_contract(capability: Union[CapabilityType, str]) -> Optional[ToolContract]:
    """Retrieve ToolContract by CapabilityType or string name."""
    if isinstance(capability, str):
        cap_clean = capability.strip().upper()
        for cap_enum, contract in CAPABILITY_CONTRACTS.items():
            if cap_enum.value == cap_clean or cap_enum.name == cap_clean:
                return contract
        return None
    return CAPABILITY_CONTRACTS.get(capability)


def map_capabilities_to_tools(required_capabilities: List[Union[CapabilityType, str]]) -> List[str]:
    """
    Deterministic mapping from SemanticFrame.required_capabilities
    to exact registered tool names. Deduplicates while preserving order.
    """
    tool_names: List[str] = []
    for cap in required_capabilities:
        contract = get_tool_contract(cap)
        if contract and contract.tool_name not in tool_names:
            tool_names.append(contract.tool_name)
    return tool_names
