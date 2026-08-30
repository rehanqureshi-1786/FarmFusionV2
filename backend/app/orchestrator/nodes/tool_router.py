"""
Tool Router Node for LangGraph Orchestrator.
Executes single-call deterministic tools via ToolRegistry based on classified intent and slots.
"""
from typing import Any, Dict, Optional
import structlog

from app.orchestrator.state import OrchestratorState
from app.tools.registry import tool_registry, ToolStatus

logger = structlog.get_logger(__name__)


async def tool_router_node(state: OrchestratorState) -> OrchestratorState:
    """Execute target tool function according to state intent and filled slots."""
    intent = state.get("intent")
    slots = dict(state.get("filled_slots", {}) or {})
    context = dict(state.get("farmer_context", {}) or {})
    last_recs = list(state.get("last_recommendations", []) or [])

    logger.info("tool_router_node_start", intent=intent, slots=slots)

    # 1. Repeat Last Response Intent: Handled directly from session memory
    if intent == "repeat_last":
        last_resp = state.get("last_final_response")
        state["tool_output"] = {
            "type": "repeat",
            "response": last_resp or "पिछली कोई जानकारी उपलब्ध नहीं है।"
        }
        state["tool_status"] = "success"
        return state

    # 2. Speech Rate Control Intent
    if intent == "speech_control":
        rate = slots.get("speech_rate", "slow")
        state["speech_rate"] = rate
        state["tool_output"] = {"type": "speech_control", "rate": rate}
        state["tool_status"] = "success"
        return state

    # 3. Anaphora / Explanation Intent: Handled directly from session memory
    if intent == "explain_recommendation":
        target_idx = int(slots.get("target_index", 0))
        if last_recs and target_idx < len(last_recs):
            rec = last_recs[target_idx]
            state["tool_output"] = {
                "type": "explanation",
                "crop_name": rec.get("crop_name"),
                "suitability_level": rec.get("suitability_level"),
                "suitability_score": rec.get("suitability_score"),
                "factors": rec.get("contributing_factors", []),
                "notes": rec.get("management_notes", []),
            }
            state["tool_status"] = "success"
            state["active_crop"] = rec.get("crop_name")
        else:
            state["tool_output"] = {
                "type": "explanation_unavailable",
                "message": "Previous recommendation context not found.",
            }
            state["tool_status"] = "not_found"
        return state

    # 4. Consequential Action Confirmation Gate
    if intent == "consequential_action":
        action = slots.get("action", "delete_data")
        state["tool_output"] = {
            "type": "consequential_action_confirmation_required",
            "action": action,
            "confirmation_message": "क्या आप वाकई अपनी फसल का डेटा हटाना चाहते हैं? कृपया पुष्टि करें।"
        }
        state["tool_status"] = "requires_confirmation"
        return state

    # 5. Language / Dialect Switching Intent
    if intent == "language_preference":
        target_lang = slots.get("target_language", "hi")
        state["farmer_preferred_language"] = target_lang
        state["response_language"] = target_lang
        state["tool_output"] = {"type": "language_preference", "target_language": target_lang}
        state["tool_status"] = "success"
        return state

    if intent == "dialect_preference":
        target_dialect = slots.get("target_dialect", "rwr")
        state["farmer_preferred_dialect"] = target_dialect
        state["response_dialect"] = target_dialect
        state["tool_output"] = {"type": "dialect_preference", "target_dialect": target_dialect}
        state["tool_status"] = "success"
        return state

    # 4. Map Intent to Tool Name
    tool_map = {
        "weather": "weather_tool",
        "crop_recommendation": "crop_recommendation_tool",
        "what_if": "crop_recommendation_tool",
        "disease": "disease_info_tool",
        "crop_care": "crop_care_tool",
        "mandi": "market_price_tool",
        "scheme": "government_scheme_tool",
        "navigation": "navigation_tool",
        "unsupported_capability": "unsupported_capability_tool",
    }

    tool_name = tool_map.get(intent)
    if not tool_name:
        state["tool_output"] = None
        state["tool_status"] = "no_tool"
        return state

    # Execute tool in registry
    tool_res = await tool_registry.execute(tool_name, slots, context)

    state["last_tool"] = tool_name
    state["last_tool_result"] = tool_res.data
    state["tool_output"] = tool_res.data
    state["tool_status"] = tool_res.status.value

    # Update session memory based on tool type
    if tool_name == "crop_recommendation_tool" and tool_res.data:
        recs = tool_res.data.get("recommendations") or tool_res.data.get("top_crops") or []
        state["last_recommendations"] = recs
        if recs:
            state["active_crop"] = recs[0].get("crop_name")
    elif tool_name == "weather_tool" and tool_res.data:
        state["last_weather_result"] = tool_res.data
    elif tool_name == "market_price_tool" and tool_res.data:
        state["last_market_result"] = tool_res.data
        if slots.get("commodity"):
            state["active_crop"] = slots.get("commodity")
    elif tool_name == "navigation_tool" and tool_res.data:
        state["last_navigation_destination"] = tool_res.data.get("destination")

    return state
