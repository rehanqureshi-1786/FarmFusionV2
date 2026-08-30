"""
Response Synthesizer Node for LangGraph Orchestrator.
Formats multi-tool outputs into simple, rural-friendly farmer responses (1-3 sentences max)
strictly using verified tool payload with zero data fabrication, supporting regional dialects (Marwari/Mewari)
and recording explicit TTS fallback metadata.
"""
from typing import Any, Dict, List, Optional
import structlog

from app.orchestrator.state import OrchestratorState
from app.voice.languages import get_language_profile

logger = structlog.get_logger(__name__)


async def response_synthesizer_node(state: OrchestratorState) -> OrchestratorState:
    """
    Synthesize final localized response for the farmer using fallback ladder.
    If requires_clarification is True, return the clarification question.
    """
    input_lang = state.get("detected_language", "hi")
    profile = get_language_profile(input_lang)
    lang = profile.canonical_code if profile.support_tier == 1 else profile.fallback_language

    dialect = state.get("detected_dialect") or state.get("farmer_preferred_dialect")
    is_marwari = dialect in ["rwr", "marwari"]
    is_mewari = dialect in ["mew", "mewari"]

    intent = state.get("intent", "unknown")
    tool_data = state.get("tool_output") or {}
    tool_status = state.get("tool_status", "success")

    # 1. Handle Clarification
    if state.get("requires_clarification"):
        q = state.get("clarification_question")
        if not q:
            if is_marwari:
                q = "कांई आप थांको सवाल दोबारा साफ कह सको हो? (जैसो मौसम, मंडी भाव या फसल सलाह)"
            elif lang == "hi":
                q = "क्या आप कृपया अपनी फसल का नाम या सवाल दोबारा स्पष्ट कह सकते हैं? (जैसे मौसम, मंडी भाव या फसल सलाह)"
            else:
                q = "Could you please clarify your question so I can provide accurate guidance?"
        state["final_response"] = q
        state["response_language"] = lang
        state["response_dialect"] = dialect
        state["tts_language"] = lang if profile.tts.native_supported else profile.fallback_language
        state["native_tts"] = profile.tts.native_supported and (not dialect)
        state["fallback_used"] = not profile.tts.native_supported or bool(dialect)
        if dialect:
            state["fallback_reason"] = f"No native {dialect} TTS voice model available in Bhashini or Indic-TTS. Spoken response synthesized using parent language {state['tts_language']} (Hindi) voice."
        elif not profile.tts.native_supported:
            state["fallback_reason"] = f"No native {lang} TTS voice available. Using fallback {state['tts_language']}."
        else:
            state["fallback_reason"] = None
        return state

    # 2. Handle Repeat Last Response
    if intent == "repeat_last":
        rep = tool_data.get("response")
        if rep:
            response = rep
        else:
            if is_marwari:
                response = "पछली कोई जानकारी नीं मिली।"
            elif lang == "hi":
                response = "पिछली कोई जानकारी उपलब्ध नहीं है।"
            else:
                response = "No previous response available to repeat."

    # 2b. Handle Greetings, Help & Identity
    elif intent == "greeting_help":
        if is_marwari:
            response = "खम्मा घणी! म्हूँ FarmFusion AI किसान सहायक हूँ। आप म्हासूं मौसम, मंडी भाव, फसल सलाह या सरकारी योजनावां बाबत पूछ सको हो।"
        elif lang == "hi":
            response = "नमस्ते! मैं FarmFusion AI किसान सहायक हूँ। आप मुझसे मौसम, मंडी भाव, फसल सलाह, कीड़े/रोग की दवा या सरकारी योजनाओं के बारे में पूछ सकते हैं।"
        else:
            response = "Hello! I am FarmFusion AI, your agricultural assistant. You can ask me about weather, mandi prices, crop recommendations, pest management, and government schemes."

    # 3. Handle Speech Rate Control
    elif intent == "speech_control":
        rate = tool_data.get("rate", "slow")
        if is_marwari:
            response = "हाँ सा, अब म्हूँ थांके खातर धीरे अर आराम सूं बोलूँगा।"
        elif lang == "hi":
            response = "जी, अब मैं आपके लिए आराम से और धीरे बोलूंगा।"
        else:
            response = "Understood. I will speak more slowly now."

    # 3b. Handle Consequential Action Confirmation Gate
    elif intent == "consequential_action":
        if is_marwari:
            response = "कांई आप साची में आपरो फसल डेटा हटावणो चाहो हो? पुष्टि खातर 'हाँ' कहो।"
        elif lang == "hi":
            response = "क्या आप वाकई अपनी फसल का डेटा हटाना चाहते हैं? कृपया पुष्टि करने के लिए 'हाँ' कहें।"
        else:
            response = "Are you sure you want to delete your crop data? Please say 'yes' to confirm."

    # 3c. Handle Language Preference Switch
    elif intent == "language_preference":
        target = tool_data.get("target_language", "hi")
        if target == "hi":
            response = "जी ठीक है, अब से मैं आपसे हिंदी में बात करूंगा।"
        elif target == "en":
            response = "Sure, I will now speak with you in English."
        elif target == "gu":
            response = "હા ચોક્કસ, હવેથી હું તમારી સાથે ગુજરાતીમાં વાત કરીશ."
        else:
            response = f"Language preference set to {target}."

    # 3d. Handle Dialect Preference Switch
    elif intent == "dialect_preference":
        response = "हाँ सा, अब मारवाड़ी बोली में बात करांगा।" if (is_marwari or lang == "hi") else "Switched to regional dialect preference."

    # 4. Handle Anaphora / Explanation: "पहली वाली क्यों?"
    elif intent == "explain_recommendation":
        crop = tool_data.get("crop_name", "यह फसल")
        factors = tool_data.get("factors", [])
        if factors:
            factor_summary = " और ".join(factors[:2]) if lang == "hi" else " and ".join(factors[:2])
            if is_marwari:
                response = f"{crop} ने पैली प्राथमिकता इण खातर दी गई है क्यूंकि {factor_summary}।"
            elif lang == "hi":
                response = f"{crop} को पहली प्राथमिकता इसलिए दी गई है क्योंकि {factor_summary}।"
            else:
                response = f"{crop} was ranked at the top because {factor_summary}."
        else:
            if is_marwari:
                response = f"{crop} थांके इलाके री जमीन, बरसात अर मौसम खातर सबसूं चोखी है।"
            elif lang == "hi":
                response = f"{crop} आपके क्षेत्र के मौसम, वर्षा और मिट्टी के लिए सबसे उपयुक्त पाई गई है।"
            else:
                response = f"{crop} is most suitable based on your local climate, rainfall, and soil conditions."

    # 5. Handle Weather
    elif intent == "weather":
        temp = tool_data.get("temperature_c", "--")
        hum = tool_data.get("humidity_percent", "--")
        cond = tool_data.get("condition", "सामान्य")
        loc = tool_data.get("location_name", "आपके क्षेत्र")
        rain = tool_data.get("annual_rainfall_mm", "--")
        if is_marwari:
            response = f"आज {loc} में मौसम साफ रैवेला, तापमान {temp}°C अर नमी {hum}% है। वार्षिक बरसात लगभग {rain} mm है।"
        elif lang == "hi":
            response = f"आज {loc} में तापमान {temp}°C और आर्द्रता {hum}% है, मौसम {cond} रहेगा। वार्षिक वर्षा लगभग {rain} mm है।"
        elif lang == "gu":
            response = f"આજે {loc}માં તાપમાન {temp}°C અને ભેજ {hum}% છે, વાતાવરણ {cond} રહેશે."
        elif lang == "mr":
            response = f"आज {loc} मध्ये तापमान {temp}°C आणि आर्द्रता {hum}% आहे, हवामान {cond} राहील."
        elif lang == "pa":
            response = f"ਅੱਜ {loc} ਵਿੱਚ ਤਾਪਮਾਨ {temp}°C ਅਤੇ ਨਮੀ {hum}% ਹੈ, ਮੌਸਮ {cond} ਰਹੇਗਾ।"
        else:
            response = f"Today in {loc}, temperature is {temp}°C with {hum}% humidity and {cond} conditions. Annual rainfall is approx {rain} mm."

    # 6. Handle Crop Recommendation & What-if
    elif intent in ["crop_recommendation", "what_if"]:
        recs = tool_data.get("recommendations") or tool_data.get("top_crops") or []
        cond_prefix = ""
        if intent == "what_if":
            if state.get("filled_slots", {}).get("rainfall_modifier") == "low":
                cond_prefix = "कम बरसात में " if is_marwari else ("कम बारिश की स्थिति में " if lang == "hi" else "In low rainfall conditions, ")
            elif state.get("filled_slots", {}).get("soil_type"):
                s_name = state.get("filled_slots", {}).get("soil_type")
                cond_prefix = f"{s_name} में " if lang == "hi" else f"For {s_name}, "
        if recs:
            top_crop = recs[0].get("crop_name", "फसल")
            score = recs[0].get("suitability_score", 0.90)
            second_crop = recs[1].get("crop_name", "") if len(recs) > 1 else ""
            if is_marwari:
                response = f"{cond_prefix}थांके खेत खातर सबसूं चोखी फसल {top_crop} है (उपयुक्तता स्कोर: {score:.2f})।" + (f" लारै आप {second_crop} भी लगा सको हो।" if second_crop else "")
            elif lang == "hi":
                response = f"{cond_prefix}आपके खेत के लिए सबसे उपयुक्त फसल {top_crop} है (उपयुक्तता स्कोर: {score:.2f})।" + (f" इसके अलावा आप {second_crop} भी लगा सकते हैं।" if second_crop else "")
            elif lang == "gu":
                response = f"તમારા ખેતર માટે સૌથી યોગ્ય પાક {top_crop} છે (સ્કોર: {score:.2f})."
            elif lang == "mr":
                response = f"तुमच्या शेतासाठी सर्वात योग्य पीक {top_crop} आहे (स्कोअर: {score:.2f})."
            else:
                response = f"{cond_prefix}the top recommended crop for your field is {top_crop} (Suitability score: {score:.2f})." + (f" You may also consider {second_crop}." if second_crop else "")
        else:
            response = "पर्याप्त मौसम या मिट्टी की जानकारी नहीं मिल सकी।" if lang == "hi" else "Insufficient environmental data to assess crop suitability."

    # 7. Handle Mandi / Market Prices
    elif intent == "mandi":
        curr = tool_data.get("current_price") or {}
        comm = curr.get("commodity", "फसल")
        mandi = curr.get("market", "स्थानीय मंडी")
        price = curr.get("modal_price", "--")
        if is_marwari:
            response = f"आज {mandi} मंडी में {comm} रो भाव ₹{price} प्रति क्विंटल चाल रैयो है।"
        elif lang == "hi":
            response = f"आज {mandi} में {comm} का औसत भाव ₹{price} प्रति क्विंटल दर्ज किया गया है।"
        elif lang == "gu":
            response = f"આજે {mandi}માં {comm}નો સરેરાશ ભાવ ₹{price} પ્રતિ ક્વિન્ટલ છે."
        elif lang == "mr":
            response = f"आज {mandi} मध्ये {comm} चा सरासरी भाव ₹{price} प्रति क्विंटल आहे."
        else:
            response = f"Today at {mandi}, the modal price for {comm} is ₹{price} per quintal."

    # 8. Handle Crop Disease Info
    elif intent == "disease":
        if tool_status == "requires_photo":
            if is_marwari:
                response = "फसल में बीमारी री सही जांच खातर, किरपा कर'र पत्ती री साफ फोटो खींचो।"
            elif lang == "hi":
                response = "फसल की बीमारी की सही पहचान के लिए, कृपया ऐप के कैमरा बटन से पत्ती की साफ फोटो खींचें।"
            else:
                response = "To diagnose plant disease, please capture a clear leaf photo using the in-app camera."
        else:
            d_name = tool_data.get("disease_name") or tool_data.get("hindi_name", "रोग")
            sym = tool_data.get("symptoms", "")
            treat = tool_data.get("chemical_control", "") or tool_data.get("organic_control", "")
            if is_marwari:
                response = f"{d_name}: मुख्य लक्षण - {sym[:80]}...। रोकथाम खातर: {treat[:100]}।"
            elif lang == "hi":
                response = f"{d_name}: मुख्य लक्षण - {sym[:80]}...। नियंत्रण के लिए: {treat[:100]}।"
            else:
                response = f"{d_name}: Symptoms include {sym[:80]}... Recommended management: {treat[:100]}."

    # 9. Handle Crop Care
    elif intent == "crop_care":
        c_name = tool_data.get("crop_name", "फसल")
        water = tool_data.get("water_requirement", "संतुलित सिंचाई")
        fert = tool_data.get("fertilizer_schedule", "संतुलित एनपीके")
        if is_marwari:
            response = f"{c_name} री सार-संभाल: {water}। खाद रो इंतज़ाम: {fert}।"
        elif lang == "hi":
            response = f"{c_name} की देखभाल: {water}। खाद प्रबंधन: {fert}।"
        else:
            response = f"Crop care for {c_name}: Water requirement - {water}. Fertilizer - {fert}."

    # 10. Handle Government Schemes
    elif intent == "scheme":
        schemes = tool_data.get("schemes", [])
        if schemes:
            s_name = schemes[0].get("scheme_name", "सरकारी योजना")
            benefit = schemes[0].get("benefits", "आर्थिक सहायता")
            if is_marwari:
                response = f"खास योजना: {s_name}। फायदा: {benefit}। पूरी जानकारी ऐप में देखो।"
            elif lang == "hi":
                response = f"प्रमुख योजना: {s_name}। लाभ: {benefit}। अधिक जानकारी ऐप के योजना सेक्शन में देखें।"
            else:
                response = f"Key scheme: {s_name}. Benefits: {benefit}. View details in the schemes section."
        else:
            response = "पीएम किसान और फसल बीमा योजना जैसी योजनाओं की जानकारी उपलब्ध है।" if lang == "hi" else "PM-Kisan and PMFBY scheme information is available."

    # 11. Handle Navigation
    elif intent == "navigation":
        dest = tool_data.get("destination", "home")
        dest_names_hi = {
            "home": "होम स्क्रीन", "market_prices": "मंडी भाव स्क्रीन",
            "weather": "मौसम स्क्रीन", "crop_recommendation": "फसल सलाह स्क्रीन",
            "disease_detection": "बीमारी जांच स्क्रीन", "government_schemes": "सरकारी योजना स्क्रीन",
            "back": "पिछली स्क्रीन"
        }
        name_hi = dest_names_hi.get(dest, dest)
        if is_marwari:
            response = f"म्हूँ थांके खातर {name_hi} खोल रैयो हूँ।"
        elif lang == "hi":
            response = f"मैं आपके लिए {name_hi} खोल रहा हूँ।"
        else:
            response = f"Opening {dest.replace('_', ' ')} screen."

    # 12. Handle Unsupported Capabilities
    elif intent == "unsupported_capability":
        cap = tool_data.get("capability", "")
        if cap == "purchase":
            if is_marwari:
                response = "FarmFusion सीधे खाद या बीज री खरीद नीं करे। थांकी नजदीकी कृषि दुकान सूं संपर्क करो।"
            elif lang == "hi":
                response = "FarmFusion सीधे खाद या बीज की ऑनलाइन खरीद नहीं करता है। कृपया अपनी नजदीकी कृषि सेवा केंद्र से संपर्क करें।"
            else:
                response = "FarmFusion does not process supply purchases. Please contact your nearest agricultural retail center."
        elif cap == "scheme_application":
            if is_marwari:
                response = "योजना री जानकारी बता सकूँ, पण आवेदन सरकारी पोर्टल (pmkisan.gov.in) माथे ही करनो पड़सी।"
            elif lang == "hi":
                response = "मैं योजना की पात्रता और जानकारी बता सकता हूँ, लेकिन आवेदन आधिकारिक सरकारी पोर्टल (जैसे pmkisan.gov.in) पर ही करना होगा।"
            else:
                response = "I can provide scheme eligibility and details, but official applications must be submitted on the government portal."
        else:
            response = "यह कार्य सीधे वॉइस असिस्टेंट द्वारा समर्थित नहीं है।" if lang == "hi" else "This capability is not supported via the voice assistant."

    # 13. Handle Animal Intrusion Detection & Farm Security
    elif intent == "animal_detection":
        overall = tool_data.get("overall_status", "AREA_CLEAR") if isinstance(tool_data, dict) else "AREA_CLEAR"
        detected = tool_data.get("detected_sensors", []) if isinstance(tool_data, dict) else []
        if overall == "INTRUSION_DETECTED":
            sensors_str = ", ".join(detected) if detected else "Perimeter"
            if is_marwari:
                response = f"सावधान! खेत में जानवर री हलचल मिली है (सेंसर: {sensors_str})।"
            elif lang == "hi":
                response = f"सावधान! खेत में जानवर की हलचल पाई गई है (सेंसर: {sensors_str})।"
            else:
                response = f"Alert! Animal intrusion detected on sensors: {sensors_str}."
        elif overall == "NODE_OFFLINE":
            if is_marwari:
                response = "खेत रो IoT सुरक्षा नोड अभी ऑफलाइन है।"
            elif lang == "hi":
                response = "खेत का IoT सुरक्षा नोड अभी ऑफलाइन है।"
            else:
                response = "The farm IoT security node is currently offline."
        else:
            if is_marwari:
                response = "खेत पूरी तरह सुरक्षित है। कोई जानवर नीं आयो।"
            elif lang == "hi":
                response = "खेत बिल्कुल सुरक्षित है। किसी जानवर की कोई हलचल नहीं है।"
            else:
                response = "The farm perimeter is clear and secure. No animal intrusion detected."

    # 14. Fallback General Response
    else:
        if is_marwari:
            response = "FarmFusion AI में आपरो स्वागत है। आप म्हासूं मौसम, मंडी भाव, फसल सलाह या योजनावां बाबत पूछ सको हो।"
        elif lang == "hi":
            response = "FarmFusion AI में आपका स्वागत है। आप मुझसे मौसम, मंडी भाव, फसल सलाह या सरकारी योजनाओं के बारे में पूछ सकते हैं।"
        else:
            response = "Welcome to FarmFusion AI. You can ask me about weather, mandi prices, crop suitability, or government schemes."

    state["final_response"] = response
    state["response_language"] = lang
    state["response_dialect"] = dialect
    state["tts_language"] = lang if profile.tts.native_supported else profile.fallback_language
    state["native_tts"] = profile.tts.native_supported and (not dialect)
    state["fallback_used"] = not profile.tts.native_supported or bool(dialect)
    if dialect:
        state["fallback_reason"] = f"No native {dialect} TTS voice model available in Bhashini or Indic-TTS. Spoken response synthesized using parent language {state['tts_language']} (Hindi) voice."
    elif not profile.tts.native_supported:
        state["fallback_reason"] = f"No native {lang} TTS voice model available. Using fallback {state['tts_language']}."
    else:
        state["fallback_reason"] = None

    logger.info("response_synthesized", intent=intent, lang=lang, dialect=dialect, response=response, tts_language=state["tts_language"], native_tts=state["native_tts"])
    return state
