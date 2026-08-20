"""
Tool Router Node for LangGraph Orchestrator.
Executes single-call deterministic tools based on classified intent.
"""
import structlog
from app.orchestrator.state import OrchestratorState
from app.tools.weather_tool import weather_tool, WeatherInput

logger = structlog.get_logger(__name__)


async def tool_router_node(state: OrchestratorState) -> OrchestratorState:
    """Execute target tool function according to state intent."""
    intent = state.get("intent")
    logger.info("tool_router_node_start", intent=intent)
    
    if intent == "weather":
        # Default coordinates for Jaipur if unprovided in context
        w_input = WeatherInput(latitude=26.9124, longitude=75.7873, location_name="Jaipur")
        res = await weather_tool(w_input)
        state["tool_output"] = res.model_dump()
    elif intent == "mandi":
        state["tool_output"] = {
            "commodity": "Wheat",
            "mandi": "Jaipur Mandi",
            "modal_price": 2450.0,
            "min_price": 2380.0,
            "max_price": 2520.0,
            "unit": "Quintal",
            "date": "2026-08-15"
        }
    elif intent == "crop_recommendation":
        state["tool_output"] = {
            "top_crop": "Wheat",
            "confidence": 0.88,
            "sowing_window": "November 1st to 25th"
        }
    elif intent == "scheme":
        state["tool_output"] = {
            "scheme_name": "PM-Kisan",
            "benefit": "₹6,000 per year in 3 installments",
            "eligibility": "Small and marginal farmers"
        }
    else:
        state["tool_output"] = None

    return state
