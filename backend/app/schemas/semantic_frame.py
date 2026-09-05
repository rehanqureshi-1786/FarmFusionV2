"""
Canonical Strongly-Typed Semantic Frame & Orchestration Data Contracts for FarmFusion.

Serves as the universal contract between:
ASR / Language Layer -> Intent & Entity Extraction -> Task Planner -> Tool Registry -> Specialist Agents -> Safety Validation -> Response & Actions.

Strictly adheres to Pydantic v2.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


# =============================================================================
# 1. CANONICAL ENUMS
# =============================================================================

class CanonicalIntent(str, Enum):
    """Supported canonical user intent types across all agricultural domains."""
    WEATHER = "weather"
    SMART_IRRIGATION = "smart_irrigation"
    IRRIGATION_ADVISORY = "irrigation_advisory"
    DISASTER_RISK = "disaster_risk"
    CROP_RECOMMENDATION = "crop_recommendation"
    DISEASE_DETECTION = "disease_detection"
    MANDI_PRICE = "mandi_price"
    MANDI_FORECAST = "mandi_forecast"
    MANDI_COMPARISON = "mandi_comparison"
    MANDI_DECISION = "mandi_decision"
    SELL_HOLD = "sell_hold"
    GOVERNMENT_SCHEME = "government_scheme"
    AGRICULTURAL_KNOWLEDGE = "agricultural_knowledge"
    ANIMAL_ALERT = "animal_alert"
    GENERAL_AGRICULTURE = "general_agriculture"
    NAVIGATION_REQUEST = "navigation_request"
    CALLING = "calling"
    REPEAT_LAST = "repeat_last"
    CLARIFICATION = "clarification"
    UNSUPPORTED = "unsupported"


class CapabilityType(str, Enum):
    """Specialist engine/tool capabilities that can be planned or invoked."""
    WEATHER = "WEATHER"
    SMART_IRRIGATION = "SMART_IRRIGATION"
    DISASTER_RISK = "DISASTER_RISK"
    CROP_RECOMMENDATION = "CROP_RECOMMENDATION"
    DISEASE_DETECTION = "DISEASE_DETECTION"
    CURRENT_PRICE = "CURRENT_PRICE"
    MANDI_CURRENT_PRICE = "MANDI_CURRENT_PRICE"
    MANDI_HISTORY = "MANDI_HISTORY"
    MANDI_FORECAST = "MANDI_FORECAST"
    MANDI_COMPARISON = "MANDI_COMPARISON"
    MANDI_DECISION = "MANDI_DECISION"
    RAG_KNOWLEDGE = "RAG_KNOWLEDGE"
    GOVERNMENT_SCHEME = "GOVERNMENT_SCHEME"
    ANIMAL_ALERT = "ANIMAL_ALERT"
    ANIMAL_DETECTION = "ANIMAL_DETECTION"
    CALLING = "CALLING"
    NAVIGATION = "NAVIGATION"
    UNSUPPORTED = "UNSUPPORTED"



class RequiredInput(str, Enum):
    """Explicit declaration of missing sensory or farmer input required to fulfill intent."""
    NONE = "NONE"
    LEAF_IMAGE = "LEAF_IMAGE"
    SOIL_REPORT = "SOIL_REPORT"
    FARM_LOCATION = "FARM_LOCATION"
    CROP_NAME = "CROP_NAME"
    MANDI_LOCATION = "MANDI_LOCATION"
    FARM_SIZE = "FARM_SIZE"
    OTHER = "OTHER"


class ActionIntent(str, Enum):
    """High-level action decided by orchestrator decision engine."""
    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    NAVIGATE = "NAVIGATE"
    REQUEST_INPUT = "REQUEST_INPUT"
    CALL = "CALL"
    NOTIFY = "NOTIFY"


class NavigationDestination(str, Enum):
    """Fixed whitelist of valid Android client navigation destinations."""
    DISEASE_SCAN = "DISEASE_SCAN"
    MANDI = "MANDI"
    WEATHER = "WEATHER"
    CROP_RECOMMENDATION = "CROP_RECOMMENDATION"
    FINANCIAL_SERVICES = "FINANCIAL_SERVICES"
    DASHBOARD = "DASHBOARD"
    ANIMAL_DETECTION = "ANIMAL_DETECTION"
    LANGUAGE_SELECTION = "LANGUAGE_SELECTION"
    BACK = "BACK"


# Direct mapping from NavigationDestination enum to Kotlin NavRoutes string constants
ANDROID_ROUTE_MAP: Dict[NavigationDestination, str] = {
    NavigationDestination.DISEASE_SCAN: "crop_disease",
    NavigationDestination.MANDI: "mandi_prices",
    NavigationDestination.WEATHER: "weather",
    NavigationDestination.CROP_RECOMMENDATION: "crop_recommendation",
    NavigationDestination.FINANCIAL_SERVICES: "financial_services",
    NavigationDestination.DASHBOARD: "dashboard",
    NavigationDestination.ANIMAL_DETECTION: "animal_detection",
    NavigationDestination.LANGUAGE_SELECTION: "language_selection",
    NavigationDestination.BACK: "back",
}


class RelativeDay(str, Enum):
    """First-class temporal anchor resolved from relative-day semantics (multilingual)."""
    UNSPECIFIED = "UNSPECIFIED"
    TODAY = "TODAY"
    TOMORROW = "TOMORROW"
    DAY_AFTER_TOMORROW = "DAY_AFTER_TOMORROW"
    NEXT_WEEK = "NEXT_WEEK"
    NEXT_7_DAYS = "NEXT_7_DAYS"
    THIS_WEEK = "THIS_WEEK"
    NEXT_MONTH = "NEXT_MONTH"
    EXPLICIT_DATE = "EXPLICIT_DATE"


class TimeContext(BaseModel):
    """Canonical temporal context attached to the semantic frame (requirement #3).

    Time is a first-class entity: the planner and specialist tools consume
    ``relative_day`` / ``resolved_date`` instead of relying on LLM text at
    synthesis time.
    """
    model_config = ConfigDict(extra="forbid")

    relative_day: RelativeDay = Field(default=RelativeDay.UNSPECIFIED)
    reference_date: Optional[str] = Field(default=None, description="ISO date the relative day anchors against")
    resolved_date: Optional[str] = Field(default=None, description="ISO date (YYYY-MM-DD) of the day the user asked about")
    horizon_days: int = Field(default=1, ge=1, le=30, description="Forecast window length in days")
    forecast_days: Optional[int] = Field(default=None, ge=1, le=30, description="Explicit multi-day horizon when requested")
    explicit_date: Optional[str] = Field(default=None, description="NCBI-style raw date token if explicitly stated")
    is_relative: bool = Field(default=False, description="True if resolved from a relative day word")
    raw_hint: Optional[str] = Field(default=None, description="Non-normalized surface token matched")

    @property
    def day_offset(self) -> int:
        """Zero-based offset from reference date to the requested target day."""
        mapping = {
            RelativeDay.TODAY: 0,
            RelativeDay.TOMORROW: 1,
            RelativeDay.DAY_AFTER_TOMORROW: 2,
            RelativeDay.NEXT_WEEK: 7,
            RelativeDay.THIS_WEEK: 0,
            RelativeDay.NEXT_7_DAYS: 0,
            RelativeDay.NEXT_MONTH: 30,
            RelativeDay.EXPLICIT_DATE: 0,
            RelativeDay.UNSPECIFIED: 0,
        }
        return mapping.get(self.relative_day, 0)


# =============================================================================
# 2. CONFIDENCE & ENTITY SCHEMAS
# =============================================================================

class ConfidenceSet(BaseModel):
    """Granular multi-dimensional confidence metrics across the semantic interpretation."""
    model_config = ConfigDict(extra="forbid")

    language_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of language/dialect identification")
    intent_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of primary intent classification")
    entity_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of extracted agricultural entities")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Harmonized composite confidence score")

    @field_validator("overall_confidence", mode="before")
    @classmethod
    def compute_or_validate_overall(cls, v: Any, info) -> float:
        if v is not None:
            return float(v)
        # Default harmonized composite: min of intent and entity
        data = info.data
        i_conf = data.get("intent_confidence", 0.5)
        e_conf = data.get("entity_confidence", 0.5)
        return round(min(i_conf, e_conf), 4)


class SoilValues(BaseModel):
    """Physical and chemical soil parameters without synthetic fabrication."""
    model_config = ConfigDict(extra="forbid")

    soil_type: Optional[str] = Field(None, description="Agronomic soil classification (e.g. Black Soil, Alluvial)")
    ph: Optional[float] = Field(None, ge=0.0, le=14.0, description="Soil pH value")
    nitrogen: Optional[float] = Field(None, ge=0.0, description="Nitrogen kg/ha (None if unmeasured)")
    phosphorus: Optional[float] = Field(None, ge=0.0, description="Phosphorus kg/ha (None if unmeasured)")
    potassium: Optional[float] = Field(None, ge=0.0, description="Potassium kg/ha (None if unmeasured)")
    organic_carbon: Optional[float] = Field(None, ge=0.0, le=100.0, description="Organic carbon percentage")


class FarmLocation(BaseModel):
    """Geographic context for weather, mandis, and crop suitability."""
    model_config = ConfigDict(extra="forbid")

    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    village: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None


class EntitySet(BaseModel):
    """
    Explicitly typed agricultural entities extracted from the query or conversational state.
    Strict rule: No hallucinated defaults. Missing entities MUST remain None/empty.
    """
    model_config = ConfigDict(extra="forbid")

    crop: Optional[str] = Field(None, description="Normalized crop name in English (e.g. 'Wheat', 'Tomato')")
    disease: Optional[str] = Field(None, description="Mentioned symptom or disease name")
    market: Optional[str] = Field(None, description="Primary mandi or agricultural market name")
    mandi: Optional[str] = Field(None, description="Alias for market")
    markets: List[str] = Field(default_factory=list, description="Multiple markets for comparison queries")
    village: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    farm_location: Optional[FarmLocation] = None
    timeframe: Optional[str] = Field(None, description="Relative or absolute timeframe (e.g. 'today', 'tomorrow', 'next week')")
    forecast_days: Optional[int] = Field(None, ge=1, le=30, description="Requested forecast horizon in days")
    time_context: Optional[TimeContext] = Field(
        default=None,
        description="First-class temporal context (relative_day, resolved_date, horizon). Planner and tools consume this field.",
    )
    soil_values: Optional[SoilValues] = None
    farm_size: Optional[float] = Field(None, ge=0.0, description="Acreage or land size")
    farm_size_unit: Optional[str] = Field(default="acre")
    quantity: Optional[float] = Field(None, ge=0.0, description="Quantity for trade or harvest")
    quantity_unit: Optional[str] = Field(default="quintal")
    season: Optional[str] = Field(None, description="Agronomic season: Kharif, Rabi, Zaid")
    additional_entities: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific extension slots")

    @field_validator("mandi", mode="before")
    @classmethod
    def sync_mandi_and_market(cls, v: Any, info) -> Optional[str]:
        if v:
            return v
        return info.data.get("market")


# =============================================================================
# 3. CONTEXT SCHEMAS
# =============================================================================

class UserContext(BaseModel):
    """Farmer profile and static farm context."""
    model_config = ConfigDict(extra="allow")

    user_id: Optional[str] = None
    registered_name: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_language: str = "hi"
    preferred_dialect: Optional[str] = None
    farm_location: Optional[FarmLocation] = None
    primary_crops: List[str] = Field(default_factory=list)
    soil_type: Optional[str] = None


class ConversationContext(BaseModel):
    """Multi-turn conversational tracking and accumulated state."""
    model_config = ConfigDict(extra="allow")

    turn_index: int = 0
    active_crop: Optional[str] = None
    last_intent: Optional[str] = None
    last_action: Optional[ActionIntent] = None
    last_destination: Optional[NavigationDestination] = None
    last_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    last_tool_outputs: Dict[str, Any] = Field(default_factory=dict)
    accumulated_slots: Dict[str, Any] = Field(default_factory=dict)
    pending_clarification: Optional[str] = None


# =============================================================================
# 4. REQUEST & SEMANTIC FRAME
# =============================================================================

class FarmerRequest(BaseModel):
    """Inbound farmer query envelope arriving from voice, text, or Android client."""
    model_config = ConfigDict(extra="allow")

    request_id: str
    session_id: str
    raw_text: str
    raw_audio_duration_sec: Optional[float] = None
    audio_format: Optional[str] = None
    image_bytes_present: bool = False
    client_language_hint: Optional[str] = None
    client_location: Optional[FarmLocation] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SemanticFrame(BaseModel):
    """
    Canonical semantic representation produced by ASR/NLU nodes.
    Shared contract ingested by the Task Planner, Confidence Gate, and Tool Router.
    """
    model_config = ConfigDict(extra="forbid")

    request_id: str
    session_id: str
    raw_text: str
    normalized_text: str
    language: str = Field(default="hi", description="BCP-47 language code (e.g. hi, en, gu, mr)")
    dialect: Optional[str] = Field(None, description="Regional dialect (e.g. mewari, marwari)")
    intent: CanonicalIntent
    sub_intent: Optional[str] = None
    required_capabilities: List[CapabilityType] = Field(
        default_factory=list,
        description="Specialist tool capabilities needed to fulfill query"
    )
    entities: EntitySet = Field(default_factory=EntitySet)
    required_input: RequiredInput = Field(default=RequiredInput.NONE)
    confidence: ConfidenceSet
    user_context: Optional[UserContext] = None
    conversation_context: Optional[ConversationContext] = None
    requested_output_language: str = Field(default="hi")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# 5. ACTION & EXECUTION SCHEMAS
# =============================================================================

class NavigationAction(BaseModel):
    """Typed navigation instruction strictly validated against Android route whitelist."""
    model_config = ConfigDict(extra="forbid")

    action: ActionIntent = Field(default=ActionIntent.NAVIGATE)
    destination: NavigationDestination
    android_route: str = Field(default="")
    required_input: RequiredInput = Field(default=RequiredInput.NONE)
    message: str
    params: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.android_route:
            self.android_route = ANDROID_ROUTE_MAP.get(self.destination, "dashboard")


class CallingAction(BaseModel):
    """Telephony calling escalation instruction for urgent warnings or farmer outreach."""
    model_config = ConfigDict(extra="forbid")

    action: ActionIntent = Field(default=ActionIntent.CALL)
    target_phone: str
    caller_name: Optional[str] = None
    reason: str
    urgency: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    script_context: Dict[str, Any] = Field(default_factory=dict)


class ToolInvocation(BaseModel):
    """Specification of a single tool execution step formulated by the Task Planner."""
    model_config = ConfigDict(extra="forbid")

    invocation_id: str
    tool_name: str
    capability: CapabilityType
    inputs: Dict[str, Any] = Field(default_factory=dict)
    order_index: int = 0
    is_parallel: bool = False
    depends_on: List[str] = Field(default_factory=list, description="IDs of prerequisite invocations")
    timeout_seconds: float = 10.0


class PlannedTask(BaseModel):
    """Complete execution DAG formulated by the LangGraph Task Planner."""
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    request_id: str
    intent: CanonicalIntent
    tool_invocations: List[ToolInvocation] = Field(default_factory=list)
    requires_clarification: bool = False
    clarification_prompt: Optional[str] = None
    requires_navigation: bool = False
    navigation_target: Optional[NavigationAction] = None
    requires_calling: bool = False
    calling_target: Optional[CallingAction] = None
    explanation: str = Field(default="")


class ToolResultReference(BaseModel):
    """Standardized output wrapper for any specialist tool or model result."""
    model_config = ConfigDict(extra="allow")

    invocation_id: str
    tool_name: str
    status: str = Field(default="SUCCESS", description="SUCCESS, UNAVAILABLE, INSUFFICIENT_DATA, ERROR")
    source: str
    model_version: Optional[str] = None
    confidence: Optional[float] = None
    execution_time_ms: float = 0.0
    data_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)


class ResponseEnvelope(BaseModel):
    """Final unified response envelope returned to Android client, voice synthesizer, and UI."""
    model_config = ConfigDict(extra="allow")

    request_id: str
    session_id: str
    language: str
    action: ActionIntent
    response_text: str
    speech_text: Optional[str] = None
    navigation: Optional[NavigationAction] = None
    calling: Optional[CallingAction] = None
    data: Optional[Dict[str, Any]] = None
    confidence: ConfidenceSet
    provenance: List[Dict[str, Any]] = Field(default_factory=list)
    follow_up_suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
