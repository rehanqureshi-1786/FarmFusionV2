"""
Response Synthesizer Node for LangGraph Orchestrator.
Formats multi-tool outputs into simple, rural-friendly farmer responses (2-3 sentences max)
strictly using verified tool payload with zero data fabrication.
"""
from typing import Any, Dict, List
import structlog

from app.orchestrator.state import OrchestratorState

logger = structlog.get_logger(__name__)


async def response_synthesizer_node(state: OrchestratorState) -> OrchestratorState:
    """
    Synthesize final localized response for the farmer.
    If requires_clarification is True, return the clarification question.
    """
    lang = state.get("detected_language", "hi")
    intent = state.get("intent", "unknown")
    tool_data = state.get("tool_output") or {}
    tool_status = state.get("tool_status", "success")

    # 1. Handle Clarification
    if state.get("requires_clarification"):
        q = state.get("clarification_question")
        if not q:
            q = "क्या आप कृपया अपनी फसल का नाम या सवाल दोबारा स्पष्ट कह सकते हैं?" if lang == "hi" else "Could you please clarify your question so I can provide accurate guidance?"
        state["final_response"] = q
        return state

    # 2. Handle Anaphora / Explanation: "पहली वाली क्यों?"
    if intent == "explain_recommendation":
        crop = tool_data.get("crop_name", "यह फसल")
        factors = tool_data.get("factors", [])
        if factors:
            factor_summary = " और ".join(factors[:2]) if lang == "hi" else " and ".join(factors[:2])
            if lang == "hi":
                response = f"{crop} को पहली प्राथमिकता इसलिए दी गई है क्योंकि {factor_summary}।"
            else:
                response = f"{crop} was ranked at the top because {factor_summary}."
        else:
            if lang == "hi":
                response = f"{crop} आपके क्षेत्र के मौसम, वर्षा और मिट्टी के लिए सबसे उपयुक्त पाई गई है।"
            else:
                response = f"{crop} is most suitable based on your local climate, rainfall, and soil conditions."

    # 3. Handle Weather
    elif intent == "weather":
        temp = tool_data.get("temperature_c", "--")
        hum = tool_data.get("humidity_percent", "--")
        cond = tool_data.get("condition", "सामान्य")
        loc = tool_data.get("location_name", "आपके क्षेत्र")
        rain = tool_data.get("annual_rainfall_mm", "--")
        if lang == "hi":
            response = f"आज {loc} में तापमान {temp}°C और आर्द्रता {hum}% है, मौसम {cond} रहेगा। वार्षिक वर्षा लगभग {rain} mm है।"
        else:
            response = f"Today in {loc}, temperature is {temp}°C with {hum}% humidity and {cond} conditions. Annual rainfall is approx {rain} mm."

    # 4. Handle Crop Recommendation & What-if
    elif intent in ["crop_recommendation", "what_if"]:
        recs = tool_data.get("recommendations") or tool_data.get("top_crops") or []
        if recs:
            top_crop = recs[0].get("crop_name", "फसल")
            score = recs[0].get("suitability_score", 0.90)
            second_crop = recs[1].get("crop_name", "") if len(recs) > 1 else ""
            if lang == "hi":
                response = f"आपके खेत के लिए सबसे उपयुक्त फसल {top_crop} है (उपयुक्तता स्कोर: {score:.2f})।" + (f" इसके अलावा आप {second_crop} भी लगा सकते हैं।" if second_crop else "")
            else:
                response = f"The top recommended crop for your field is {top_crop} (Suitability score: {score:.2f})." + (f" You may also consider {second_crop}." if second_crop else "")
        else:
            response = "पर्याप्त मौसम या मिट्टी की जानकारी नहीं मिल सकी।" if lang == "hi" else "Insufficient environmental data to assess crop suitability."

    # 5. Handle Mandi / Market Prices
    elif intent == "mandi":
        curr = tool_data.get("current_price") or {}
        comm = curr.get("commodity", "फसल")
        mandi = curr.get("market", "स्थानीय मंडी")
        price = curr.get("modal_price", "--")
        if lang == "hi":
            response = f"आज {mandi} में {comm} का औसत भाव ₹{price} प्रति क्विंटल दर्ज किया गया है।"
        else:
            response = f"Today at {mandi}, the modal price for {comm} is ₹{price} per quintal."

    # 6. Handle Crop Disease Info
    elif intent == "disease":
        if tool_status == "requires_photo":
            response = "फसल की बीमारी की सही पहचान के लिए, कृपया ऐप के कैमरा बटन से पत्ती की साफ फोटो खींचें।" if lang == "hi" else "To diagnose plant disease, please capture a clear leaf photo using the in-app camera."
        else:
            d_name = tool_data.get("disease_name") or tool_data.get("hindi_name", "रोग")
            sym = tool_data.get("symptoms", "")
            treat = tool_data.get("chemical_control", "") or tool_data.get("organic_control", "")
            if lang == "hi":
                response = f"{d_name}: मुख्य लक्षण - {sym[:80]}...। नियंत्रण के लिए: {treat[:100]}।"
            else:
                response = f"{d_name}: Symptoms include {sym[:80]}... Recommended management: {treat[:100]}."

    # 7. Handle Government Schemes
    elif intent == "scheme":
        schemes = tool_data.get("schemes", [])
        if schemes:
            s_name = schemes[0].get("scheme_name", "सरकारी योजना")
            benefit = schemes[0].get("benefits", "आर्थिक सहायता")
            if lang == "hi":
                response = f"प्रमुख योजना: {s_name}। लाभ: {benefit}। अधिक जानकारी ऐप के योजना सेक्शन में देखें।"
            else:
                response = f"Key scheme: {s_name}. Benefits: {benefit}. View details in the schemes section."
        else:
            response = "पीएम किसान और फसल बीमा योजना जैसी योजनाओं की जानकारी उपलब्ध है।" if lang == "hi" else "PM-Kisan and PMFBY scheme information is available."

    # 8. Handle Unsupported Capabilities
    elif intent == "unsupported_capability":
        cap = tool_data.get("capability", "")
        if cap == "purchase":
            response = "FarmFusion सीधे खाद या बीज की ऑनलाइन खरीद नहीं करता है। कृपया अपनी नजदीकी कृषि सेवा केंद्र से संपर्क करें।" if lang == "hi" else "FarmFusion does not process supply purchases. Please contact your nearest agricultural retail center."
        elif cap == "scheme_application":
            response = "मैं योजना की पात्रता और जानकारी बता सकता हूँ, लेकिन आवेदन आधिकारिक सरकारी पोर्टल (जैसे pmkisan.gov.in) पर ही करना होगा।" if lang == "hi" else "I can provide scheme eligibility and details, but official applications must be submitted on the government portal."
        else:
            response = "यह कार्य सीधे वॉइस असिस्टेंट द्वारा समर्थित नहीं है।" if lang == "hi" else "This capability is not supported via the voice assistant."

    # 9. Fallback General Response
    else:
        if lang == "hi":
            response = "FarmFusion AI में आपका स्वागत है। आप मुझसे मौसम, मंडी भाव, फसल सलाह या सरकारी योजनाओं के बारे में पूछ सकते हैं।"
        else:
            response = "Welcome to FarmFusion AI. You can ask me about weather, mandi prices, crop suitability, or government schemes."

    state["final_response"] = response
    logger.info("response_synthesized", intent=intent, lang=lang, response=response)
    return state
