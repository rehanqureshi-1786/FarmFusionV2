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

    # 1. Unsupported Capabilities (Strict Priority Check)
    if any(kw in query for kw in ["खरीद", "order", "आर्डर", "buy", "purchase", "यूरिया मंगा", "यूरिया आर्डर", "पेमेंट", "पैसे भेज", "मंगा दो"]):
        intent = "unsupported_capability"
        confidence = 0.95
        filled_slots["capability_type"] = "purchase"
    elif any(kw in query for kw in ["आवेदन कर दो", "फॉर्म भर दो", "apply for scheme", "सबमिट कर दो", "रजिस्टर कर दो", "फॉर्म भर"]):
        intent = "unsupported_capability"
        confidence = 0.95
        filled_slots["capability_type"] = "scheme_application"

    # 2. In-App Navigation Intent (Strict Priority for "खोलो", "स्क्रीन", "पेज")
    elif any(kw in query for kw in ["स्क्रीन खोलो", "पेज खोलो", "स्क्रीन", "खोलो", "खोल", "चलो", "जाओ", "वापस", "दिखाओ", "होम पर", "navigate", "open screen", "open"]):
        intent = "navigation"
        confidence = 0.92
        dest = "home"
        if any(w in query for w in ["मंडी", "market", "भाव"]):
            dest = "market_prices"
        elif any(w in query for w in ["मौसम", "weather"]):
            dest = "weather"
        elif any(w in query for w in ["फसल", "crop", "सलाह"]):
            dest = "crop_recommendation"
        elif any(w in query for w in ["बीमारी", "रोग", "disease"]):
            dest = "disease_detection"
        elif any(w in query for w in ["योजना", "scheme"]):
            dest = "government_schemes"
        elif any(w in query for w in ["वापस", "back"]):
            dest = "back"
        elif any(w in query for w in ["होम", "home", "डैशबोर्ड"]):
            dest = "home"
        filled_slots["destination"] = dest

    # 3. Repeat Last Response: "फिर से बताओ", "दोबारा बोलो", "repeat that"
    elif any(p in query for p in ["फिर से बताओ", "दोबारा बोलो", "repeat", "फिर बताओ", "वो वाली कीमत फिर से", "बात दोबारा", "say again", "once more"]):
        intent = "repeat_last"
        confidence = 0.98

    # 4. Speech Rate Control: "धीरे बोलो", "speak slowly"
    elif any(p in query for p in ["धीरे बोलो", "धीमे बोलो", "slowly", "speak slowly", "आराम से बोलो"]):
        intent = "speech_control"
        confidence = 0.95
        filled_slots["speech_rate"] = "slow"

    # 5. Follow-Up Anaphora: "पहली वाली क्यों?", "वो पहली वाली फसल क्यों अच्छी है?"
    elif any(p in query for p in ["पहली वाली क्यों", "पहला क्यों", "why top", "why first", "पहली फसल क्यों", "क्यों चुनी", "why this crop", "पहली वाली फसल क्यों", "पहली वाली फसल"]):
        intent = "explain_recommendation"
        confidence = 0.95
        filled_slots["target_index"] = 0
    elif any(p in query for p in ["दूसरी वाली क्यों", "दूसरा क्यों", "why second", "दूसरी फसल क्यों", "दूसरी वाली"]):
        intent = "explain_recommendation"
        confidence = 0.95
        filled_slots["target_index"] = 1

    # 6. "What-if" Counterfactual: "अगर बारिश कम हो जाए तो?", "अगर पानी कम मिले तो?"
    elif any(p in query for p in ["अगर बारिश", "यदि बारिश", "what if rain", "कम बारिश", "पानी कम", "सूखा"]):
        intent = "what_if"
        confidence = 0.93
        filled_slots["condition_type"] = "rainfall"
        filled_slots["rainfall_modifier"] = "low" if any(w in query for w in ["कम", "low", "सूखा", "घट"]) else "high"
    elif any(p in query for p in ["अगर मिट्टी", "यदि मिट्टी", "what if soil"]):
        intent = "what_if"
        confidence = 0.93
        filled_slots["condition_type"] = "soil"
        for s_word in ["काली", "black", "रेतीली", "sandy", "लाल", "red", "दोमट", "alluvial", "चिकनी", "clay"]:
            if s_word in query:
                filled_slots["soil_type"] = normalize_soil_name(s_word)
                break

    # 7. Crop Care & Fertilizer Timing: "धान की देखभाल कैसे करूं?", "खाद कब डालनी है?"
    elif any(kw in query for kw in ["देखभाल", "खाद कब", "उर्वरक", "सिंचाई कब", "care", "fertilizer timing", "how to grow", "cultivation"]):
        intent = "crop_care"
        confidence = 0.92
        matched_crop = None
        for c_word in ["धान", "गेहूं", "कपास", "सरसों", "चना", "सोयाबीन", "मक्का", "मूंगफली", "बाजरा", "गन्ना", "rice", "wheat", "cotton", "mustard", "groundnut"]:
            if c_word in query:
                matched_crop = normalize_crop_name(c_word)
                break
        filled_slots["crop_name"] = matched_crop or (last_recs[0].get("crop_name") if last_recs else "Wheat")

    # 8. Weather Intent (Multi-lingual: Hindi, Punjabi 'ਮੌਸਮ', Marathi 'हवामान', Gujarati 'વાતાવરણ')
    elif any(kw in query for kw in ["मौसम", "बारिश", "तापमान", "weather", "rain", "temperature", "forecast", "हवा", "आंधी", "mausam", "हवामान", "પાણી", "વાતાવરણ", "ਮੌਸਮ", "ਕਿਵੇਂ"]):
        intent = "weather"
        confidence = 0.95
        for loc in ["jaipur", "udaipur", "jodhpur", "kota", "nagaur", "delhi", "patna", "lucknow", "bhopal", "ahmedabad", "जयपुर", "उदयपुर", "जोधपुर", "कोटा", "नागौर", "पुणे", "अहमदाबाद"]:
            if loc.lower() in query:
                filled_slots["location_name"] = loc.title()
                break

    # 9. Mandi / Market Prices Intent (Multi-lingual: Gujarati 'ભાવ', Punjabi 'ਕੀਮਤ', Telugu 'ధర')
    elif any(kw in query for kw in ["मंडी", "भाव", "कीमत", "दाम", "price", "mandi", "rate", "market", "रेट", "दर", "ભાવ", "શું છે", "ਕੀਮਤ", "ధర"]):
        intent = "mandi"
        confidence = 0.93
        if any(w in query for w in ["इसका", "इस फसल", "it", "this crop", "उसका भाव"]) and last_recs:
            filled_slots["commodity"] = last_recs[0].get("crop_name", "Wheat")
        else:
            for c_word in ["गेहूं", "धान", "चावल", "सरसों", "कपास", "चना", "सोयाबीन", "मक्का", "मूंगफली", "बाजरा", "लहसुन", "प्याज", "टमाटर", "गन्ना", "wheat", "mustard", "cotton", "rice", "soybean", "gram", "maize", "groundnut", "bajra", "chana", "sugarcane", "onion", "potato", "ઘઉં"]:
                if c_word in query:
                    filled_slots["commodity"] = normalize_crop_name(c_word) or "Wheat"
                    break

    # 10. Crop Disease / Pest Intent (with leaf photo redirect guidance)
    elif any(kw in query for kw in ["बीमारी", "कीड़ा", "पत्ते", "रोग", "disease", "pest", "leaf", "fungus", "spots", "सूख रहे", "पीले पत्ते", "photo", "फोटो", "स्कैन", "पत्ता खराब"]):
        intent = "disease"
        confidence = 0.91
        if any(w in query for w in ["इसमें", "इस फसल", "in this"]) and last_recs:
            filled_slots["crop_name"] = last_recs[0].get("crop_name")
            filled_slots["query_crop_or_disease"] = last_recs[0].get("crop_name")
        else:
            filled_slots["query_crop_or_disease"] = query

    # 11. Crop Recommendation Intent (Multi-lingual: Marathi 'पीक'/'शेतात', Gujarati 'પાક')
    elif any(kw in query for kw in ["कौन सी फसल", "फसल सलाह", "recommend", "which crop", "sow", "बुवाई", "क्या बोएं", "उपयुक्त फसल", "खेत में क्या", "क्या लगाऊं", "पीक", "शेतात", "पाक"]):
        intent = "crop_recommendation"
        confidence = 0.92
        for s_word in ["रेतीली", "sandy", "काली", "black", "लाल", "red", "दोमट", "alluvial", "चिकनी", "clay"]:
            if s_word in query:
                filled_slots["soil_type"] = normalize_soil_name(s_word)
                break

    # 12. Government Schemes Intent
    elif any(kw in query for kw in ["योजना", "पीएम किसान", "बीमा", "सब्सिडी", "scheme", "pm-kisan", "subsidies", "सरकारी", "मदद"]):
        intent = "scheme"
        confidence = 0.94
        filled_slots["query"] = query

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
