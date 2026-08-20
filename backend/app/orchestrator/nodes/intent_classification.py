"""
Intent Classification Node for LangGraph Orchestrator.
Classifies farmer queries into standard intents with confidence scores.
"""
from typing import Literal
import structlog
from app.orchestrator.state import OrchestratorState

logger = structlog.get_logger(__name__)

IntentType = Literal["weather", "mandi", "disease", "crop_recommendation", "scheme", "navigation", "clarify", "unknown"]


async def intent_classification_node(state: OrchestratorState) -> OrchestratorState:
    """
    Classify intent from user input.
    If intent confidence < 0.6, enforce safety rule #6: route to clarify question.
    """
    query = state.get("user_input", "").lower().strip()
    logger.info("intent_classification_start", query=query)
    
    # Example intent matching rules (Deity/Devanagari and English keywords)
    if any(kw in query for kw in ["मौसम", "बारिश", "तापमान", "weather", "rain", "temperature", "forecast"]):
        intent = "weather"
        confidence = 0.95
    elif any(kw in query for kw in ["मंडी", "भाव", "कीमत", "दाम", "price", "mandi", "rate", "market"]):
        intent = "mandi"
        confidence = 0.92
    elif any(kw in query for kw in ["बीमारी", "कीड़ा", "पत्ते", "रोग", "disease", "pest", "leaf", "fungus", "spots"]):
        intent = "disease"
        confidence = 0.88
    elif any(kw in query for kw in ["कौन सी फसल", "मिट्टी", "खाद", "recommend", "soil", "which crop", "sow"]):
        intent = "crop_recommendation"
        confidence = 0.90
    elif any(kw in query for kw in ["योजना", "पीएम किसान", "बीमा", "scheme", "pm-kisan", "subsidies"]):
        intent = "scheme"
        confidence = 0.94
    elif any(kw in query for kw in ["स्क्रीन", "खोलें", "पेज", "navigate", "open screen", "dashboard"]):
        intent = "navigation"
        confidence = 0.85
    else:
        intent = "unknown"
        confidence = 0.45  # Low confidence

    # Safety Rule #6: If confidence < 0.6, route to clarify node
    if confidence < 0.6:
        logger.warning("low_intent_confidence_trigger_clarification", confidence=confidence, query=query)
        state["intent"] = "clarify"
        state["intent_confidence"] = confidence
        state["requires_clarification"] = True
    else:
        state["intent"] = intent
        state["intent_confidence"] = confidence
        state["requires_clarification"] = False

    return state
