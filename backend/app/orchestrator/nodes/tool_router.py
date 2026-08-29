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

    # 1. Anaphora / Explanation Intent: Handled directly from session memory
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
        else:
            state["tool_output"] = {
                "type": "explanation_unavailable",
                "message": "Previous recommendation context not found.",
            }
            state["tool_status"] = "not_found"
        return state

    # 2. Map Intent to Tool Name
    tool_map = {
        "weather": "weather_tool",
        "crop_recommendation": "crop_recommendation_tool",
        "what_if": "crop_recommendation_tool",
        "disease": "disease_info_tool",
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

    # Update session recommendations memory if crop recommendation succeeded
    if tool_name == "crop_recommendation_tool" and tool_res.data:
        recs = tool_res.data.get("recommendations") or tool_res.data.get("top_crops") or []
        state["last_recommendations"] = recs

    return state
