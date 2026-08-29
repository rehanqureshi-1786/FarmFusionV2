"""
Intent Classification & Slot Extraction Node for LangGraph Orchestrator.
Classifies farmer queries into standard intents, extracts typed slots, and resolves conversational references.
"""
from typing import Any, Dict, List, Optional
import re
import structlog

from app.orchestrator.state import OrchestratorState
from app.voice.languages import normalize_crop_name, normalize_soil_name

logger = structlog.get_logger(__name__)


async def intent_classification_node(state: OrchestratorState) -> OrchestratorState:
    """
    Classify intent and extract slots from user input while resolving context from previous turns.
    If intent confidence < 0.6, enforce safety rule #6: route to clarify question.
    """
    query = state.get("user_input", "").lower().strip()
    farmer_ctx = state.get("farmer_context", {}) or {}
    last_recs = state.get("last_recommendations", []) or []
    filled_slots: Dict[str, Any] = dict(state.get("filled_slots", {}) or {})

    logger.info("intent_classification_start", query=query, session_id=state.get("session_id"))

    intent = "unknown"
    confidence = 0.50

    # 1. Check Follow-Up Anaphora: "पहली वाली क्यों?", "why top crop?"
    if any(p in query for p in ["पहली वाली क्यों", "पहला क्यों", "why top", "why first", "पहली फसल क्यों", "क्यों चुनी", "why this crop"]):
        intent = "explain_recommendation"
        confidence = 0.95
        filled_slots["target_index"] = 0
    elif any(p in query for p in ["दूसरी वाली क्यों", "दूसरा क्यों", "why second", "दूसरी फसल क्यों"]):
        intent = "explain_recommendation"
        confidence = 0.95
        filled_slots["target_index"] = 1

    # 2. Check "What-if" Counterfactual: "अगर बारिश कम हो?", "अगर मिट्टी काली हो?"
    elif any(p in query for p in ["अगर बारिश", "यदि बारिश", "what if rain", "कम बारिश"]):
        intent = "what_if"
        confidence = 0.92
        filled_slots["condition_type"] = "rainfall"
        filled_slots["rainfall_modifier"] = "low" if any(w in query for w in ["कम", "low", "सूखा"]) else "high"
    elif any(p in query for p in ["अगर मिट्टी", "यदि मिट्टी", "what if soil"]):
        intent = "what_if"
        confidence = 0.92
        filled_slots["condition_type"] = "soil"
        for s_word in ["काली", "black", "रेतीली", "sandy", "लाल", "red", "दोमट", "alluvial"]:
            if s_word in query:
                filled_slots["soil_type"] = normalize_soil_name(s_word)
                break

    # 3. Weather Intent
    elif any(kw in query for kw in ["मौसम", "बारिश", "तापमान", "weather", "rain", "temperature", "forecast", "हवा", "आंधी"]):
        intent = "weather"
        confidence = 0.95
        # Extract location if mentioned
        for loc in ["jaipur", "udaipur", "jodhpur", "kota", "nagaur", "delhi", "patna", "lucknow", "bhopal", "ahmedabad", "जयपुर", "उदयपुर", "जोधपुर", "कोटा", "नागौर"]:
            if loc in query:
                filled_slots["location_name"] = loc.title()
                break

    # 4. Mandi / Market Prices Intent
    elif any(kw in query for kw in ["मंडी", "भाव", "कीमत", "दाम", "price", "mandi", "rate", "market", "रेट"]):
        intent = "mandi"
        confidence = 0.93
        # Check cross-domain reference: "इसका भाव?" -> carry forward from previous crop
        if any(w in query for w in ["इसका", "इस फसल", "it", "this crop"]) and last_recs:
            filled_slots["commodity"] = last_recs[0].get("crop_name", "Wheat")
        else:
            for c_word in ["गेहूं", "धान", "चावल", "सरसों", "कपास", "चना", "सोयाबीन", "मक्का", "मूंगफली", "बाजरा", "लहसुन", "प्याज", "टमाटर", "wheat", "mustard", "cotton", "rice", "soybean", "gram", "maize", "groundnut", "bajra"]:
                if c_word in query:
                    filled_slots["commodity"] = normalize_crop_name(c_word)
                    break

    # 5. Crop Disease / Pest Intent
    elif any(kw in query for kw in ["बीमारी", "कीड़ा", "पत्ते", "रोग", "disease", "pest", "leaf", "fungus", "spots", "सूख रहे", "पीले पत्ते", "photo", "फोटो", "स्कैन"]):
        intent = "disease"
        confidence = 0.90
        # Carry forward crop from context if not specified
        if any(w in query for w in ["इसमें", "इस फसल", "in this"]) and last_recs:
            filled_slots["crop_name"] = last_recs[0].get("crop_name")
            filled_slots["query_crop_or_disease"] = last_recs[0].get("crop_name")
        else:
            filled_slots["query_crop_or_disease"] = query

    # 6. Crop Recommendation Intent
    elif any(kw in query for kw in ["कौन सी फसल", "फसल सलाह", "recommend", "which crop", "sow", "बुवाई", "क्या बोएं", "उपयुक्त फसल"]):
        intent = "crop_recommendation"
        confidence = 0.92
        for s_word in ["रेतीली", "sandy", "काली", "black", "लाल", "red", "दोमट", "alluvial"]:
            if s_word in query:
                filled_slots["soil_type"] = normalize_soil_name(s_word)
                break

    # 7. Government Schemes Intent
    elif any(kw in query for kw in ["योजना", "पीएम किसान", "बीमा", "सब्सिडी", "scheme", "pm-kisan", "subsidies", "सरकारी"]):
        intent = "scheme"
        confidence = 0.94
        filled_slots["query"] = query

    # 8. In-App Navigation Intent
    elif any(kw in query for kw in ["स्क्रीन", "खोलें", "पेज", "navigate", "open screen", "dashboard", "दिखाएं"]):
        intent = "navigation"
        confidence = 0.88
        for dest in ["crop_recommendation", "disease_detection", "market_prices", "weather", "government_schemes"]:
            if dest.replace("_", " ") in query or dest in query:
                filled_slots["destination"] = dest
                break

    # 9. Unsupported Capabilities
    elif any(kw in query for kw in ["खरीद", "order", "buy", "purchase", "यूरिया मंगा", "पेमेंट", "पैसे भेज"]):
        intent = "unsupported_capability"
        confidence = 0.95
        filled_slots["capability_type"] = "purchase"
    elif any(kw in query for kw in ["आवेदन कर दो", "फॉर्म भर दो", "apply for scheme", "सबमिट कर दो"]):
        intent = "unsupported_capability"
        confidence = 0.95
        filled_slots["capability_type"] = "scheme_application"

    # Enforce Safety Rule #6: Low Confidence Clarification
    if confidence < 0.6:
        logger.warning("low_intent_confidence_trigger_clarification", confidence=confidence, query=query)
        state["intent"] = "clarify"
        state["intent_confidence"] = confidence
        state["requires_clarification"] = True
        state["clarification_question"] = "क्या आप कृपया अपना सवाल दोबारा स्पष्ट कह सकते हैं? (जैसे मौसम, मंडी भाव या फसल सलाह)"
    else:
        state["intent"] = intent
        state["intent_confidence"] = confidence
        state["requires_clarification"] = False

    state["filled_slots"] = filled_slots
    return state
