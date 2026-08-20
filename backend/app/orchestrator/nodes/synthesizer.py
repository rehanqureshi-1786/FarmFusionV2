"""
Response Synthesizer Node for LangGraph Orchestrator.
Formats multi-tool outputs into simple, rural-friendly farmer responses (2-3 sentences max).
"""
import structlog
from app.orchestrator.state import OrchestratorState

logger = structlog.get_logger(__name__)


async def response_synthesizer_node(state: OrchestratorState) -> OrchestratorState:
    """
    Synthesize final response for farmer.
    If requires_clarification is True, generate a clarifying question.
    """
    lang = state.get("detected_language", "hi")
    intent = state.get("intent", "unknown")
    tool_data = state.get("tool_output") or {}
    
    if state.get("requires_clarification"):
        if lang == "hi":
            response = "क्या आप कृपया अपनी फसल का नाम या सवाल दोबारा स्पष्ट कह सकते हैं? ताकि मैं सही जानकारी दे सकूं।"
        else:
            response = "Could you please clarify your crop name or question so I can provide accurate information?"
    else:
        if intent == "weather":
            temp = tool_data.get("temperature_c", "N/A")
            cond = tool_data.get("condition", "N/A")
            loc = tool_data.get("location", "आपकी जगह")
            if lang == "hi":
                response = f"आज {loc} में तापमान {temp}°C है और मौसम {cond} रहेगा। आगामी सप्ताह हल्की बारिश की संभावना है।"
            else:
                response = f"Today in {loc}, the temperature is {temp}°C with {cond} conditions. Light rain is expected this week."
        elif intent == "mandi":
            comm = tool_data.get("commodity", "गेहूं")
            price = tool_data.get("modal_price", 2450)
            mandi = tool_data.get("mandi", "जयपुर मंडी")
            if lang == "hi":
                response = f"आज {mandi} में {comm} का औसत भाव ₹{price} प्रति क्विंटल चल रहा है। आने वाले दिनों में भाव स्थिर रहने की उम्मीद है।"
            else:
                response = f"Today at {mandi}, the average price for {comm} is ₹{price} per quintal."
        else:
            if lang == "hi":
                response = "FarmFusion में आपका स्वागत है। आप मुझसे मौसम, मंडी भाव या फसल बीमारी के बारे में पूछ सकते हैं।"
            else:
                response = "Welcome to FarmFusion. You can ask me about weather, mandi prices, or crop disease diagnostic advice."

    state["final_response"] = response
    logger.info("response_synthesized", intent=intent, lang=lang, response=response)
    return state
