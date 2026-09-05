"""
Validation / Safety Node for LangGraph Orchestrator.
Performs deterministic pre-synthesis verification:
1. Validates specialist tool execution statuses and required payload fields.
2. Extracts an immutable machine-readable fact set from tool results.
3. Enforces physical and agronomic range checks (temperatures, prices, percentages).
4. Verifies cross-tool consistency (e.g. Weather rain vs Smart Irrigation advice).
5. Confirms RAG evidence quality and aligns confidence tiering.
"""
from typing import Any, Dict, List, Optional, Tuple
import structlog

from app.orchestrator.state import OrchestratorState
from app.schemas.validation import (
    CheckSeverity,
    CrossToolConsistencyResult,
    ValidationCheck,
    ValidationResult,
    VerifiedFact,
    VerifiedFactSet,
)
from app.schemas.rag import EvidenceLevel

logger = structlog.get_logger(__name__)


def extract_verified_facts_from_state(state: OrchestratorState) -> VerifiedFactSet:
    """
    Extracts all verified numerical and categorical facts from specialist tool executions.
    These facts form the immutable ground-truth set that LLM synthesis cannot alter.
    """
    facts: List[VerifiedFact] = []
    tool_results = state.get("tool_results", {}) or {}
    legacy_output = state.get("tool_output", {}) or {}

    # 1. Mandi Pricing & Forecasting Facts
    for k, v in tool_results.items():
        if "price" in k or "mandi" in k:
            comm = v.get("commodity") or (v.get("observed", {}) or {}).get("commodity")
            mkt = v.get("market") or (v.get("observed", {}) or {}).get("market")
            if comm:
                facts.append(VerifiedFact(
                    key="mandi_commodity",
                    value=str(comm),
                    unit=None,
                    source_tool=k,
                    is_numeric=False,
                ))
            if mkt:
                facts.append(VerifiedFact(
                    key="mandi_market",
                    value=str(mkt),
                    unit=None,
                    source_tool=k,
                    is_numeric=False,
                ))
            raw_p = v.get("current_price")
            if isinstance(raw_p, dict):
                curr_price = raw_p.get("modal_price") or raw_p.get("price")
            else:
                curr_price = raw_p or v.get("modal_price") or v.get("price")
            if curr_price is not None:
                try:
                    facts.append(VerifiedFact(
                        key="mandi_current_price",
                        value=round(float(curr_price), 2),
                        unit="INR/quintal",
                        source_tool=k,
                        is_numeric=True,
                    ))
                except (ValueError, TypeError):
                    pass
            if "daily_forecasts" in v and isinstance(v["daily_forecasts"], list) and v["daily_forecasts"]:
                last_f = v["daily_forecasts"][-1]
                pred_p = last_f.get("predicted_price")
                if pred_p is not None:
                    facts.append(VerifiedFact(
                        key="mandi_forecast_price",
                        value=round(float(pred_p), 2),
                        unit="INR/quintal",
                        source_tool=k,
                        is_numeric=True,
                    ))
            if "deterministic_action" in v and isinstance(v["deterministic_action"], dict):
                act = v["deterministic_action"].get("action")
                pct = v["deterministic_action"].get("expected_pct_change")
                if act:
                    facts.append(VerifiedFact(
                        key="mandi_decision_action",
                        value=str(act),
                        unit=None,
                        source_tool=k,
                        is_numeric=False,
                    ))
                if pct is not None:
                    facts.append(VerifiedFact(
                        key="mandi_expected_change_pct",
                        value=round(float(pct), 2),
                        unit="percent",
                        source_tool=k,
                        is_numeric=True,
                    ))

    # 2. Weather & Forecast Facts
    weather_task = next((v for k, v in tool_results.items() if "weather" in k), legacy_output)
    if isinstance(weather_task, dict):
        temp = weather_task.get("temperature_c") or weather_task.get("temperature")
        hum = weather_task.get("humidity_percent") or weather_task.get("humidity")
        rain = weather_task.get("annual_rainfall_mm") or weather_task.get("precipitation_mm")
        wind = weather_task.get("wind_speed_kmh") or weather_task.get("wind_speed")
        feels = weather_task.get("feels_like_c")

        # Check forecast rows (e.g. for tomorrow / 7-day)
        forecast_rows = weather_task.get("forecast")
        if isinstance(forecast_rows, list) and forecast_rows:
            f_row = forecast_rows[0]
            if temp is None:
                temp = f_row.get("temperature_avg_c") or f_row.get("temperature_c") or f_row.get("temperature_max_c")
            if hum is None:
                hum = f_row.get("humidity_percent")
            f_precip = f_row.get("precipitation_mm")
            f_prob = f_row.get("precipitation_probability_percent")
            f_wind = f_row.get("wind_speed_max_kmh") or f_row.get("wind_speed_kmh")
            if f_precip is not None:
                facts.append(VerifiedFact(
                    key="rainfall_mm",
                    value=round(float(f_precip), 1),
                    unit="mm",
                    source_tool="weather_tool",
                    is_numeric=True,
                ))
            if f_prob is not None:
                facts.append(VerifiedFact(
                    key="rainfall_probability_percent",
                    value=round(float(f_prob), 1),
                    unit="percent",
                    source_tool="weather_tool",
                    is_numeric=True,
                ))
            if f_wind is not None and wind is None:
                wind = f_wind

        if temp is not None:
            facts.append(VerifiedFact(
                key="temperature_c",
                value=round(float(temp), 1),
                unit="C",
                source_tool="weather_tool",
                is_numeric=True,
            ))
        if hum is not None:
            facts.append(VerifiedFact(
                key="humidity_percent",
                value=round(float(hum), 1),
                unit="percent",
                source_tool="weather_tool",
                is_numeric=True,
            ))
        if rain is not None and not any(f.key == "rainfall_mm" for f in facts):
            facts.append(VerifiedFact(
                key="rainfall_mm",
                value=round(float(rain), 1),
                unit="mm",
                source_tool="weather_tool",
                is_numeric=True,
            ))
        if wind is not None:
            facts.append(VerifiedFact(
                key="wind_speed_kmh",
                value=round(float(wind), 1),
                unit="km/h",
                source_tool="weather_tool",
                is_numeric=True,
            ))
        if feels is not None:
            facts.append(VerifiedFact(
                key="feels_like_c",
                value=round(float(feels), 1),
                unit="C",
                source_tool="weather_tool",
                is_numeric=True,
            ))

    # 3. Smart Irrigation Facts
    irrigation_task = next((v for k, v in tool_results.items() if "irrigation" in k), {})
    si_source = irrigation_task if (isinstance(irrigation_task, dict) and irrigation_task) else (
        weather_task.get("smart_irrigation") if isinstance(weather_task, dict) else {}
    )
    if isinstance(si_source, dict) and si_source:
        si_status = si_source.get("status") or si_source.get("action") or si_source.get("recommendation")
        if si_status:
            facts.append(VerifiedFact(
                key="irrigation_status",
                value=str(si_status),
                unit=None,
                source_tool="smart_irrigation_tool",
                is_numeric=False,
            ))
        sm = (
            si_source.get("root_zone_moisture_percent")
            or si_source.get("soil_moisture_percent")
            or si_source.get("soil_moisture_pct")
            or si_source.get("soil_moisture")
        )
        if sm is not None:
            facts.append(VerifiedFact(
                key="soil_moisture_percent",
                value=round(float(sm), 1),
                unit="percent",
                source_tool="smart_irrigation_tool",
                is_numeric=True,
            ))
        r24 = (
            si_source.get("next_24h_rain_sum_mm")
            or si_source.get("next_24h_rainfall_mm")
            or si_source.get("expected_rain_mm")
            or si_source.get("rainfall_mm")
        )
        if r24 is not None:
            facts.append(VerifiedFact(
                key="irrigation_24h_rain_mm",
                value=round(float(r24), 1),
                unit="mm",
                source_tool="smart_irrigation_tool",
                is_numeric=True,
            ))
        score = si_source.get("irrigation_need_score")
        if score is not None:
            facts.append(VerifiedFact(
                key="irrigation_need_score",
                value=round(float(score), 1),
                unit=None,
                source_tool="smart_irrigation_tool",
                is_numeric=True,
            ))

    # 4. Disaster Risk Facts
    disaster_task = next((v for k, v in tool_results.items() if "disaster" in k), {})
    if isinstance(disaster_task, dict) and disaster_task:
        risk_lvl = disaster_task.get("peak_risk_level") or disaster_task.get("current_risk_level") or disaster_task.get("risk_level")
        risk_score = disaster_task.get("peak_risk_score") or disaster_task.get("current_risk_score") or disaster_task.get("risk_score")
        hazard = disaster_task.get("peak_disaster_type") or disaster_task.get("current_disaster_type") or disaster_task.get("hazard_type")
        if risk_lvl:
            facts.append(VerifiedFact(
                key="disaster_risk_level",
                value=str(risk_lvl),
                unit=None,
                source_tool="disaster_risk_tool",
                is_numeric=False,
            ))
        if risk_score is not None:
            facts.append(VerifiedFact(
                key="disaster_risk_score",
                value=round(float(risk_score), 1),
                unit=None,
                source_tool="disaster_risk_tool",
                is_numeric=True,
            ))
        if hazard:
            facts.append(VerifiedFact(
                key="disaster_hazard_type",
                value=str(hazard),
                unit=None,
                source_tool="disaster_risk_tool",
                is_numeric=False,
            ))

    # 5. Crop Recommendation Facts
    crop_task = next((v for k, v in tool_results.items() if "crop" in k), {})
    if isinstance(crop_task, dict) and crop_task:
        top_crop = crop_task.get("top_crop") or crop_task.get("crop_name")
        conf = crop_task.get("confidence") or crop_task.get("probability")
        if top_crop:
            facts.append(VerifiedFact(
                key="recommended_crop",
                value=str(top_crop),
                unit=None,
                source_tool="crop_recommendation_tool",
                is_numeric=False,
            ))
        if conf is not None:
            facts.append(VerifiedFact(
                key="crop_confidence",
                value=round(float(conf), 2),
                unit="probability",
                source_tool="crop_recommendation_tool",
                is_numeric=True,
            ))

    # 6. Disease Detection Facts
    disease_task = next((v for k, v in tool_results.items() if "disease" in k), legacy_output)
    if isinstance(disease_task, dict) and disease_task:
        d_name = disease_task.get("disease_name") or disease_task.get("predicted_disease")
        conf = disease_task.get("confidence") or disease_task.get("model_confidence")
        if d_name:
            facts.append(VerifiedFact(
                key="detected_disease",
                value=str(d_name),
                unit=None,
                source_tool="disease_detection_tool",
                is_numeric=False,
            ))
        if conf is not None:
            facts.append(VerifiedFact(
                key="disease_confidence",
                value=round(float(conf), 3),
                unit="probability",
                source_tool="disease_detection_tool",
                is_numeric=True,
            ))

    # 7. Time Horizon Grounding Fact (Critical Fix 5)
    sf = state.get("semantic_frame") or {}
    sf_entities = sf.get("entities") or {} if isinstance(sf, dict) else {}
    slots = state.get("filled_slots") or {}
    forecast_days = sf_entities.get("forecast_days") or slots.get("forecast_days")
    user_query = state.get("user_input", "").lower()

    if forecast_days == 7 or any(w in user_query for w in ["7 दिन", "7 days", "7-day", "अगले हफ्ते", "हफ्ते", "next week", "seven days"]):
        horizon_val = "7_DAYS"
    elif forecast_days == 2 or any(w in user_query for w in ["48 घंटे", "48 hours", "परसों"]):
        horizon_val = "48_HOURS"
    elif forecast_days == 1 or any(w in user_query for w in ["24 घंटे", "24 hours", "कल", "tomorrow"]):
        horizon_val = "24_HOURS"
    else:
        horizon_val = "CURRENT"

    facts.append(VerifiedFact(
        key="forecast_horizon",
        value=horizon_val,
        unit=None,
        source_tool="semantic_frame",
        is_numeric=False,
    ))

    return VerifiedFactSet(facts=facts)


def check_disease_contradictions(state: OrchestratorState, facts: VerifiedFactSet) -> Optional[ValidationCheck]:
    """
    Critical Fix 2: Detects contradictory disease results:
    - Model predicts a pathogen (e.g. Tomato Mosaic Virus) but downstream/tool claims 'No Plant Detected' or 'Healthy'.
    - Or image gatekeeper claims non-plant while disease classifier outputs positive disease.
    - Or disease confidence is unclear/low (< 0.30) while downstream RAG claims healthy plant.
    """
    tool_results = state.get("tool_results", {}) or {}
    legacy_output = state.get("tool_output", {}) or {}
    disease_task = next((v for k, v in tool_results.items() if "disease" in k), legacy_output)

    if not isinstance(disease_task, dict) or not disease_task:
        return None

    d_name = str(disease_task.get("disease_name") or disease_task.get("predicted_disease") or "").strip()
    crop = str(disease_task.get("crop_name") or disease_task.get("crop") or "").strip()
    conf = float(disease_task.get("confidence") or disease_task.get("model_confidence") or 0.0)

    is_pathogen = bool(d_name) and d_name.lower() not in ["healthy", "no plant detected", "unknown disease", "पौध रोग", "none"]

    rag_data = state.get("rag_grounding") or {}
    docs = rag_data.get("documents", [])
    rag_titles = [d.get("title", "").lower() for d in docs] if isinstance(docs, list) else []

    # 1. Contradiction: Pathogen predicted but image was non-plant
    if is_pathogen and (disease_task.get("is_plant") is False or "no plant detected" in d_name.lower() or crop.lower() in ["none", "no plant"]):
        return ValidationCheck(
            check_name="contradictory_disease_diagnosis",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            details=f"Contradiction: Plant disease '{d_name}' reported on non-plant image ('{crop}').",
            target_tool="disease_detection_tool",
        )

    # 2. Contradiction: Pathogen predicted with unclear confidence (< 0.30) while healthy guide retrieved
    if is_pathogen and conf < 0.30 and any("healthy" in t for t in rag_titles):
        return ValidationCheck(
            check_name="contradictory_disease_diagnosis",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            details=f"Contradiction: Pathogen '{d_name}' predicted with unclear confidence ({conf:.2f}), conflicting with healthy plant reference.",
            target_tool="disease_detection_tool",
        )

    # 3. Contradiction: 'No Plant Detected' cannot carry positive pathogen confidence
    if "no plant detected" in d_name.lower() and conf > 0.5:
        return ValidationCheck(
            check_name="contradictory_disease_diagnosis",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            details="Contradiction: 'No Plant Detected' cannot carry positive pathogen confidence.",
            target_tool="disease_detection_tool",
        )

    return None


def compute_deterministic_confidence(
    state: OrchestratorState,
    facts: VerifiedFactSet,
    checks: List[ValidationCheck],
    conf_tier: str,
) -> float:
    """
    Critical Fix 4: Deterministic confidence aggregation policy.
    Aggregates intent confidence, specialist tool/model confidence,
    RAG evidence quality, validation check severity, and data freshness.
    Guarantees model confidence (e.g. 0.14) is never inflated.
    """
    intent_conf = float(state.get("intent_confidence") or 0.90)
    model_conf = 0.92

    disease_conf = facts.get_fact("disease_confidence")
    crop_conf = facts.get_fact("crop_confidence")

    if disease_conf is not None and disease_conf.is_numeric:
        model_conf = float(disease_conf.value)
    elif crop_conf is not None and crop_conf.is_numeric:
        model_conf = float(crop_conf.value)

    base_conf = min(intent_conf, model_conf)

    # RAG evidence factor
    rag_data = state.get("rag_grounding") or {}
    evidence_lvl = rag_data.get("evidence_level") or rag_data.get("evidence_strength")
    if evidence_lvl == EvidenceLevel.HIGH_EVIDENCE.value:
        rag_factor = 1.0
    elif evidence_lvl == EvidenceLevel.LOW_EVIDENCE.value:
        rag_factor = 0.75
    elif evidence_lvl == EvidenceLevel.NO_EVIDENCE.value and rag_data.get("status") == "NO_RELEVANT_CHUNKS":
        rag_factor = 0.50
    else:
        rag_factor = 1.0

    # Validation severity factor
    has_blocking = any(not c.passed and c.severity == CheckSeverity.BLOCKING for c in checks)
    has_warning = any(not c.passed and c.severity == CheckSeverity.WARNING for c in checks)
    if has_blocking:
        val_factor = 0.15
    elif has_warning:
        val_factor = 0.85
    else:
        val_factor = 1.0

    freshness_factor = 0.90 if state.get("fallback_used") else 1.0

    final_conf = round(base_conf * rag_factor * val_factor * freshness_factor, 2)
    # Strictly align aggregated confidence with confidence_tier bounds (Safety Rule #3)
    if conf_tier == "medium":
        final_conf = min(final_conf, 0.74)
    elif conf_tier == "low":
        final_conf = min(final_conf, 0.44)
    elif conf_tier == "unclear":
        final_conf = min(final_conf, 0.29)
    return max(min(final_conf, 1.0), 0.05)


def validate_response_temporal_alignment(
    text: str,
    relative_day: str,
    horizon_days: int = 1,
) -> Tuple[bool, Optional[str]]:
    """
    Deterministic validation that final text's temporal framing matches requested horizon.
    """
    text_lower = text.lower()
    if relative_day == "TOMORROW":
        # Must contain tomorrow markers
        has_tomorrow = any(w in text_lower for w in ["कल", "tomorrow", "kal", "अगले दिन", "next day"])
        if not has_tomorrow:
            return False, "Response omitted tomorrow framing ('कल' / 'tomorrow') for tomorrow question."
    elif relative_day == "TODAY":
        # Must contain today markers or current framing
        has_today = any(w in text_lower for w in ["आज", "today", "aaj", "वर्तमान", "अभी", "current"])
        if not has_today:
            return False, "Response omitted today framing ('आज' / 'today') for today question."
    elif relative_day in ("NEXT_7_DAYS", "NEXT_WEEK") or horizon_days == 7:
        has_7days = any(w in text_lower for w in ["7 दिन", "7 days", "सात दिन", "हफ्ते", "हफ्ता", "next 7 days", "week"])
        if not has_7days:
            return False, "Response omitted 7-day horizon framing for 7-day question."
    return True, None


def check_temporal_consistency(state: OrchestratorState) -> Optional[ValidationCheck]:
    """
    Deterministic temporal-consistency guard (F7 fix): if the user asked about a
    FUTURE day (tomorrow / explicit date) but the weather tool returned today's
    current observations (no forecast window), flag a BLOCKING inconsistency so the
    synthesizer never answers today's weather for a tomorrow question.
    """
    intent = state.get("intent")
    sf = state.get("semantic_frame") or {}
    sf_entities = sf.get("entities") or {}
    rd = (sf_entities.get("time_context") or {}).get("relative_day") or "UNSPECIFIED"
    tool_results = state.get("tool_results", {}) or {}
    weather_data = next((v for k, v in tool_results.items() if "weather" in k), None)

    if intent not in ("weather", "smart_irrigation", "irrigation_advisory"):
        return None
    if not weather_data:
        return None

    asked_future = rd in ("TOMORROW", "DAY_AFTER_TOMORROW", "NEXT_WEEK", "NEXT_7_DAYS", "EXPLICIT_DATE")
    # Current tool returns observations WITHOUT a forecast window => cannot satisfy future query.
    has_forecast = isinstance(weather_data.get("forecast"), list) and weather_data.get("forecast")
    has_forecast_date = bool(weather_data.get("forecast_date"))

    if asked_future and not has_forecast and not has_forecast_date:
        return ValidationCheck(
            check_name="temporal_consistency",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            details=(
                f"User asked about future day ({rd}) but weather tool returned current-weather "
                "observations. Replanning required to fetch forecast."
            ),
            target_tool="weather_tool",
        )
    # User asked for TODAY but tool returned a forecast anchored elsewhere.
    if rd == "TODAY" and weather_data and "forecast" in weather_data and not weather_data.get("forecast_date", ""):
        # a multi-day forecast used for a today-ask is acceptable; only flag when a
        # specific future forecast_date was selected yet the user asked today.
        if weather_data.get("forecast_date"):
            return ValidationCheck(
                check_name="temporal_consistency",
                passed=False,
                severity=CheckSeverity.WARNING,
                details="User asked about today but tool returned a specific forecast date.",
                target_tool="weather_tool",
            )
    return None


def check_cross_tool_consistency(state: OrchestratorState, facts: VerifiedFactSet) -> CrossToolConsistencyResult:
    """
    Compares outputs from related specialist tools to ensure agronomic consistency.
    Example: Weather precipitation vs Smart Irrigation watering advice.
    """
    tool_results = state.get("tool_results", {}) or {}

    # Check Weather vs Irrigation
    has_weather = any("weather" in k for k in tool_results.keys())
    has_irrigation = any("irrigation" in k for k in tool_results.keys())

    if has_weather and has_irrigation:
        weather_data = next(v for k, v in tool_results.items() if "weather" in k)
        irrigation_data = next(v for k, v in tool_results.items() if "irrigation" in k)

        rain = weather_data.get("annual_rainfall_mm") or weather_data.get("precipitation_mm", 0.0)
        irrigation_action = str(irrigation_data.get("status", "")).upper()
        precip_prob = weather_data.get("precipitation_probability_max", 0.0)

        if precip_prob >= 75.0 and "WATER_NOW" in irrigation_action:
            return CrossToolConsistencyResult(
                consistent=False,
                issue_description=(
                    f"Weather forecast predicts heavy rainfall probability ({precip_prob}%), "
                    f"which conflicts with immediate irrigation recommendation."
                ),
                participating_tools=["weather_tool", "smart_irrigation_tool"],
            )

    return CrossToolConsistencyResult(consistent=True)


async def validation_node(state: OrchestratorState) -> OrchestratorState:
    """
    Executes pre-synthesis validation:
    1. Extracts immutable verified facts (including forecast horizon).
    2. Executes deterministic range and unit checks.
    3. Detects contradictory disease diagnoses and multi-tool conflicts.
    4. Evaluates confidence tiering (Safety Rule #3).
    5. Computes deterministic confidence aggregation (no inflation).
    6. Injects ValidationResult into state.
    """
    checks: List[ValidationCheck] = []
    warnings: List[str] = []
    facts = extract_verified_facts_from_state(state)

    # 1. Check tool execution results
    failed_tasks = state.get("failed_tasks", [])
    task_plan = state.get("task_plan") or {}
    if failed_tasks:
        blocking_failures = [
            t_id for t_id in failed_tasks
            if any(t.get("task_id") == t_id and t.get("is_blocking", True) for t in task_plan.get("tasks", []))
        ]
        if blocking_failures:
            checks.append(ValidationCheck(
                check_name="blocking_tool_failures",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                details=f"Blocking tasks failed: {', '.join(blocking_failures)}",
            ))

    # 2. Numerical physical range checks
    for fact in facts.facts:
        if fact.is_numeric:
            val = float(fact.value)
            if fact.key == "temperature_c" and not (-20.0 <= val <= 65.0):
                checks.append(ValidationCheck(
                    check_name="temperature_range",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    details=f"Temperature value {val}°C is out of realistic physical range (-20 to 65).",
                    target_tool=fact.source_tool,
                ))
            elif fact.key == "humidity_percent" and not (0.0 <= val <= 100.0):
                checks.append(ValidationCheck(
                    check_name="humidity_range",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    details=f"Humidity value {val}% is out of range (0 to 100).",
                    target_tool=fact.source_tool,
                ))
            elif fact.key == "mandi_current_price" and val <= 0:
                checks.append(ValidationCheck(
                    check_name="mandi_price_positive",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    details=f"Mandi price must be positive, got {val}.",
                    target_tool=fact.source_tool,
                ))
            elif fact.key == "disease_confidence" and not (0.0 <= val <= 1.0):
                checks.append(ValidationCheck(
                    check_name="probability_bounds",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    details=f"Disease probability {val} is outside [0, 1].",
                    target_tool=fact.source_tool,
                ))

    # 3. Cross-tool consistency check
    cross_tool_res = check_cross_tool_consistency(state, facts)
    if not cross_tool_res.consistent:
        checks.append(ValidationCheck(
            check_name="cross_tool_consistency",
            passed=False,
            severity=CheckSeverity.WARNING,
            details=cross_tool_res.issue_description or "Cross-tool discrepancy detected.",
        ))
        warnings.append(cross_tool_res.issue_description or "Tool recommendation disparity noted.")

    # 3b. Disease Contradiction check (Critical Fix 2)
    disease_contradiction = check_disease_contradictions(state, facts)
    if disease_contradiction:
        checks.append(disease_contradiction)
        warnings.append(disease_contradiction.details or "Contradictory disease indicators detected.")

    # 3c. Temporal consistency check (F7 fix)
    temporal_check = check_temporal_consistency(state)
    if temporal_check:
        checks.append(temporal_check)
        warnings.append(temporal_check.details or "Temporal mismatch detected.")

    # 4. RAG Evidence check
    rag_data = state.get("rag_grounding") or {}
    evidence_lvl = rag_data.get("evidence_level") or rag_data.get("evidence_strength")
    if evidence_lvl == EvidenceLevel.LOW_EVIDENCE.value:
        warnings.append("Retrieved agronomic evidence is partial; preserve uncertainty in response.")
    elif evidence_lvl == EvidenceLevel.NO_EVIDENCE.value and rag_data.get("status") == "NO_RELEVANT_CHUNKS":
        warnings.append("No verified ICAR documents matched the query; avoid speculative claims.")

    # 5. Evaluate Confidence Tier (Safety Rule #3)
    disease_conf_fact = facts.get_fact("disease_confidence")
    crop_conf_fact = facts.get_fact("crop_confidence")

    if disease_contradiction:
        conf_tier = "unclear"
    elif disease_conf_fact:
        d_conf = float(disease_conf_fact.value)
        if d_conf >= 0.75:
            conf_tier = "high"
        elif d_conf >= 0.45:
            conf_tier = "medium"
        elif d_conf >= 0.30:
            conf_tier = "low"
        else:
            conf_tier = "unclear"
    elif crop_conf_fact:
        c_conf = float(crop_conf_fact.value)
        if c_conf >= 0.70:
            conf_tier = "high"
        elif c_conf >= 0.40:
            conf_tier = "medium"
        else:
            conf_tier = "low"
    elif evidence_lvl == EvidenceLevel.LOW_EVIDENCE.value:
        conf_tier = "medium"
    elif evidence_lvl == EvidenceLevel.NO_EVIDENCE.value and rag_data.get("status") in ["NO_RELEVANT_CHUNKS", "ERROR"]:
        conf_tier = "low"
    else:
        conf_tier = "high"

    # Enforce: LOW_EVIDENCE RAG can never be presented as HIGH confidence (Section 11 requirement)
    if evidence_lvl == EvidenceLevel.LOW_EVIDENCE.value and conf_tier == "high":
        conf_tier = "medium"
    elif evidence_lvl == EvidenceLevel.NO_EVIDENCE.value and rag_data.get("status") in ["NO_RELEVANT_CHUNKS", "ERROR"] and conf_tier in ["high", "medium"]:
        conf_tier = "low"

    # 6. Compute Aggregated Deterministic Confidence (Critical Fix 4)
    aggregated_conf = compute_deterministic_confidence(state, facts, checks, conf_tier)

    # Compile overall validity
    has_blocking = any(not c.passed and c.severity == CheckSeverity.BLOCKING for c in checks)
    val_result = ValidationResult(
        is_valid=not has_blocking,
        checks=checks,
        verified_facts=facts,
        cross_tool_consistency=cross_tool_res,
        confidence_tier=conf_tier,
        aggregated_confidence=aggregated_conf,
        warnings=warnings,
    )

    state["validation_result"] = val_result.model_dump()
    state["verified_facts"] = [f.model_dump() for f in facts.facts]
    state["confidence_tier"] = conf_tier
    state["aggregated_confidence"] = aggregated_conf

    logger.info(
        "validation_node_complete",
        is_valid=val_result.is_valid,
        facts_count=len(facts.facts),
        checks_count=len(checks),
        confidence_tier=conf_tier,
        aggregated_confidence=aggregated_conf,
        warnings_count=len(warnings),
    )
    return state
