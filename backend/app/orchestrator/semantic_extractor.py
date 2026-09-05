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
    crop = normalize_crop_name(clean_text)
    markets = extract_markets(clean_text)
    primary_market = markets[0] if len(markets) == 1 else None
    forecast_days = extract_forecast_days(clean_text)
    timeframe = extract_timeframe(clean_text)
    soil_type = normalize_soil_type(clean_text)

    # 2. Multi-turn context inheritance
    deictic_crop_markers = [
        "इस फसल", "यह फसल", "ये फसल", "इसकी", "इसका", "इसमें", "my crop", "the crop",
        "this crop", "is fasal", "ye fasal", "meri fasal", "hamari fasal", "apni fasal",
        "is crop", "that crop", "it", "itna", "iski", "iska", "dekhbhal", "देखभाल"
    ]
    has_deictic_crop = any(w in lower_text for w in [
        "इस फसल", "यह फसल", "ये फसल", "इसकी", "इसका", "my crop", "the crop",
        "this crop", "is fasal", "ye fasal", "meri fasal", "hamari fasal", "apni fasal",
        "is crop", "that crop"
    ])

    if crop is None and conversation_context and conversation_context.active_crop:
        # Check if the query uses anaphora like "इसमें", "इस फसल", "इसकी", "it", "this crop"
        if any(w in lower_text for w in deictic_crop_markers):
            crop = conversation_context.active_crop
        elif not any(w in lower_text for w in ["फसल", "crop", "कौन सी"]):
            # Follow-up turn inheriting previous crop (e.g. Turn 1: "Gehu ka bhav", Turn 2: "Jaipur mein")
            crop = conversation_context.active_crop

    # 3. Location context inheritance
    primary_city = primary_market
    primary_district = None
    primary_state = None
    if not primary_market and user_context and user_context.farm_location:
        loc = user_context.farm_location
        primary_city = loc.city
        primary_district = loc.district
        primary_state = loc.state

    # 4. Intent & Required Capability Detection
    required_capabilities: List[CapabilityType] = []
    required_input = RequiredInput.NONE
    sub_intent: Optional[str] = None

    # Keyword bundles
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
        "farmer ko call", "किसान को फोन", "किसान को कॉल"
    ])
    is_weather_kw = any(w in lower_text for w in [
        "मौसम", "weather", "बारिश", "rain", "तापमान", "temperature", "वर्षा",
        "बादल", "हवामान", "વાતાવરણ", "વરસાદ", "ਮੌਸਮ", "ਮੀਂਹ", "আবহাওয়া", "বৃষ্টি",
        "வானிலை", "மழை", "వాతావరణం", "వర్షం", "ಹವಾಮಾನ", "ಮಳೆ", "കാലാവസ്ഥ",
        "mausam", "barish", "pani girega", "paus", "varsad", "brishti", "havaman", "धूप", "हवा",
        "badal", "badlo", "dhoop", "andhi", "hawa", "fog", "kohra", "barsat", "tapan", "garmi", "sardi", "megh"
    ])
    is_irrigation_kw = any(w in lower_text for w in [
        "सिंचाई", "irrigation", "irrigate", "पानी देना", "पानी देने", "पानी दूं", "water", "pani doon",
        "पानी लगाऊं", "सिंचना", "water stress", "moisture", "પાણી આપવું", "પાણી પાવું", "water karun",
        "પાણી ક્યારે", "geeli", "geela", "sukhi", "sukha", "nami", "paani rok", "pani band", "paani band",
        "paani kab du", "kab paani", "paani lagayein", "pani kab", "pani dena"
    ])
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
        "patte sukh rahe", "sukhte patte", "murjha", "disease kaise"
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
        "kaunsi fasal theek rahegi", "konsi fasal theek", "mere khet ke hisaab se", "kaunsi kheti"
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
        "neeche ja raha", "gir raha", "rukna sahi hoga", "bechna sahi hoga", "wait karein ya sell", "rukna chahiye", "kya rukna", "sahi time bechne ka"
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

    # 1. Repeat Last Response
    if is_repeat_kw:
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

    # 4. Compound: Irrigation Advisory (Weather + Soil Moisture)

    elif is_irrigation_kw and is_weather_kw:
        intent = CanonicalIntent.IRRIGATION_ADVISORY
        required_capabilities = [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION]
        intent_confidence = 0.95
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

RULES:
1. Output ONLY valid JSON conforming to the SemanticFrame schema. No conversational preamble.
2. NEVER calculate numbers, predict prices, estimate weather, or diagnose diseases. You only EXTRACT what the farmer meant.
3. If the farmer asks about plant diseases, pests, or leaf damage without attaching an image, set required_input="LEAF_IMAGE".
4. For multi-part queries (e.g. "rain tomorrow, should I irrigate wheat?"), detect compound capabilities: ["WEATHER", "SMART_IRRIGATION"].
5. For market decisions (e.g. "sell in Jaipur or Kalapipal, what rate next 7 days?"), detect capabilities: ["CURRENT_PRICE", "MANDI_COMPARISON", "MANDI_FORECAST", "MANDI_DECISION"].
6. Unknown entities must be null. Never invent fake crops or locations.
7. Normalize crop names to English (e.g. gehu -> "Wheat", pyaaz -> "Onion", dhan -> "Paddy", kapas -> "Cotton").
"""


async def extract_semantic_frame_llm(
    raw_text: str,
    detected_language: str = "hi",
    detected_dialect: Optional[str] = None,
    user_context: Optional[UserContext] = None,
    conversation_context: Optional[ConversationContext] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    timeout_seconds: float = 3.5,
) -> Optional[SemanticFrame]:
    """
    Invokes configured LLM provider (OpenRouter or Groq) to extract SemanticFrame.
    Returns None if LLM is unavailable, times out, or returns invalid schema.
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    # Check if a valid non-placeholder key is present
    api_key = None
    api_url = None
    model_name = None

    if openrouter_key and not openrouter_key.startswith("placeholder"):
        api_key = openrouter_key
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        model_name = "google/gemma-3-12b-it"
    elif groq_key and not groq_key.startswith("gsk_placeholder"):
        api_key = groq_key
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    else:
        # No cloud LLM configured
        return None

    # Build prompt payload
    context_hints = {}
    if conversation_context and conversation_context.active_crop:
        context_hints["active_crop"] = conversation_context.active_crop
    if user_context and user_context.farm_location:
        context_hints["default_location"] = user_context.farm_location.model_dump()

    user_prompt = f"Query: \"{raw_text}\"\nLanguage: {detected_language}\nDialect: {detected_dialect or 'standard'}\nContext: {json.dumps(context_hints)}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            resp = await client.post(api_url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                # Inject missing IDs and validated fields
                parsed["request_id"] = request_id or f"req_{uuid.uuid4().hex[:8]}"
                parsed["session_id"] = session_id or "default_session"
                parsed["raw_text"] = raw_text
                parsed["normalized_text"] = parsed.get("normalized_text") or raw_text
                parsed["language"] = detected_language
                parsed["dialect"] = detected_dialect

                return SemanticFrame.model_validate(parsed)
            else:
                logger.warning("llm_extraction_http_error", status=resp.status_code)
                return None
    except Exception as e:
        logger.warning("llm_extraction_failed_fallback_triggered", error=str(e))
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
