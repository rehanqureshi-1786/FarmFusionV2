"""
Intent Classification & Slot Extraction Node for LangGraph Orchestrator.
Classifies farmer queries into standard intents, extracts typed slots, and resolves conversational references.
"""
from typing import Any, Dict, List, Optional
import re
import structlog

from app.orchestrator.state import OrchestratorState
from app.voice.languages import normalize_crop_name, normalize_soil_name, detect_dialect, normalize_agricultural_term

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

    # Detect regional dialect & language markers
    dialect_res = detect_dialect(query, detected_language=state.get("detected_language", "hi"))
    if dialect_res.dialect and not state.get("detected_dialect"):
        state["detected_dialect"] = dialect_res.dialect
        state["detected_language"] = dialect_res.language

    # Auto-detect Hindi from Devanagari script or Hinglish vocabulary if client passed "en"
    has_devanagari = bool(re.search(r'[\u0900-\u097F]', query))
    has_hinglish = any(w in query for w in [
        "mausam", "kaisa", "khet", "fasal", "bhai", "aaj", "rate", "bhav", "mandi",
        "gehu", "chawal", "dhan", "kya", "hai", "karo", "batao", "rahega", "karna",
        "lagau", "kharab", "rog", "yojana", "pani", "mitti", "khad", "kisan", "kyon", "kyu", "boye", "salah"
    ])
    if (has_devanagari or has_hinglish) and state.get("detected_language") in ["en", "unknown", None]:
        state["detected_language"] = "hi"

    logger.info("intent_classification_start", query=query, dialect=state.get("detected_dialect"), language=state.get("detected_language"), session_id=state.get("session_id"))

    intent = "unknown"
    confidence = 0.50

    # 1. Consequential / Destructive Action Safety Check
    if any(kw in query for kw in ["डेटा डिलीट", "डिलीट कर", "हटा दो", "खाता बंद", "delete my data", "delete data", "delete crop"]):
        intent = "consequential_action"
        confidence = 0.95
        state["safety_classification"] = "CONSEQUENTIAL"
        state["requires_consequential_confirmation"] = True
        filled_slots["action"] = "delete_data"

    # 2. Greetings, Help & Identity (Exact query match for short words like 'hi' / 'hey' to prevent matching 'delhi')
    elif query in ["hi", "hey", "hello", "namaste", "नमस्ते", "नमस्कार", "हेलो", "राम राम", "खम्मा घणी"] or any(kw in query for kw in [
        "नमस्ते", "नमस्कार", "राम राम", "खम्मा घणी", "hello assistant", "hello farmfusion",
        "तुम कौन हो", "आप कौन हो", "who are you", "क्या कर सकते हो", "what can you do",
        "मदद करो", "सहायता", "help me"
    ]):
        intent = "greeting_help"
        confidence = 0.96

    # 3. Language & Dialect Switching Preferences
    elif any(kw in query for kw in ["हिंदी में बताओ", "हिंदी में बोलो", "in hindi", "hindi me"]):
        intent = "language_preference"
        confidence = 0.96
        filled_slots["target_language"] = "hi"
        state["farmer_preferred_language"] = "hi"
    elif any(kw in query for kw in ["मरवाड़ी में बोलो", "मारवाड़ी में", "मारवाड़ी में बोलो", "marwari me"]):
        intent = "dialect_preference"
        confidence = 0.96
        filled_slots["target_dialect"] = "rwr"
        state["farmer_preferred_dialect"] = "rwr"
    elif any(kw in query for kw in ["अंग्रेजी में", "english me", "in english", "speak in english"]):
        intent = "language_preference"
        confidence = 0.96
        filled_slots["target_language"] = "en"
        state["farmer_preferred_language"] = "en"
    elif any(kw in query for kw in ["गुजराती में", "gujarati me", "in gujarati"]):
        intent = "language_preference"
        confidence = 0.96
        filled_slots["target_language"] = "gu"
        state["farmer_preferred_language"] = "gu"

    # 3. Unsupported Capabilities (Strict Priority Check)
    elif any(kw in query for kw in ["खरीद", "order", "आर्डर", "buy", "purchase", "यूरिया मंगा", "यूरिया आर्डर", "पेमेंट", "पैसे भेज", "मंगा दो"]):
        intent = "unsupported_capability"
        confidence = 0.95
        filled_slots["capability_type"] = "purchase"
    elif any(kw in query for kw in ["आवेदन कर दो", "फॉर्म भर दो", "apply for scheme", "सबमिट कर दो", "रजिस्टर कर दो", "फॉर्म भर"]):
        intent = "unsupported_capability"
        confidence = 0.95
        filled_slots["capability_type"] = "scheme_application"

    # 4. In-App Navigation Intent (Strict Priority for "खोलो", "स्क्रीन", "पेज")
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

    # 5. Repeat Last Response: "फिर से बताओ", "दोबारा बोलो", "repeat that"
    elif any(p in query for p in ["फिर से बताओ", "दोबारा बोलो", "repeat", "फिर बताओ", "वो वाली कीमत फिर से", "बात दोबारा", "say again", "once more"]):
        intent = "repeat_last"
        confidence = 0.98

    # 6. Speech Rate Control: "धीरे बोलो", "speak slowly"
    elif any(p in query for p in ["धीरे बोलो", "धीमे बोलो", "slowly", "speak slowly", "आराम से बोलो"]):
        intent = "speech_control"
        confidence = 0.95
        filled_slots["speech_rate"] = "slow"

    # 7. Follow-Up Anaphora: "पहली वाली क्यों?", "वो पहली वाली फसल क्यों अच्छी है?"
    elif any(p in query for p in ["पहली वाली क्यों", "पहला क्यों", "why top", "why first", "पहली फसल क्यों", "क्यों चुनी", "why this crop", "पहली वाली फसल क्यों", "पहली वाली फसल"]):
        intent = "explain_recommendation"
        confidence = 0.95
        filled_slots["target_index"] = 0
    elif any(p in query for p in ["दूसरी वाली क्यों", "दूसरा क्यों", "why second", "दूसरी फसल क्यों", "दूसरी वाली"]):
        intent = "explain_recommendation"
        confidence = 0.95
        filled_slots["target_index"] = 1

    # 8. "What-if" Counterfactual: "अगर बारिश कम हो जाए तो?", "अगर पानी कम मिले तो?"
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

    # 9. Crop Disease / Pest / Leaf Health Intent (with leaf photo redirect guidance)
    elif any(kw in query for kw in [
        "कीड़े", "कीड़ा", "कीट", "कीड़े लगे", "कीट लगे", "लगे हैं", "बीमारी", "रोग", "पत्ते", "पत्ता", "पत्ता खराब", "पत्ते खराब",
        "पीले पत्ते", "सूख रहे", "धब्बे", "इल्ली", "माहू", "दीमक", "फफूंद", "फंगस", "सुंडी", "मच्छर", "पौधे में क्या लगा", "पौधे में",
        "दवा", "कीटनाशक", "दवाई", "स्प्रे", "उपचार", "रोकथाम", "photo", "फोटो", "स्कैन", "disease", "pest", "leaf", "fungus", "spots", "insect", "worm",
        "keede", "kida", "bimari", "rog", "patta kharab", "illey", "mahu", "kitnashak", "दावा", "நோய்", "ರೋಗ", "രോഗം", "କୀଟ"
    ]):
        intent = "disease"
        confidence = 0.94
        if any(w in query for w in ["इसमें", "इस फसल", "in this"]) and last_recs:
            filled_slots["crop_name"] = last_recs[0].get("crop_name")
            filled_slots["query_crop_or_disease"] = last_recs[0].get("crop_name")
        else:
            filled_slots["query_crop_or_disease"] = query

    # 10. Crop Care & Fertilizer Timing: "धान की देखभाल कैसे करूं?", "खाद कब डालनी है?", "ধান ফসলে সার কখন দিতে হবে?", "വിള പരിപാലനം എങ്ങനെ ചെയ്യാം?"
    elif any(kw in query for kw in [
        "देखभाल", "खाद कब", "उर्वरक", "सिंचाई कब", "सिंचाई", "पानी कब", "पानी देना",
        "स्प्रे कब", "पोषण", "care", "fertilizer timing", "how to grow", "cultivation",
        "dekhbhal", "khad kab", "pani kab", "সার", "কখন দিতে", "সার কখন", "সার প্রয়োগ", "পরিচর্যা",
        "പരിപാലനം", "എങ്ങനെ ചെയ്യാം", "പരിചരണം", "വളം", "ജലസേചനം", "ಯಾವಾಗ"
    ]):
        intent = "crop_care"
        confidence = 0.94
        matched_crop = None
        for c_word in ["धान", "गेहूं", "कपास", "सरसों", "चना", "सोयाबीन", "मक्का", "मूंगफली", "बाजरा", "गन्ना", "लहसुन", "प्याज", "टमाटर", "rice", "wheat", "cotton", "mustard", "groundnut", "bajra", "maize", "soybean", "garlic", "onion", "tomato", "ভাত", "கோதுமை", "ಬೆಳೆ", "ধান"]:
            if c_word in query:
                matched_crop = normalize_crop_name(c_word)
                break
        filled_slots["crop_name"] = matched_crop or (last_recs[0].get("crop_name") if last_recs else "Wheat")

    # 11. Crop Recommendation Intent (Broad agricultural phrasing, soil mentions, seasonal sowing)
    elif any(kw in query for kw in [
        "कौन सी फसल", "फसल की सलाह", "फसल सलाह", "सलाह दो", "सलाह", "recommend", "which crop", "sow", "बुवाई", "बोना", "बोएं", "बोऊं", "बॉय", "बोए", "बोऊ",
        "लगाएं", "लगाऊं", "लगाए", "लगाना", "उपयुक्त फसल", "खेत में क्या", "क्या लगाऊं", "क्या बोएं", "के बोऊं", "बोईब", "बोईं", "बोवई", "खेती",
        "काली मिट्टी", "रेतीली मिट्टी", "लाल मिट्टी", "दोमट मिट्टी", "चिकनी मिट्टी", "मिट्टी में क्या", "अभी के टाइम", "इस मौसम में", "टाइम पर",
        "what to grow", "what to plant", "kya boye", "kya lagaye", "khet me kya", "fasal ki salah", "fasal salah", "salah do",
        "पीक", "शेतात", "पाक", "પાક", "কোন ফসল", "কি ফসল", "ফসল চাষ", "ভালো ফসল", "ఏ పంట", "ఎలాంటి పంట", "எந்த பயிர்", "ಯಾವ ಬೆಳೆ", "ഏത് വിള", "അനുയോജ്യമായ വിള", "କେଉଁ ଫସଲ", "খেতি", "فصل"
    ]):
        intent = "crop_recommendation"
        confidence = 0.95
        for s_word in ["रेतीली", "sandy", "काली", "black", "लाल", "red", "दोमट", "alluvial", "चिकनी", "clay", "बलुई", "रेगुर", "मटियारी", "काली मिट्टी", "रेतीली मिट्टी", "लाल मिट्टी", "दोमट मिट्टी", "चिकनी मिट्टी", "black soil", "sandy soil", "red soil", "clay soil", "alluvial soil", "kali mitti", "retili mitti", "lal mitti", "domat mitti", "chikni mitti", "ମାଟି", "മണ്ണ്", "మట్టి", "மண்", "മಣ್ಣು"]:
            if s_word in query:
                filled_slots["soil_type"] = normalize_soil_name(s_word)
                break

    # 12. Mandi / Market Prices Intent (Multi-lingual: Gujarati 'ભાવ', Punjabi 'ਕੀਮਤ', Telugu 'ధర', Tamil 'விலை', Kannada 'ಬೆಲೆ', Malayalam 'വില', Odia 'ଦର', Urdu 'قیمत')
    elif any(kw in query for kw in [
        "मंडी", "भाव", "कीमत", "दाम", "price", "mandi", "rate", "market", "रेट", "दर", "चल रहा", "क्या रेट", "क्या भाव", "कितना है",
        "bhav", "mandi bhav", "market rate", "kitna hai", "kya rate", "bhav kya",
        "ભાવ", "શું છે", "ਕੀਮਤ", "ధర", "விலை", "ಬೆಲೆ", "വില", "ଦର", "قیمत", "گندم", "দাম"
    ]):
        intent = "mandi"
        confidence = 0.94
        if any(w in query for w in ["इसका", "इस फसल", "it", "this crop", "उसका भाव", "దీని ధర", "இதன் விலை"]) and last_recs:
            filled_slots["commodity"] = last_recs[0].get("crop_name", "Wheat")
        else:
            for c_word in ["गेहूं", "धान", "चावल", "सरसों", "कपास", "चना", "सोयाबीन", "मक्का", "मूंगफली", "बाजरा", "लहसुन", "प्याज", "टमाटर", "गन्ना", "wheat", "mustard", "cotton", "rice", "soybean", "gram", "maize", "groundnut", "bajra", "chana", "sugarcane", "onion", "potato", "garlic", "tomato", "gehu", "dhan", "chawal", "sarso", "kapas", "chana", "soyabean", "makka", "mungfali", "bajra", "lahsun", "pyaz", "tamatar", "ghau", "kanak", "vari", "paruthi", "ઘઉં", "ਕਣਕ", "వరి", "பருத்தி", "گندم"]:
                if c_word in query:
                    filled_slots["commodity"] = normalize_crop_name(c_word) or "Wheat"
                    break

    # 13. Weather Intent (Multi-lingual: Hindi, Punjabi 'ਮੌਸਮ', Marathi 'हवामान', Gujarati 'વાતાવરણ', Bengali 'আবহাওয়া', Telugu 'వాతావరణం', Tamil 'வானிலை', Kannada 'ಹವಾಮಾನ', Malayalam 'കാലാവസ്ഥ', Odia 'ପାଣିପାଗ', Assamese 'বতৰ', Urdu 'موسم')
    elif any(kw in query for kw in [
        "मौसम", "बारिश", "तापमान", "पानी गिरेगा", "वर्षा", "धूप", "बादल", "आंधी", "हवा", "weather", "rain", "temperature", "forecast", "climate",
        "mausam", "barish", "pani girega", "tapman", "badal", "हवामान", "પાણી", "વાતાવરણ", "ਮੌਸਮ", "ਕਿਵੇਂ", "আবহাওয়া", "వాతావరణం", "வானிலை", "ಹವಾಮಾನ", "കാലാവസ്ഥ", "ପାଣିପାଗ", "বতৰ", "موسم"
    ]):
        intent = "weather"
        confidence = 0.95
        city_lookup = {
            "jaipur": "Jaipur", "जयपुर": "Jaipur",
            "udaipur": "Udaipur", "उदयपुर": "Udaipur",
            "jodhpur": "Jodhpur", "जोधपुर": "Jodhpur",
            "kota": "Kota", "कोटा": "Kota",
            "nagaur": "Nagaur", "नागौर": "Nagaur",
            "delhi": "Delhi", "दिल्ली": "Delhi",
            "patna": "Patna", "पटना": "Patna",
            "lucknow": "Lucknow", "लखनऊ": "Lucknow",
            "bhopal": "Bhopal", "भोपाल": "Bhopal",
            "ahmedabad": "Ahmedabad", "अहमदाबाद": "Ahmedabad", "અમદાવાદ": "Ahmedabad",
            "kolkata": "Kolkata", "कोलकाता": "Kolkata", "কলকাতা": "Kolkata",
            "chennai": "Chennai", "चेन्नई": "Chennai", "சென்னை": "Chennai",
            "hyderabad": "Hyderabad", "हैदराबाद": "Hyderabad", "హైదరాబాద్": "Hyderabad",
            "bengaluru": "Bengaluru", "बेंगलुरु": "Bengaluru",
            "kochi": "Kochi", "कोच्चि": "Kochi",
            "guwahati": "Guwahati", "गुवाहाटी": "Guwahati",
            "bhubaneswar": "Bhubaneswar", "भुवनेश्वर": "Bhubaneswar",
            "pune": "Pune", "पुणे": "Pune",
        }
        for city_token, canonical_city in city_lookup.items():
            if city_token in query:
                filled_slots["location_name"] = canonical_city
                break

    # 14. Government Schemes Intent (Multi-lingual: Kannada 'ಯೋಜನೆ', Tamil 'திட்டம்', Telugu 'పథకం', Bengali 'প্রকল্প')
    elif any(kw in query for kw in ["योजना", "पीएम किसान", "बीमा", "सब्सिडी", "scheme", "pm-kisan", "subsidies", "सरकारी", "मदद", "ಯೋಜನೆ", "திட்டம்", "పథకం", "প্রকল্প"]):
        intent = "scheme"
        confidence = 0.94
        filled_slots["query"] = query

    # 15. General Farming Query Fallback (Intelligent agricultural understanding rather than asking to repeat)
    elif any(kw in query for kw in ["खेती", "फसल", "पौधा", "पेड़", "जमीन", "मिट्टी", "खाद", "पानी", "बीज", "कीटनाशक", "कृषि", "farming", "crop", "plant", "soil", "kisan"]):
        intent = "crop_care"
        confidence = 0.90
        filled_slots["crop_name"] = (last_recs[0].get("crop_name") if last_recs else "Wheat")

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
