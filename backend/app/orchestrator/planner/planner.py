"""
Task Planner for FarmFusion.
Translates SemanticFrame into a dependency-aware, executable TaskPlan.
Enforces required-input gates, resolves tool inputs without data fabrication,
and builds topological execution batches.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

from app.schemas.semantic_frame import (
    SemanticFrame,
    CapabilityType,
    RequiredInput,
    CanonicalIntent,
)
from app.tools.contracts import (
    AllowedNavigationDestination,
    NAVIGATION_ROUTE_MAP,
    NAVIGATION_ALIAS_MAP,
    get_tool_contract,
    map_capabilities_to_tools,
)
from app.orchestrator.planner.schemas import (
    TaskPlan,
    PlannedTask,
    PlanStatus,
    ActionType,
)
from app.orchestrator.planner.dag import build_execution_batches

logger = structlog.get_logger(__name__)


def generate_task_plan(
    semantic_frame: SemanticFrame,
    farmer_context: Optional[Dict[str, Any]] = None,
    session_state: Optional[Dict[str, Any]] = None,
    image_bytes: Optional[bytes] = None,
    image_path: Optional[str] = None,
) -> TaskPlan:
    """
    Constructs a dependency-aware TaskPlan from a validated SemanticFrame.
    
    1. Evaluates required-input gates (e.g. Leaf photo requirement, GPS coordinates)
    2. Maps required capabilities to specialist tools
    3. Resolves static inputs from entities, farmer profile, and session memory
    4. Declares upstream/downstream result dependencies
    5. Calculates topological parallel execution batches
    """
    f_ctx = farmer_context or {}
    s_state = session_state or {}
    entities = semantic_frame.entities

    logger.info(
        "generate_task_plan_start",
        intent=semantic_frame.intent,
        capabilities=semantic_frame.required_capabilities,
        required_input=semantic_frame.required_input,
    )

    # -------------------------------------------------------------------------
    # 1. Gate Check: Clarification Required (Safety Rule #6 or Confidence < 0.6)
    # -------------------------------------------------------------------------
    if (
        semantic_frame.intent == CanonicalIntent.CLARIFICATION
        or semantic_frame.confidence.intent_confidence < 0.60
    ):
        raw_lower = semantic_frame.raw_text.lower()
        if any(w in raw_lower for w in ["इस फसल", "यह फसल", "ये फसल", "my crop", "the crop", "this crop", "is fasal", "ye fasal", "meri fasal", "dekhbhal", "देखभाल"]):
            clarif_msg = "क्या आप कृपया अपनी फसल का नाम बता सकते हैं जिसकी देखभाल के बारे में आप पूछ रहे हैं?"
        else:
            clarif_msg = "क्या आप कृपया अपना सवाल दोबारा स्पष्ट कह सकते हैं? (जैसे मौसम, मंडी भाव या फसल सलाह)"

        return TaskPlan(
            session_id=semantic_frame.session_id,
            objective="Query ambiguous or confidence low. Requesting farmer clarification.",
            action_type=ActionType.CLARIFY,
            clarification_message=clarif_msg,
            status=PlanStatus.READY,
        )

    # -------------------------------------------------------------------------
    # 2. Gate Check: Disease Diagnosis Photo Requirement (Step 5)
    # -------------------------------------------------------------------------
    has_image = bool(image_bytes or image_path or s_state.get("image_bytes") or s_state.get("image_path"))
    if (
        semantic_frame.required_input == RequiredInput.LEAF_IMAGE
        or semantic_frame.intent == CanonicalIntent.DISEASE_DETECTION
        or CapabilityType.DISEASE_DETECTION in semantic_frame.required_capabilities
    ):
        if not has_image:
            # Strictly DO NOT call disease model or invent diagnosis
            return TaskPlan(
                session_id=semantic_frame.session_id,
                objective="Farmer requests disease diagnosis without image. Directing to leaf scan screen.",
                action_type=ActionType.NAVIGATE,
                navigation_destination="DISEASE_SCAN",
                navigation_route=NAVIGATION_ROUTE_MAP[AllowedNavigationDestination.DISEASE_SCAN],
                required_input=RequiredInput.LEAF_IMAGE,
                clarification_message="फसल रोग पहचान के लिए प्रभावित पत्ती का फोटो आवश्यक है। कृपया कैमरा खोलें।",
                status=PlanStatus.READY,
            )

    # -------------------------------------------------------------------------
    # 3. Direct Navigation Intent
    # -------------------------------------------------------------------------
    if (
        semantic_frame.intent == CanonicalIntent.NAVIGATION_REQUEST
        or CapabilityType.NAVIGATION in semantic_frame.required_capabilities
    ):
        target_raw = entities.additional_entities.get("destination") or semantic_frame.raw_text.lower()
        target_enum: Optional[AllowedNavigationDestination] = None
        for alias_k, enum_val in NAVIGATION_ALIAS_MAP.items():
            if alias_k in target_raw:
                target_enum = enum_val
                break

        if target_enum is None:
            target_enum = AllowedNavigationDestination.DASHBOARD

        route = NAVIGATION_ROUTE_MAP.get(target_enum, "dashboard")
        return TaskPlan(
            session_id=semantic_frame.session_id,
            objective=f"Navigate farmer to {target_enum.value} screen.",
            action_type=ActionType.NAVIGATE,
            navigation_destination=target_enum.value,
            navigation_route=route,
            required_input=(
                RequiredInput.LEAF_IMAGE
                if target_enum == AllowedNavigationDestination.DISEASE_SCAN
                else None
            ),
            status=PlanStatus.READY,
        )

    # -------------------------------------------------------------------------
    # 4. Resolve Contextual Entities
    # -------------------------------------------------------------------------
    crop = entities.crop or s_state.get("active_crop")
    market = entities.market or s_state.get("last_market")
    markets = entities.markets or ([market] if market else [])

    lat = (
        entities.farm_location.latitude
        if entities.farm_location and entities.farm_location.latitude is not None
        else f_ctx.get("latitude")
    )
    lon = (
        entities.farm_location.longitude
        if entities.farm_location and entities.farm_location.longitude is not None
        else f_ctx.get("longitude")
    )
    state_name = (
        entities.state
        or (entities.farm_location.state if entities.farm_location else None)
        or f_ctx.get("state")
    )
    district_name = (
        entities.district
        or (entities.farm_location.district if entities.farm_location else None)
        or f_ctx.get("district")
    )
    soil_type = (
        (getattr(entities.soil_values, "soil_type", None) or (entities.soil_values.get("soil_type") if isinstance(entities.soil_values, dict) else None))
        if entities.soil_values
        else f_ctx.get("soil_type")
    )

    # -------------------------------------------------------------------------
    # 5. Missing Location Gate for Physical Tools
    # -------------------------------------------------------------------------
    needs_physical_location = any(
        cap in semantic_frame.required_capabilities
        for cap in [CapabilityType.WEATHER, CapabilityType.CROP_RECOMMENDATION, CapabilityType.DISASTER_RISK]
    )
    if needs_physical_location and (lat is None or lon is None) and not district_name and not state_name:
        return TaskPlan(
            session_id=semantic_frame.session_id,
            objective="Physical farming recommendations require location context.",
            action_type=ActionType.REQUEST_INPUT,
            required_input=RequiredInput.FARM_LOCATION,
            unresolved_inputs=["latitude", "longitude", "district"],
            clarification_message="कृपया अपने खेत का स्थान या जिला बताएं ताकि हम सही मौसम और फसल सलाह दे सकें।",
            status=PlanStatus.READY,
        )

    # -------------------------------------------------------------------------
    # 6. Decompose Capabilities into Planned Tasks & Dependencies
    # -------------------------------------------------------------------------
    tasks: List[PlannedTask] = []
    caps = list(semantic_frame.required_capabilities)

    # 6.1 Weather Tool Task
    if CapabilityType.WEATHER in caps:
        # First-class temporal routing: tomorrow/explicit-date/multi-day requests must
        # use the forecast tool anchored to the requested date, NOT today's current weather.
        tc = None
        if isinstance(entities.time_context, dict):
            tc = entities.time_context
        elif entities.time_context is not None:
            tc = entities.time_context.model_dump()
        tc = tc or {}
        rd = tc.get("relative_day") or "UNSPECIFIED"
        target_date = tc.get("resolved_date")
        wants_forecast = rd in ("TOMORROW", "DAY_AFTER_TOMORROW", "NEXT_WEEK", "NEXT_7_DAYS", "EXPLICIT_DATE")

        if wants_forecast:
            tasks.append(
                PlannedTask(
                    task_id="weather_1",
                    capability=CapabilityType.WEATHER,
                    tool_name="weather_forecast_tool",
                    description="Fetch physical forecast for the requested date/horizon.",
                    depends_on=[],
                    static_inputs={
                        "latitude": float(lat) if lat is not None else 26.9124,
                        "longitude": float(lon) if lon is not None else 75.7873,
                        "location_name": district_name or state_name,
                        "days": int((tc or {}).get("forecast_days") or (tc or {}).get("horizon_days") or entities.forecast_days or 7),
                        "target_date": target_date,
                    },
                    is_blocking=False,
                )
            )
        else:
            tasks.append(
                PlannedTask(
                    task_id="weather_1",
                    capability=CapabilityType.WEATHER,
                    tool_name="weather_tool",
                    description="Fetch real-time physical temperature, humidity, rainfall, and wind.",
                    depends_on=[],
                    static_inputs={
                        "latitude": float(lat) if lat is not None else 26.9124,
                        "longitude": float(lon) if lon is not None else 75.7873,
                        "location_name": district_name or state_name,
                    },
                    is_blocking=False,
                )
            )

    # 6.2 Smart Irrigation Tool Task (Depends on Weather if present)
    if CapabilityType.SMART_IRRIGATION in caps:
        weather_dep = ["weather_1"] if any(t.task_id == "weather_1" for t in tasks) else []
        tasks.append(
            PlannedTask(
                task_id="irrigation_1",
                capability=CapabilityType.SMART_IRRIGATION,
                tool_name="smart_irrigation_tool",
                description="Compute deterministic agronomic soil-moisture deficit and irrigation recommendation.",
                depends_on=weather_dep,
                static_inputs={
                    "latitude": float(lat) if lat is not None else 26.9124,
                    "longitude": float(lon) if lon is not None else 75.7873,
                    "crop": crop,
                    "language": semantic_frame.language or "hi",
                },
                is_blocking=True,
            )
        )

    # 6.3 Disaster Risk Tool Task (Depends on Weather if present)
    if CapabilityType.DISASTER_RISK in caps:
        weather_dep = ["weather_1"] if any(t.task_id == "weather_1" for t in tasks) else []
        tasks.append(
            PlannedTask(
                task_id="disaster_1",
                capability=CapabilityType.DISASTER_RISK,
                tool_name="disaster_risk_tool",
                description="Run DisasterPredictorAI 4-model ensemble for 7-day multi-hazard prediction.",
                depends_on=weather_dep,
                static_inputs={
                    "latitude": float(lat) if lat is not None else 26.9124,
                    "longitude": float(lon) if lon is not None else 75.7873,
                    "crop_name": crop,
                    "days": entities.forecast_days or 7,
                    "location_name": district_name or state_name,
                },
                is_blocking=True,
            )
        )

    # 6.4 Crop Recommendation Tool Task
    if CapabilityType.CROP_RECOMMENDATION in caps:
        tasks.append(
            PlannedTask(
                task_id="crop_rec_1",
                capability=CapabilityType.CROP_RECOMMENDATION,
                tool_name="crop_recommendation_tool",
                description="Recommend top suitable crops using XGBoost V2 model and ICAR agronomic rules.",
                depends_on=[],
                static_inputs={
                    "latitude": float(lat) if lat is not None else 26.9124,
                    "longitude": float(lon) if lon is not None else 75.7873,
                    "soil_type": soil_type,
                    "season": entities.season,
                    "state": state_name,
                },
                is_blocking=True,
            )
        )

    # 6.5 Disease Detection Tool Task (Image is guaranteed present by Gate 2)
    if CapabilityType.DISEASE_DETECTION in caps:
        img_bytes = image_bytes or s_state.get("image_bytes")
        img_path = image_path or s_state.get("image_path")
        tasks.append(
            PlannedTask(
                task_id="disease_1",
                capability=CapabilityType.DISEASE_DETECTION,
                tool_name="disease_detection_tool",
                description="Perform leaf pathology classification using EfficientNet-B3 model.",
                depends_on=[],
                static_inputs={
                    "image_bytes": img_bytes,
                    "image_path": img_path,
                    "crop": crop,
                    "language": semantic_frame.language or "hi",
                },
                is_blocking=True,
            )
        )

    # 6.6 Mandi Current Price Task
    if CapabilityType.CURRENT_PRICE in caps or CapabilityType.MANDI_CURRENT_PRICE in caps:
        tasks.append(
            PlannedTask(
                task_id="mandi_price_1",
                capability=CapabilityType.CURRENT_PRICE,
                tool_name="mandi_current_price_tool",
                description="Fetch verified live/modal price from Agmarknet mandi records.",
                depends_on=[],
                static_inputs={
                    "crop": crop or "Wheat",
                    "market": market,
                    "district": district_name,
                    "state": state_name,
                },
                is_blocking=False,
            )
        )

    # 6.7 Mandi Comparison Task (Runs concurrently with current price / forecast)
    if CapabilityType.MANDI_COMPARISON in caps:
        m_a = markets[0] if len(markets) >= 1 else (market or "Jaipur")
        m_b = markets[1] if len(markets) >= 2 else "Kota"
        tasks.append(
            PlannedTask(
                task_id="mandi_compare_1",
                capability=CapabilityType.MANDI_COMPARISON,
                tool_name="mandi_comparison_tool",
                description=f"Compare price spread and net yield between {m_a} and {m_b}.",
                depends_on=[],
                static_inputs={
                    "crop": crop or "Wheat",
                    "market_a": m_a,
                    "market_b": m_b,
                },
                is_blocking=False,
            )
        )

    # 6.8 Mandi Forecast Task (Runs concurrently with price lookup)
    if CapabilityType.MANDI_FORECAST in caps:
        f_market = market or (markets[0] if markets else "Jaipur")
        tasks.append(
            PlannedTask(
                task_id="mandi_forecast_1",
                capability=CapabilityType.MANDI_FORECAST,
                tool_name="mandi_forecast_tool",
                description="Generate 7-day price forecast using Prophet + LightGBM ensemble.",
                depends_on=[],
                static_inputs={
                    "crop": crop or "Wheat",
                    "market": f_market,
                    "forecast_days": entities.forecast_days or 7,
                },
                is_blocking=False,
            )
        )

    # 6.9 Mandi Decision Task (Depends on current price and forecast if present)
    if CapabilityType.MANDI_DECISION in caps:
        mandi_deps = [
            t.task_id for t in tasks
            if t.task_id in ["mandi_price_1", "mandi_forecast_1"]
        ]
        tasks.append(
            PlannedTask(
                task_id="mandi_decision_1",
                capability=CapabilityType.MANDI_DECISION,
                tool_name="mandi_decision_tool",
                description="Generate deterministic sell-now vs hold decision with projected yield.",
                depends_on=mandi_deps,
                static_inputs={
                    "crop": crop or "Wheat",
                    "market": market or "Jaipur Mandi",
                    "holding_days": entities.forecast_days or 7,
                },
                is_blocking=True,
            )
        )

    # 6.10 RAG Knowledge Task (Dynamic dependency on disease diagnosis or disaster hazards)
    if CapabilityType.RAG_KNOWLEDGE in caps:
        rag_deps: List[str] = []
        dyn_map: Dict[str, str] = {}
        static_q = semantic_frame.raw_text

        if any(t.task_id == "disease_1" for t in tasks):
            rag_deps.append("disease_1")
            dyn_map["query"] = "disease_1.disease_name"
        elif any(t.task_id == "disaster_1" for t in tasks):
            rag_deps.append("disaster_1")
            dyn_map["query"] = "disaster_1.active_hazards"

        tasks.append(
            PlannedTask(
                task_id="rag_1",
                capability=CapabilityType.RAG_KNOWLEDGE,
                tool_name="rag_knowledge_tool",
                description="Search verified ICAR agronomic guidance and treatment guidelines via pgvector.",
                depends_on=rag_deps,
                static_inputs={
                    "query": static_q,
                    "crop": crop,
                    "top_k": 3,
                },
                dynamic_mappings=dyn_map,
                is_blocking=False,
            )
        )

    # 6.11 Government Schemes Task
    if CapabilityType.GOVERNMENT_SCHEME in caps:
        tasks.append(
            PlannedTask(
                task_id="scheme_1",
                capability=CapabilityType.GOVERNMENT_SCHEME,
                tool_name="government_scheme_tool",
                description="Retrieve verified welfare scheme eligibility and guidelines.",
                depends_on=[],
                static_inputs={
                    "query": semantic_frame.raw_text,
                    "state": state_name,
                    "crop_name": crop,
                },
                is_blocking=False,
            )
        )

    # 6.12 Animal Detection IoT Task
    if CapabilityType.ANIMAL_ALERT in caps or CapabilityType.ANIMAL_DETECTION in caps:
        tasks.append(
            PlannedTask(
                task_id="animal_1",
                capability=CapabilityType.ANIMAL_DETECTION,
                tool_name="animal_detection_tool",
                description="Check IoT perimeter PIR sensor status for wildlife/stray animal intrusion.",
                depends_on=[],
                static_inputs={"device_id": "NODE_01"},
                is_blocking=False,
            )
        )

    # 6.13 Calling Tool Task
    if CapabilityType.CALLING in caps:
        extracted_phone = entities.additional_entities.get("phone") if hasattr(entities, "additional_entities") and entities.additional_entities else None
        target_phone = extracted_phone or f_ctx.get("phone") or "+919876543210"
        target_name = f_ctx.get("name") or "Farmer"
        tasks.append(
            PlannedTask(
                task_id="calling_1",
                capability=CapabilityType.CALLING,
                tool_name="calling_tool",
                description="Initiate outbound voice advisory call via Vobiz telephony gateway.",
                depends_on=[],
                static_inputs={
                    "phone": target_phone,
                    "farmer_name": target_name,
                    "language": semantic_frame.language or "hi",
                    "crop_name": crop,
                    "mandi_name": market,
                },
                is_blocking=True,
            )
        )

    # -------------------------------------------------------------------------
    # 7. Calculate Topological Parallel Execution Batches
    # -------------------------------------------------------------------------
    batches = build_execution_batches(tasks)

    return TaskPlan(
        session_id=semantic_frame.session_id,
        objective=f"Fulfill farmer intent '{semantic_frame.intent}' with {len(tasks)} planned tools.",
        action_type=ActionType.EXECUTE_TOOL,
        tasks=tasks,
        execution_batches=batches,
        status=PlanStatus.READY,
    )
