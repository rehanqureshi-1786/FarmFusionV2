"""
Semantic Intent & Entity Extraction Layer for FarmFusion LangGraph Orchestrator.

Implements:
1. LLM semantic parsing with strict structured JSON output conforming to SemanticFrame.
2. Robust, comprehensive deterministic fallback with bidirectional agricultural normalization.
3. Multi-turn context inheritance (carrying forward active crop, location, and accumulated slots).
4. Compound intent & multi-capability detection (e.g. Weather + Irrigation, Mandi Price + Comparison + Forecast).
5. Explicit sensor / input gating (e.g. flagging RequiredInput.LEAF_IMAGE for disease diagnosis).
6. Transparent, calculated multi-dimensional confidence scoring.
"""
from __future__ import annotations

import os
import re
import json
import uuid
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import structlog

from app.schemas.semantic_frame import (
    CanonicalIntent,
    CapabilityType,
    RequiredInput,
    ActionIntent,
    NavigationDestination,
    ConfidenceSet,
    SoilValues,
    FarmLocation,
    EntitySet,
    TimeContext,
    RelativeDay,
    UserContext,
    ConversationContext,
    SemanticFrame,
)
from app.orchestrator.normalization import (
    normalize_crop_name,
    extract_crops,
    extract_markets,
    normalize_soil_type,
    extract_forecast_days,
    extract_timeframe,
    resolve_time_context,
)
from app.voice.languages import detect_dialect

logger = structlog.get_logger(__name__)


# =============================================================================
# DETERMINISTIC EXTRACTION ENGINE (PRIMARY & FALLBACK)
# =============================================================================

def extract_semantic_frame_deterministic(
    raw_text: str,
    detected_language: str = "hi",
    detected_dialect: Optional[str] = None,
    user_context: Optional[UserContext] = None,
    conversation_context: Optional[ConversationContext] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> SemanticFrame:
    """
    Robust deterministic semantic extractor using verified agricultural catalog
    and domain heuristics. Populates the exact same Canonical SemanticFrame.
    """
    clean_text = raw_text.strip()
    lower_text = clean_text.lower()
    req_id = request_id or f"req_{uuid.uuid4().hex[:8]}"
    sess_id = session_id or "default_session"

    # Dialect detection if not already supplied
    if not detected_dialect:
        dialect_res = detect_dialect(clean_text, detected_language=detected_language)
        if dialect_res.dialect:
            detected_dialect = dialect_res.dialect
            detected_language = dialect_res.language

    # 1. Normalize agricultural entities
    crops = extract_crops(clean_text)
    crop = crops[0] if len(crops) == 1 else None
    markets = extract_markets(clean_text)
    primary_market = markets[0] if len(markets) == 1 else None
    forecast_days = extract_forecast_days(clean_text)
    timeframe = extract_timeframe(clean_text)
    soil_type = normalize_soil_type(clean_text)

    # 2. Multi-turn context inheritance & Ambiguity Safety
    candidate_crops = list(getattr(conversation_context, "candidate_crops", []) or [])
    for c in crops:
        if c not in candidate_crops:
            candidate_crops.append(c)

    candidate_markets = list(getattr(conversation_context, "candidate_markets", []) or [])
    for m in markets:
        if m not in candidate_markets:
            candidate_markets.append(m)

    deictic_crop_markers = [
        "इस फसल", "यह फसल", "ये फसल", "इसकी", "इसका", "इसमें", "my crop", "the crop",
        "this crop", "is fasal", "ye fasal", "meri fasal", "hamari fasal", "apni fasal",
        "is crop", "that crop", "it", "itna", "iski", "iska", "dekhbhal", "देखभाल",
        "iske liye", "इसके लिए", "is ke liye", "iske", "isko", "इसको",
        "uske liye", "उसके लिए", "uske", "usko", "उसको",
        "mere liye", "मेरे लिए", "ispe", "is par", "इस पर", "is pe",
        "phir", "fir", "फिर", "aur kal", "और कल",
    ]
    has_deictic_crop = any(w in lower_text for w in deictic_crop_markers)

    deictic_market_markers = [
        "इस मंडी", "is mandi", "iss mandi", "yahan", "यहाँ", "vahan", "वहाँ",
        "is market", "there", "aaj bechna", "bechna theek", "rukna theek", "rukna sahi",
        "bechu", "bechun", "sell today", "sell now"
    ]
    has_deictic_mandi = any(w in lower_text for w in deictic_market_markers)

    # Ambiguity Check: multiple candidates without user specification OR isolated deictic reference without any context
    is_ambiguous_crop = (
        crop is None
        and has_deictic_crop
        and (
            (len(candidate_crops) > 1 and not any(c.lower() in lower_text for c in candidate_crops))
            or (not conversation_context or not conversation_context.active_crop)
        )
    )
    is_ambiguous_market = (
        primary_market is None
        and has_deictic_mandi
        and (
            (len(candidate_markets) > 1 and not any(m.lower() in lower_text for m in candidate_markets))
            or (has_deictic_mandi and any(w in lower_text for w in ["is mandi", "iss mandi", "इस मंडी"]) and (not conversation_context or not conversation_context.active_market))
        )
    )

    if is_ambiguous_crop or is_ambiguous_market:
        crop = None
        primary_market = None
        markets = []
    else:
        # Unambiguous crop inheritance
        if crop is None and conversation_context and conversation_context.active_crop:
            if has_deictic_crop:
                crop = conversation_context.active_crop
            elif not any(w in lower_text for w in ["फसल", "crop", "कौन सी"]):
                crop = conversation_context.active_crop

        # Unambiguous market inheritance
        if not primary_market and conversation_context and conversation_context.active_market:
            if has_deictic_mandi or not any(w in lower_text for w in ["मंडी", "mandi", "market"]):
                primary_market = conversation_context.active_market
                markets = [primary_market]

    # 3. Location context inheritance
    primary_city = primary_market or (conversation_context.active_location if conversation_context else None)
    primary_district = None
    primary_state = None
    if not primary_city and user_context and user_context.farm_location:
        loc = user_context.farm_location
        primary_city = loc.city
        primary_district = loc.district
        primary_state = loc.state

    # 4. Intent & Required Capability Detection
    required_capabilities: List[CapabilityType] = []
    required_input = RequiredInput.NONE
    sub_intent: Optional[str] = None

    # Keyword bundles
    is_action_inquiry = any(w in lower_text for w in [
        "kya karna chahiye", "kya karna hai", "kya karu", "kya karein", "kya karna hoga",
        "kya kare", "kya karun", "what to do", "what should i do", "what next",
        "aur kal", "kal kya", "kal ka kya", "aaj kya", "kya kare", "kya karna",
        "क्या करना चाहिए", "क्या करूं", "क्या करें", "क्या करना है"
    ])
    is_photo_inquiry = any(w in lower_text for w in [
        "photo bheju", "photo bhej", "फोटो भेज", "तस्वीर भेज", "tashveer bheju",
        "image bheju", "pic bheju", "photo kheechu", "फोटो खींचू", "send photo",
        "send picture", "photo bhejun", "photo khichu"
    ])
    is_nav_kw = any(w in lower_text for w in [
        "स्क्रीन खोलो", "पेज खोलो", "स्क्रीन", "खोलो", "चलो", "दिखाओ", "open screen",
        "navigate", "open crop", "वापस", "camera", "कैमरा खोलो"
    ])
    is_repeat_kw = any(w in lower_text for w in [
        "फिर से बताओ", "दोबारा बोलो", "repeat", "say again", "once more", "फिर बताओ", "दोबारा"
    ])
    is_scheme_kw = any(w in lower_text for w in [
        "योजना", "scheme", "पीएम किसान", "pm kisan", "pm-kisan", "सब्सिडी",
        "subsidy", "फसल बीमा", "बीमा योजना", "bima yojana", "kcc", "क्रेडिट कार्ड", "किस्त"
    ])
    is_calling_kw = any(w in lower_text for w in [
        "कॉल करो", "कॉल कर दो", "फोन करो", "फोन कर दो", "कॉल करें", "फोन करें", "फोन लगाओ", "फोन मिलाओ",
        "call", "phone karo", "call karo", "call the farmer", "phone kar do", "phone mila do",
        "call kijiye", "phone milao", "कॉल मिलाओ", "फोन लगाओ", "call lagao", "outbound call",
        "farmer ko call", "किसान को फोन", "किसान को कॉल", "phone laga do", "call laga do", "phone lagao",
        "call me", "call me now", "please call me", "give me a call", "can you call me", "call me please",
        "mujhe call karo", "mujhe call kar do", "mujhe phone karo", "mujhe phone lagao", "call back",
        "call me back", "कॉल बैक", "मुझे कॉल करो", "मुझे फोन करो", "मुझे कॉल", "मुझे फोन", "फोन कर"
    ])
    is_weather_kw = any(w in lower_text for w in [
        "मौसम", "weather", "बारिश", "rain", "तापमान", "temperature", "वर्षा",
        "बादल", "हवामान", "વાતાવરણ", "વરસાદ", "ਮੌਸਮ", "ਮੀਂਹ", "আবহাওয়া", "বৃষ্টি",
        "வானிலை", "மழை", "వాతావరణం", "వర్షం", "ಹವಾಮಾನ", "ಮಳೆ", "കാലാവസ്ഥ",
        "mausam", "barish", "baarish", "pani girega", "paus", "varsad", "brishti", "havaman", "धूप", "हवा",
        "badal", "badlo", "dhoop", "andhi", "hawa", "fog", "kohra", "barsat", "tapan", "garmi", "sardi", "megh"
    ])
    is_irrigation_kw = any(w in lower_text for w in [
        "सिंचाई", "irrigation", "irrigate", "पानी देना", "पानी देने", "पानी दूं", "water", "pani doon",
        "पानी लगाऊं", "सिंचना", "water stress", "moisture", "પાણી આપવું", "પાણી પાવું", "water karun",
        "પાણી ક્યારે", "geeli", "geela", "sukhi", "sukha", "nami", "paani rok", "pani band", "paani band",
        "paani kab du", "kab paani", "paani lagayein", "pani kab", "pani dena", "paani kab", "paani dena",
        "kab pani", "paani kab dena", "pani kab dena", "paani lagana", "pani lagana"
    ]) or (
        ("paani" in lower_text or "pani" in lower_text or "पानी" in lower_text)
        and any(w in lower_text for w in ["kab", "dena", "lagana", "du", "doon", "कब", "देना", "लगाना", "दूं", "कब देना"])
    )
    is_irrigation_followup = (
        any(w in lower_text for w in [
            "aaj karu", "aaj karein", "aaj karun", "karu kya", "aaj du", "aaj doon", "aaj lagau", "आज करूं", "आज करू", "karu", "karein", "kare kya"
        ])
        and (
            is_irrigation_kw
            or (conversation_context and str(conversation_context.last_intent).lower() in ["smart_irrigation", "irrigation_advisory", "irrigation"])
            or (conversation_context and any(w in str(conversation_context.accumulated_slots).lower() for w in ["irrigation", "water", "pani", "paani"]))
        )
    )
    is_mandi_kw = any(w in lower_text for w in [
        "मंडी", "mandi", "भाव", "bhav", "रेट", "rate", "कीमत", "दाम", "price",
        "मार्केट", "market", "બજાર", "ભાવ", "ਕੀਮਤ", "ਧਰ", "விலை", "modal price",
        "ਭਾਅ", "ਮੰਡੀ"
    ])
    is_disease_kw = any(w in lower_text for w in [
        "बीमारी", "disease", "रोग", "कीड़े", "कीड़ा", "कीड़ा", "कीट", "pest", "पत्ता खराब", "धब्बे", "ડાઘ", "પાંદડા",
        "fungus", "इल्ली", "rog", "bimari", "keeda", "kitnashak", "दवा", "स्प्रे", "ઉકઠા", "उकठा",
        "spots", "leaf", "blight", "rust", "कीटनाशक", "खराब हो गई", "पहचानो",
        "peele nishan", "peele patte", "peele dhabbe", "peela pad raha", "peeli pad rahi", "dhabbe", "dhabbey",
        "patte sukh rahe", "sukhte patte", "murjha", "disease kaise",
        "dawai", "dawa", "spray", "safed makkhi", "makkhi", "whitefly", "prakop", "keet", "kit"
    ])
    is_disaster_kw = any(w in lower_text for w in [
        "बाढ़", "flood", "तूफान", "storm", "cyclone", "चक्रवात", "सूखा", "drought",
        "आपदा", "disaster", "खतरा", "जोखिम", "heavy rain risk", "વાવાઝોડું", "અતિવૃષ્ટિ",
        "હੜ੍ਹ", "હੜ੍ਹ", "ਖ਼ਤਰਾ", "calamity", "दुष्काळ", "अतिवृष्टी", "दुष्काळाची",
        "safe hai", "surakshit", "suraksha", "khatra", "nuksan", "fasal ko kaise bachaye", "khet me kaam karna safe", "bachaye", "bachav"
    ])
    is_crop_rec_kw = any(w in lower_text for w in [
        "कौन सी फसल", "what crop", "which crop", "फसल सलाह", "crop recommendation",
        "क्या बोएं", "क्या लगाएं", "क्या बोना", "kya boye", "kya lagaye", "recommend crop", "खेती",
        "કયો પાક", "પાક", "पीक", "পাক", "કાળી જમીન", "રેતીલી",
        "kaunsi fasal theek rahegi", "konsi fasal theek", "mere khet ke hisaab se", "kaunsi kheti",
        "kya uga sakta", "kya ugayein", "uga sakte hain", "kya boyein"
    ])
    is_animal_kw = any(w in lower_text for w in [
        "जानवर", "animal", "नीलगाय", "nilgai", "सूअर", "pig", "घुसपैठ", "intrusion",
        "खेत सुरक्षित", "sensor", "farm security", "सुरक्षा अलार्म", "perimeter",
        "suar", "janwar", "ghus", "boundary", "tarbandi"
    ])
    is_decision_kw = any(w in lower_text for w in [
        "बेचूं या", "रुकूं", "sell now or wait", "should i sell", "कब बेचूं", "निर्णय", "बेचना ठीक", "hold", "sell right now",
        "बेचना चाहिए", "बेच दूं", "बेचू", "bechna chahiye", "bech du", "bechun", "sell karun", "sell karna chahiye",
        "hold or sell", "sell today", "sell or wait", "વિકાવે કા", "વેચવું જોઈએ", "વેચું", "ਵੇਚਣਾ ਚਾਹੀਦਾ", "विकू", "विकायला", "विकू का",
        "neeche ja raha", "gir raha", "rukna sahi hoga", "bechna sahi hoga", "wait karein ya sell", "rukna chahiye", "kya rukna", "sahi time bechne ka",
        "bechna theek", "bechna sahi", "aaj bechna", "bechna kaisa", "bechna"
    ])
    is_comparison_kw = any(w in lower_text for w in [
        "compare", "तुलना", "कहाँ महंगा", "कहाँ सस्ता", "vs", "versus", "बनाम", "better", "महंगा", "सस्ता"
    ]) or len(markets) >= 2
    is_forecast_kw = any(w in lower_text for w in [
        "forecast", "अनुमान", "अगले 7 दिन", "अगले हफ्ते", "7-day", "7 day", "14 दिन", "बढ़ेगा या घटेगा", "आगे बढ़ेगा",
        "rise over the next week", "prices rise", "will prices rise", "future price", "prediction", "predict",
        "भविष्यवाणी", "भाव वाढेल का", "ભાવ વધશે"
    ]) or (forecast_days is not None and (is_mandi_kw or crop is not None))


    # Intent Resolution Tree
    intent = CanonicalIntent.GENERAL_AGRICULTURE
    intent_confidence = 0.85
    entity_confidence = 0.90

    # 0. Ambiguity Safety Gate (Never guess between multiple crops or markets)
    if is_ambiguous_crop or is_ambiguous_market:
        intent = CanonicalIntent.CLARIFICATION
        required_capabilities = []
        intent_confidence = 0.50

    # 1. Repeat Last Response
    elif is_repeat_kw:
        intent = CanonicalIntent.REPEAT_LAST
        intent_confidence = 0.98

    # 2. In-App Navigation (Priority Check)
    elif is_nav_kw:
        intent = CanonicalIntent.NAVIGATION_REQUEST
        required_capabilities = [CapabilityType.NAVIGATION]
        intent_confidence = 0.96

    # 2b. Calling Intent (Priority Check)
    elif is_calling_kw:
        intent = CanonicalIntent.CALLING
        required_capabilities = [CapabilityType.CALLING]
        intent_confidence = 0.98

    # 3. Government Schemes & Subsidies (Priority Check)
    elif is_scheme_kw:
        intent = CanonicalIntent.GOVERNMENT_SCHEME
        required_capabilities = [CapabilityType.GOVERNMENT_SCHEME]
        intent_confidence = 0.95

    # 3b. Disease Photo / Symptom Offer
    elif is_photo_inquiry:
        intent = CanonicalIntent.DISEASE_DETECTION
        required_capabilities = [CapabilityType.DISEASE_DETECTION]
        required_input = RequiredInput.LEAF_IMAGE
        intent_confidence = 0.95

    # 4. Compound: Irrigation Advisory (Weather + Soil Moisture) & Irrigation Follow-up
    elif is_irrigation_kw and is_weather_kw:
        intent = CanonicalIntent.IRRIGATION_ADVISORY
        required_capabilities = [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION]
        intent_confidence = 0.95
    elif is_irrigation_followup:
        intent = CanonicalIntent.IRRIGATION_ADVISORY
        required_capabilities = [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION]
        intent_confidence = 0.94
    elif is_action_inquiry and crop is not None:
        intent = CanonicalIntent.IRRIGATION_ADVISORY
        required_capabilities = [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION]
        intent_confidence = 0.94
    elif is_irrigation_kw:
        intent = CanonicalIntent.SMART_IRRIGATION
        required_capabilities = [CapabilityType.SMART_IRRIGATION]
        intent_confidence = 0.92

    # 5. Mandi Decision / Comparison / Forecast / Price
    elif is_decision_kw or (is_comparison_kw and forecast_days):
        intent = CanonicalIntent.MANDI_DECISION
        required_capabilities = [
            CapabilityType.CURRENT_PRICE,
            CapabilityType.MANDI_FORECAST,
            CapabilityType.MANDI_DECISION
        ]
        if is_comparison_kw:
            required_capabilities.insert(1, CapabilityType.MANDI_COMPARISON)
        intent_confidence = 0.95
    elif (is_comparison_kw and len(markets) >= 2) or any(w in lower_text for w in ["compare", "तुलना", "बनाम", "better"]):
        intent = CanonicalIntent.MANDI_COMPARISON
        required_capabilities = [CapabilityType.CURRENT_PRICE, CapabilityType.MANDI_COMPARISON]
        intent_confidence = 0.94
    elif is_forecast_kw and (is_mandi_kw or crop):
        intent = CanonicalIntent.MANDI_FORECAST
        required_capabilities = [CapabilityType.MANDI_FORECAST]
        intent_confidence = 0.94
    elif is_mandi_kw:
        intent = CanonicalIntent.MANDI_PRICE
        required_capabilities = [CapabilityType.CURRENT_PRICE]
        intent_confidence = 0.94

    # 6. Disease Detection (Gated by Leaf Image requirement)
    elif is_disease_kw:
        intent = CanonicalIntent.DISEASE_DETECTION
        required_capabilities = [CapabilityType.DISEASE_DETECTION, CapabilityType.RAG_KNOWLEDGE]
        required_input = RequiredInput.LEAF_IMAGE
        intent_confidence = 0.95

    # 7. Disaster Risk
    elif is_disaster_kw:
        intent = CanonicalIntent.DISASTER_RISK
        required_capabilities = [
            CapabilityType.WEATHER,
            CapabilityType.DISASTER_RISK,
            CapabilityType.RAG_KNOWLEDGE
        ]
        intent_confidence = 0.96

    # 8. Crop Recommendation
    elif is_crop_rec_kw or soil_type:
        intent = CanonicalIntent.CROP_RECOMMENDATION
        required_capabilities = [CapabilityType.CROP_RECOMMENDATION]
        intent_confidence = 0.95

    # 9. Weather
    elif is_weather_kw:
        intent = CanonicalIntent.WEATHER
        required_capabilities = [CapabilityType.WEATHER]
        intent_confidence = 0.95

    # 10. Animal Alert
    elif is_animal_kw:
        intent = CanonicalIntent.ANIMAL_ALERT
        required_capabilities = [CapabilityType.ANIMAL_ALERT]
        intent_confidence = 0.95

    # Multi-intent check: Append weather capability if query contains explicit weather query alongside mandi/crop
    if is_weather_kw and CapabilityType.WEATHER not in required_capabilities and intent != CanonicalIntent.WEATHER:
        required_capabilities.append(CapabilityType.WEATHER)

    # Multi-turn intent inheritance if current turn has no explicit intent keywords but has conversation context
    if intent == CanonicalIntent.GENERAL_AGRICULTURE and conversation_context and conversation_context.last_intent:
        if primary_market or crop or timeframe or len(clean_text.split()) <= 4:
            try:
                intent = CanonicalIntent(conversation_context.last_intent)
                if intent == CanonicalIntent.MANDI_PRICE:
                    required_capabilities = [CapabilityType.CURRENT_PRICE]
                elif intent == CanonicalIntent.WEATHER:
                    required_capabilities = [CapabilityType.WEATHER]
                elif intent == CanonicalIntent.SMART_IRRIGATION:
                    required_capabilities = [CapabilityType.SMART_IRRIGATION]
                elif intent == CanonicalIntent.CROP_RECOMMENDATION:
                    required_capabilities = [CapabilityType.CROP_RECOMMENDATION]
                elif intent == CanonicalIntent.DISEASE_DETECTION:
                    required_capabilities = [CapabilityType.DISEASE_DETECTION, CapabilityType.RAG_KNOWLEDGE]
                    required_input = RequiredInput.LEAF_IMAGE
                intent_confidence = 0.92
            except (ValueError, TypeError):
                pass

    # Low-Confidence / Unknown Fallback Gate
    if intent == CanonicalIntent.GENERAL_AGRICULTURE:
        # Check if query specifically referenced a crop ("इस फसल", "my crop") but no crop could be resolved
        if has_deictic_crop and not crop:
            intent = CanonicalIntent.CLARIFICATION
            required_capabilities = []
            intent_confidence = 0.50
        # Check if length < 3 characters or random noise or purely acknowledgment
        elif len(clean_text) <= 3 or not re.search(r'[\w]', clean_text) or lower_text in ["हम्म", "...", "ok", "बताओ", "hmm", "haan", "theek hai"]:
            intent = CanonicalIntent.CLARIFICATION
            required_capabilities = []
            intent_confidence = 0.40
        elif any(w in lower_text for w in ["खाद", "जीवामृत", "रोपाई", "पैदावार", "fertilizer", "yield"]):
            intent = CanonicalIntent.AGRICULTURAL_KNOWLEDGE
            required_capabilities = [CapabilityType.RAG_KNOWLEDGE]
            intent_confidence = 0.92
        else:
            required_capabilities = [CapabilityType.RAG_KNOWLEDGE]
            intent_confidence = 0.70

    # Entity Confidence calculation
    if crop:
        entity_confidence = min(entity_confidence + 0.05, 0.98)
    if markets:
        entity_confidence = min(entity_confidence + 0.05, 0.98)
    if not crop and intent in [CanonicalIntent.MANDI_PRICE, CanonicalIntent.DISEASE_DETECTION]:
        entity_confidence = max(entity_confidence - 0.15, 0.60)

    # Language confidence heuristic
    lang_conf = 0.98 if detected_language in ["hi", "en", "pa", "gu", "mr"] else 0.90
    overall_conf = round(min(intent_confidence, entity_confidence, lang_conf), 4)

    # Construct EntitySet
    phone_match = re.search(r'(\+?91[\-\s]?)?[6789]\d{9}', clean_text)
    add_entities = {}
    if phone_match:
        add_entities["phone"] = phone_match.group(0).replace(" ", "").replace("-", "")
    if is_irrigation_kw or is_irrigation_followup:
        add_entities["topic"] = "irrigation"
    if len(crops) > 1:
        add_entities["candidate_crops"] = crops
    if len(markets) > 1:
        add_entities["candidate_markets"] = markets

    entities = EntitySet(
        crop=crop,
        disease=None,
        market=primary_market,
        mandi=primary_market,
        markets=markets,
        city=primary_city,
        district=primary_district,
        state=primary_state,
        timeframe=timeframe,
        forecast_days=forecast_days,
        time_context=TimeContext.model_validate(
            resolve_time_context(clean_text)
        ) if resolve_time_context(clean_text).get("relative_day") != "UNSPECIFIED" or resolve_time_context(clean_text).get("explicit_date") else None,
        soil_values=SoilValues(soil_type=soil_type) if soil_type else None,
        season="Kharif" if any(w in lower_text for w in ["खरीफ", "kharif"]) else ("Rabi" if any(w in lower_text for w in ["रबी", "rabi"]) else None),
        additional_entities=add_entities,
    )


    conf_set = ConfidenceSet(
        language_confidence=lang_conf,
        intent_confidence=round(intent_confidence, 4),
        entity_confidence=round(entity_confidence, 4),
        overall_confidence=overall_conf,
    )

    return SemanticFrame(
        request_id=req_id,
        session_id=sess_id,
        raw_text=raw_text,
        normalized_text=clean_text,
        language=detected_language,
        dialect=detected_dialect,
        intent=intent,
        sub_intent=sub_intent,
        required_capabilities=required_capabilities,
        entities=entities,
        required_input=required_input,
        confidence=conf_set,
        user_context=user_context,
        conversation_context=conversation_context,
        requested_output_language=detected_language,
    )


# =============================================================================
# LLM SEMANTIC EXTRACTION ENGINE
# =============================================================================

EXTRACTION_SYSTEM_PROMPT = """You are FarmFusion NLU, an expert multilingual agricultural intent and entity extractor.
Your job is to parse rural Indian farmer queries (in Hindi, Hinglish, English, Gujarati, Marathi, Punjabi, Tamil, Telugu, Kannada, Malayalam, Marwari, Mewari) into a strict structured JSON SemanticFrame.

ALLOWED INTENTS:
weather, smart_irrigation, irrigation_advisory, disaster_risk, crop_recommendation, disease_detection, mandi_price, mandi_forecast, mandi_comparison, mandi_decision, sell_hold, government_scheme, agricultural_knowledge, animal_alert, general_agriculture, navigation_request, calling, repeat_last, clarification, unsupported.

ALLOWED CAPABILITIES:
WEATHER, SMART_IRRIGATION, DISASTER_RISK, CROP_RECOMMENDATION, DISEASE_DETECTION, CURRENT_PRICE, MANDI_CURRENT_PRICE, MANDI_HISTORY, MANDI_FORECAST, MANDI_COMPARISON, MANDI_DECISION, RAG_KNOWLEDGE, GOVERNMENT_SCHEME, ANIMAL_ALERT, TELEPHONY_CALL, APP_NAVIGATION.

RULES:
1. Output ONLY valid JSON conforming to the SemanticFrame schema. No conversational preamble.
2. NEVER calculate numbers, predict prices, estimate weather, or diagnose diseases. You only EXTRACT what the farmer meant.
3. If the farmer asks about plant diseases, pests, or leaf damage without attaching an image, set required_input="LEAF_IMAGE".
4. For multi-part queries (e.g. "rain tomorrow, should I irrigate wheat?"), detect compound capabilities: ["WEATHER", "SMART_IRRIGATION"] and intent="irrigation_advisory".
5. For market decisions (e.g. "sell in Jaipur or Kalapipal, what rate next 7 days?"), detect capabilities: ["CURRENT_PRICE", "MANDI_COMPARISON", "MANDI_FORECAST", "MANDI_DECISION"].
6. Unknown entities must be null. Never invent fake crops or locations.
7. Normalize crop names to English (e.g. gehu -> "Wheat", pyaaz -> "Onion", dhan -> "Paddy", kapas -> "Cotton").
8. MULTI-TURN CONTEXT RESOLUTION & DEICTIC REFERENCES:
- Resolve deictic/anaphoric references ("iske liye", "is fasal ke liye", "is crop ke liye", "mere liye", "uske liye", "isko", "phir", "aur kal?", "kal kya karna hai?", "aaj bechna theek rahega?", "photo bheju kya?", "ab flood ka risk hai?") using the Context Hints.
- UNAMBIGUOUS ENTITY INHERITANCE: If there is an active_crop or active_market or active_location in Context Hints and the query refers to it via pronouns or follow-up questions, inherit that entity in entities.crop / entities.market / entities.city.
- AMBIGUITY SAFETY: If candidate_crops or candidate_markets in Context Hints contains multiple items and the query does not specify which one (e.g. "iske liye kya karu?" when both Wheat and Mustard are present), set intent="clarification" with confidence 0.50. Never guess between multiple crops or markets.
- CURRENT UTTERANCE DETERMINES NEW INTENT:
  * Inquiring what to do tomorrow/actions for an active crop ("iske liye kal kya karna chahiye?", "kal kya karu?"): Intent is "irrigation_advisory" with required_capabilities: ["WEATHER", "SMART_IRRIGATION"].
  * Inquiring whether to sell today or hold for an active crop/mandi ("aaj bechna theek rahega?", "rukna chahiye?"): Intent is "mandi_decision" with required_capabilities: ["CURRENT_PRICE", "MANDI_FORECAST", "MANDI_DECISION"].
  * Inquiring about rainfall/weather with inherited location ("kal barish hogi?"): Intent is "weather" with required_capabilities: ["WEATHER"].
  * Inquiring about sending a photo for leaf/disease symptoms ("photo bheju kya?"): Intent is "disease_detection" with required_input="LEAF_IMAGE" and required_capabilities: ["DISEASE_DETECTION"].
  * Inquiring whether to irrigate today following irrigation context ("aaj karu?"): Intent is "irrigation_advisory" with required_capabilities: ["WEATHER", "SMART_IRRIGATION"].
  * Inquiring about flood or disaster risk following rainfall ("ab flood ka risk hai?"): Intent is "disaster_risk" with required_capabilities: ["WEATHER", "DISASTER_RISK"].
  * DO NOT automatically map follow-up queries to RAG_KNOWLEDGE when a specialist capability applies.
"""


def map_canonical_intent(raw_intent: str) -> CanonicalIntent:
    s = str(raw_intent).lower().strip()
    for intent in CanonicalIntent:
        if intent.value == s or intent.name.lower() == s:
            return intent
    if "irrigat" in s or "paani" in s or "water" in s:
        return CanonicalIntent.IRRIGATION_ADVISORY
    if "weather" in s or "mausam" in s or "barish" in s or "rain" in s:
        return CanonicalIntent.WEATHER
    if "mandi" in s or "price" in s or "rate" in s or "bhav" in s:
        if "forecast" in s or "aage" in s:
            return CanonicalIntent.MANDI_FORECAST
        if "compare" in s or "tulna" in s:
            return CanonicalIntent.MANDI_COMPARISON
        return CanonicalIntent.MANDI_PRICE
    if "disease" in s or "kida" in s or "patte" in s or "bimari" in s:
        return CanonicalIntent.DISEASE_DETECTION
    if "crop" in s or "fasal" in s or "recommend" in s or "uga" in s:
        return CanonicalIntent.CROP_RECOMMENDATION
    if "disaster" in s or "aapdha" in s or "flood" in s or "toofan" in s or "risk" in s:
        return CanonicalIntent.DISASTER_RISK
    if "call" in s or "phone" in s:
        return CanonicalIntent.CALLING
    if "navigate" in s or "kholo" in s or "open" in s:
        return CanonicalIntent.NAVIGATION_REQUEST
    if "scheme" in s or "yojana" in s:
        return CanonicalIntent.GOVERNMENT_SCHEME
    return CanonicalIntent.GENERAL_AGRICULTURE


def map_capability_type(raw_cap: str) -> Optional[CapabilityType]:
    s = str(raw_cap).upper().strip()
    for cap in CapabilityType:
        if cap.value == s or cap.name == s:
            return cap
    if "WEATHER" in s:
        return CapabilityType.WEATHER
    if "IRRIGAT" in s:
        return CapabilityType.SMART_IRRIGATION
    if "PRICE" in s or "RATE" in s:
        return CapabilityType.CURRENT_PRICE
    if "FORECAST" in s:
        return CapabilityType.MANDI_FORECAST
    if "COMPARE" in s or "COMPARISON" in s:
        return CapabilityType.MANDI_COMPARISON
    if "DISEASE" in s:
        return CapabilityType.DISEASE_DETECTION
    if "CROP" in s or "SUITABILITY" in s:
        return CapabilityType.CROP_RECOMMENDATION
    if "DISASTER" in s:
        return CapabilityType.DISASTER_RISK
    if "CALL" in s or "PHONE" in s or "TELEPHONY" in s:
        return CapabilityType.CALLING
    if "NAV" in s:
        return CapabilityType.NAVIGATION
    if "RAG" in s or "KNOWLEDGE" in s:
        return CapabilityType.RAG_KNOWLEDGE
    return None


async def extract_semantic_frame_llm(
    raw_text: str,
    detected_language: str = "hi",
    detected_dialect: Optional[str] = None,
    user_context: Optional[UserContext] = None,
    conversation_context: Optional[ConversationContext] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    timeout_seconds: float = 8.0,
) -> Optional[SemanticFrame]:
    """
    Invokes configured cloud LLM (OpenRouter primary with Groq fallback) to extract SemanticFrame.
    Returns None if LLM is unavailable, times out, or returns invalid schema, triggering
    the deterministic agricultural extractor fallback.
    """
    from app.core.config import get_settings
    settings = get_settings()

    clean_text = raw_text.strip()
    req_id = request_id or f"req_{uuid.uuid4().hex[:8]}"
    sess_id = session_id or "default_session"

    context_hints: Dict[str, Any] = {}
    if conversation_context:
        if conversation_context.active_crop:
            context_hints["active_crop"] = conversation_context.active_crop
        if conversation_context.active_market:
            context_hints["active_market"] = conversation_context.active_market
        if conversation_context.active_location:
            context_hints["active_location"] = conversation_context.active_location
        if conversation_context.candidate_crops:
            context_hints["candidate_crops"] = conversation_context.candidate_crops
        if conversation_context.candidate_markets:
            context_hints["candidate_markets"] = conversation_context.candidate_markets
        if conversation_context.last_intent:
            context_hints["previous_turn_intent"] = conversation_context.last_intent
        if conversation_context.accumulated_slots:
            context_hints["accumulated_slots"] = conversation_context.accumulated_slots
    if user_context and user_context.farm_location:
        context_hints["default_location"] = user_context.farm_location.model_dump()

    user_prompt = (
        f"Query: \"{raw_text}\"\n"
        f"Language: {detected_language}\n"
        f"Dialect: {detected_dialect or 'standard'}\n"
        f"Context Hints: {json.dumps(context_hints, ensure_ascii=False)}"
    )

    candidate_providers: List[Dict[str, Any]] = []

    # 1. Primary: OpenRouter
    if settings.openrouter_api_key and not settings.openrouter_api_key.startswith("placeholder"):
        candidate_providers.append({
            "name": "openrouter",
            "url": f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
            "key": settings.openrouter_api_key,
            "model": settings.openrouter_model,
            "headers": {
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://farmfusion.app",
                "X-Title": "FarmFusion",
            }
        })

    # 2. Fallback: Groq
    if settings.groq_api_key and not settings.groq_api_key.startswith("gsk_placeholder"):
        candidate_providers.append({
            "name": "groq",
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key": settings.groq_api_key,
            "model": settings.groq_model or "llama-3.3-70b-versatile",
            "headers": {
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Content-Type": "application/json",
            }
        })

    if not candidate_providers:
        logger.info("llm_extraction_skipped_no_api_keys")
        return None

    for provider in candidate_providers:
        p_name = provider["name"]
        payload = {
            "model": provider["model"],
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                resp = await client.post(provider["url"], headers=provider["headers"], json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    raw_c = content.strip()
                    if raw_c.startswith("```json"):
                        raw_c = raw_c[7:]
                    elif raw_c.startswith("```"):
                        raw_c = raw_c[3:]
                    if raw_c.endswith("```"):
                        raw_c = raw_c[:-3]
                    parsed = json.loads(raw_c.strip())

                    # Normalize and validate into SemanticFrame
                    # 1. Base IDs
                    parsed["request_id"] = req_id
                    parsed["session_id"] = sess_id
                    parsed["raw_text"] = raw_text
                    parsed["normalized_text"] = parsed.get("normalized_text") or clean_text
                    parsed["language"] = detected_language
                    parsed["dialect"] = detected_dialect

                    # 2. Intent mapping
                    parsed["intent"] = map_canonical_intent(parsed.get("intent", ""))

                    # 3. Capabilities mapping
                    raw_caps = parsed.get("required_capabilities", [])
                    valid_caps: List[CapabilityType] = []
                    for c in raw_caps:
                        cap_obj = map_capability_type(str(c))
                        if cap_obj and cap_obj not in valid_caps:
                            valid_caps.append(cap_obj)
                    if not valid_caps:
                        if parsed["intent"] == CanonicalIntent.WEATHER:
                            valid_caps = [CapabilityType.WEATHER]
                        elif parsed["intent"] in (CanonicalIntent.IRRIGATION_ADVISORY, CanonicalIntent.SMART_IRRIGATION):
                            valid_caps = [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION]
                        elif parsed["intent"] in (CanonicalIntent.MANDI_DECISION, CanonicalIntent.SELL_HOLD):
                            valid_caps = [CapabilityType.CURRENT_PRICE, CapabilityType.MANDI_DECISION, CapabilityType.MANDI_FORECAST]
                        elif parsed["intent"] == CanonicalIntent.MANDI_PRICE:
                            valid_caps = [CapabilityType.CURRENT_PRICE]
                        elif parsed["intent"] == CanonicalIntent.MANDI_FORECAST:
                            valid_caps = [CapabilityType.MANDI_FORECAST]
                        elif parsed["intent"] == CanonicalIntent.MANDI_COMPARISON:
                            valid_caps = [CapabilityType.MANDI_COMPARISON]
                        elif parsed["intent"] == CanonicalIntent.DISEASE_DETECTION:
                            valid_caps = [CapabilityType.DISEASE_DETECTION]
                        elif parsed["intent"] == CanonicalIntent.CROP_RECOMMENDATION:
                            valid_caps = [CapabilityType.CROP_RECOMMENDATION]
                        elif parsed["intent"] == CanonicalIntent.DISASTER_RISK:
                            valid_caps = [CapabilityType.DISASTER_RISK]
                        elif parsed["intent"] == CanonicalIntent.CALLING:
                            valid_caps = [CapabilityType.CALLING]
                        elif parsed["intent"] == CanonicalIntent.NAVIGATION_REQUEST:
                            valid_caps = [CapabilityType.NAVIGATION]
                        else:
                            valid_caps = [CapabilityType.RAG_KNOWLEDGE]
                    parsed["required_capabilities"] = valid_caps

                    # 4. Required input mapping
                    raw_req_input = str(parsed.get("required_input", "NONE")).upper()
                    try:
                        parsed["required_input"] = RequiredInput(raw_req_input)
                    except ValueError:
                        parsed["required_input"] = RequiredInput.NONE

                    # 5. EntitySet construction & enrichment
                    ent_data = parsed.get("entities")
                    if not isinstance(ent_data, dict):
                        ent_data = {}

                    # Copy top-level entity fields if LLM emitted them flat
                    for field in ["crop", "disease", "market", "mandi", "markets", "city", "district", "state", "timeframe", "forecast_days"]:
                        if field in parsed and field not in ent_data:
                            ent_data[field] = parsed[field]

                    # Map entity alias fields from LLM
                    if "time" in ent_data and not ent_data.get("timeframe"):
                        ent_data["timeframe"] = ent_data.pop("time")
                    if "date" in ent_data and not ent_data.get("timeframe"):
                        ent_data["timeframe"] = ent_data.pop("date")
                    if "commodity" in ent_data and not ent_data.get("crop"):
                        ent_data["crop"] = ent_data.pop("commodity")
                    if "location" in ent_data:
                        loc_val = ent_data.pop("location")
                        if isinstance(loc_val, str) and not ent_data.get("city"):
                            ent_data["city"] = loc_val

                    cand_crops = getattr(conversation_context, "candidate_crops", []) if conversation_context else []
                    cand_markets = getattr(conversation_context, "candidate_markets", []) if conversation_context else []
                    has_deictic = any(w in clean_text.lower() for w in [
                        "iske liye", "is ke liye", "uske liye", "isko", "इस फसल", "my crop",
                        "this crop", "is fasal", "ye fasal", "is mandi", "iss mandi", "aaj bechna", "mere liye"
                    ])

                    # Ambiguity check for LLM results: multiple candidates without user specification
                    if has_deictic and len(cand_crops) > 1 and not any(c.lower() in clean_text.lower() for c in cand_crops):
                        parsed["intent"] = CanonicalIntent.CLARIFICATION
                        parsed["required_capabilities"] = []
                        if isinstance(parsed.get("confidence"), dict):
                            parsed["confidence"]["intent_confidence"] = 0.50
                            parsed["confidence"]["overall_confidence"] = 0.50

                    # Normalize crop if present
                    if ent_data.get("crop"):
                        norm_c = normalize_crop_name(str(ent_data["crop"]))
                        if norm_c:
                            ent_data["crop"] = norm_c
                    elif conversation_context and conversation_context.active_crop and len(cand_crops) <= 1:
                        # Context inheritance
                        ent_data["crop"] = conversation_context.active_crop

                    # Extract/normalize markets if present
                    mkts = extract_markets(clean_text)
                    if mkts and not ent_data.get("market") and not ent_data.get("markets"):
                        ent_data["market"] = mkts[0]
                        ent_data["markets"] = mkts
                    elif not ent_data.get("market") and not ent_data.get("markets") and conversation_context and conversation_context.active_market and len(cand_markets) <= 1:
                        ent_data["market"] = conversation_context.active_market
                        ent_data["markets"] = [conversation_context.active_market]

                    # Critical Temporal Mapping: Ensure relative days (TOMORROW, TODAY, etc.) are never lost
                    time_info = resolve_time_context(clean_text)
                    if time_info.get("relative_day") != "UNSPECIFIED" or time_info.get("explicit_date"):
                        ent_data["time_context"] = TimeContext.model_validate(time_info)
                        if not ent_data.get("timeframe"):
                            ent_data["timeframe"] = time_info.get("raw_hint") or extract_timeframe(clean_text)
                    elif ent_data.get("timeframe"):
                        ent_time_info = resolve_time_context(str(ent_data["timeframe"]))
                        if ent_time_info.get("relative_day") != "UNSPECIFIED":
                            ent_data["time_context"] = TimeContext.model_validate(ent_time_info)

                    # Location inheritance if missing
                    if not ent_data.get("city") and conversation_context and conversation_context.active_location:
                        ent_data["city"] = conversation_context.active_location
                    elif not ent_data.get("market") and not ent_data.get("city") and user_context and user_context.farm_location:
                        loc = user_context.farm_location
                        ent_data["city"] = loc.city
                        ent_data["district"] = loc.district
                        ent_data["state"] = loc.state

                    # Filter extra fields for EntitySet (extra="forbid")
                    valid_ent_fields = set(EntitySet.model_fields.keys())
                    extra_ent_keys = [k for k in ent_data if k not in valid_ent_fields]
                    add_ents = ent_data.setdefault("additional_entities", {})
                    if not isinstance(add_ents, dict):
                        add_ents = {}
                    for k in extra_ent_keys:
                        val = ent_data.pop(k)
                        if val is not None:
                            add_ents[k] = val
                    ent_data["additional_entities"] = add_ents

                    parsed["entities"] = EntitySet.model_validate(ent_data)

                    # 6. Confidence construction
                    if not parsed.get("confidence") or not isinstance(parsed.get("confidence"), dict):
                        lang_conf = 0.98 if detected_language in ["hi", "en", "pa", "gu", "mr"] else 0.90
                        parsed["confidence"] = ConfidenceSet(
                            language_confidence=lang_conf,
                            intent_confidence=0.92,
                            entity_confidence=0.90,
                            overall_confidence=0.90,
                        )

                    # Final validation filtering against SemanticFrame (extra="forbid")
                    valid_frame_fields = set(SemanticFrame.model_fields.keys())
                    clean_frame_dict = {k: v for k, v in parsed.items() if k in valid_frame_fields}
                    frame = SemanticFrame.model_validate(clean_frame_dict)
                    logger.info("llm_semantic_extraction_success", provider=p_name, intent=frame.intent)
                    return frame
                else:
                    logger.warning("llm_extraction_http_error", provider=p_name, status=resp.status_code)
        except httpx.TimeoutException:
            logger.warning("llm_extraction_timeout", provider=p_name)
        except Exception as e:
            logger.warning("llm_extraction_failed_fallback_triggered", provider=p_name, error=str(e))

    return None


# =============================================================================
# HYBRID PUBLIC EXTRACTOR ENTRYPOINT
# =============================================================================

async def extract_semantic_frame(
    raw_text: str,
    detected_language: str = "hi",
    detected_dialect: Optional[str] = None,
    user_context: Optional[UserContext] = None,
    conversation_context: Optional[ConversationContext] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> SemanticFrame:
    """
    Main entrypoint for Phase F3 Semantic Extraction.
    Attempts LLM semantic extraction first; falls back seamlessly to
    deterministic agricultural extraction if LLM is unavailable, offline, or invalid.
    """
    # 1. Attempt LLM extraction
    llm_frame = await extract_semantic_frame_llm(
        raw_text=raw_text,
        detected_language=detected_language,
        detected_dialect=detected_dialect,
        user_context=user_context,
        conversation_context=conversation_context,
        request_id=request_id,
        session_id=session_id,
    )
    if llm_frame is not None:
        logger.info("semantic_extraction_success", mode="llm", intent=llm_frame.intent)
        return llm_frame

    # 2. Deterministic Fallback
    fallback_frame = extract_semantic_frame_deterministic(
        raw_text=raw_text,
        detected_language=detected_language,
        detected_dialect=detected_dialect,
        user_context=user_context,
        conversation_context=conversation_context,
        request_id=request_id,
        session_id=session_id,
    )
    logger.info("semantic_extraction_success", mode="deterministic_fallback", intent=fallback_frame.intent)
    return fallback_frame
