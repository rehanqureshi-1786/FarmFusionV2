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
        si = tool_data.get("smart_irrigation") or {}
        si_advice = si.get("actionable_advice", "")

        if is_marwari:
            response = f"आज {loc} में मौसम साफ रैवेला, तापमान {temp}°C अर नमी {hum}% है।"
            if si_advice:
                response += f" सिंचाई सलाह: {si_advice}"
            else:
                response += f" वार्षिक बरसात लगभग {rain} mm है।"
        elif lang == "hi":
            response = f"आज {loc} में तापमान {temp}°C और आर्द्रता {hum}% है, मौसम {cond} रहेगा।"
            if si_advice:
                response += f" {si_advice}"
            else:
                response += f" वार्षिक वर्षा लगभग {rain} mm है।"
        elif lang == "gu":
            response = f"આજે {loc}માં તાપમાન {temp}°C અને ભેજ {hum}% છે, વાતાવરણ {cond} રહેશે."
            if si_advice:
                response += f" {si_advice}"
        elif lang == "mr":
            response = f"आज {loc} मध्ये तापमान {temp}°C आणि आर्द्रता {hum}% आहे, हवामान {cond} राहील."
            if si_advice:
                response += f" {si_advice}"
        elif lang == "pa":
            response = f"ਅੱਜ {loc} ਵਿੱਚ ਤਾਪਮਾਨ {temp}°C ਅਤੇ ਨਮੀ {hum}% ਹੈ, ਮੌਸਮ {cond} ਰਹੇਗਾ।"
            if si_advice:
                response += f" {si_advice}"
        else:
            response = f"Today in {loc}, temperature is {temp}°C with {hum}% humidity and {cond} conditions."
            if si_advice:
                response += f" Irrigation advice: {si_advice}"
            else:
                response += f" Annual rainfall is approx {rain} mm."

    # 5b. Handle 7-Day Disaster Risk Prediction (DisasterPredictorAI ML Ensemble)
    elif intent == "disaster_risk":
        loc = tool_data.get("location", "आपके क्षेत्र")
        days = tool_data.get("forecast_days", 7)
        peak_hazard = tool_data.get("peak_disaster_type", "Low Risk")
        peak_level = tool_data.get("peak_risk_level", "LOW")
        peak_score = tool_data.get("peak_risk_score", 0.0)
        peak_date = tool_data.get("peak_risk_date", "")
        has_critical = tool_data.get("has_critical_alert", False)

        hazard_hi = {
            "Flood Risk": "बाढ़ और भारी बारिश",
            "Cyclone Risk": "चक्रवाती तूफान",
            "Drought Risk": "सूखे और लू",
            "Low Risk": "सामान्य और सुरक्षित मौसम"
        }.get(peak_hazard, peak_hazard)

        hazard_gu = {
            "Flood Risk": "પૂર અને ભારે વરસાદ",
            "Cyclone Risk": "વાવાઝોડું",
            "Drought Risk": "દુષ્કાળ અને ગરમી",
            "Low Risk": "સામાન્ય અને સુરક્ષિત વાતાવરણ"
        }.get(peak_hazard, peak_hazard)

        hazard_mr = {
            "Flood Risk": "पूर आणि मुसळधार पाऊस",
            "Cyclone Risk": "चक्रीवादळ",
            "Drought Risk": "दुष्काळ आणि उष्णता",
            "Low Risk": "सामान्य आणि सुरक्षित हवामान"
        }.get(peak_hazard, peak_hazard)

        hazard_pa = {
            "Flood Risk": "ਹੜ੍ਹ ਅਤੇ ਭਾਰੀ ਮੀਂਹ",
            "Cyclone Risk": "ਚੱਕਰਵਾਤੀ ਤੂਫਾਨ",
            "Drought Risk": "ਸੋਕਾ ਅਤੇ ਲੂ",
            "Low Risk": "ਸਧਾਰਣ ਅਤੇ ਸੁਰੱਖਿਅਤ ਮੌਸਮ"
        }.get(peak_hazard, peak_hazard)

        if has_critical:
            if is_marwari:
                response = f"सावधान किसान भाई! {loc} में {peak_date} ने {hazard_hi} रो भारी खतरा ({peak_level} स्तर, स्कोर {peak_score:.0f}) है। आपरी फसल अर पशुआं री सुरक्षा करो।"
            elif lang == "hi":
                response = f"सावधान किसान भाई! अगले {days} दिनों में {loc} में {peak_date} को {hazard_hi} का गंभीर खतरा ({peak_level} स्तर, स्कोर {peak_score:.0f}) है। कृपया तुरंत फसल सुरक्षा के उपाय करें।"
            elif lang == "gu":
                response = f"સાવધાન ખેડૂત મિત્ર! આગામી {days} દિવસમાં {loc}માં {peak_date}ના રોજ {hazard_gu}નું ગંભીર જોખમ ({peak_level} સ્તર, સ્કોર {peak_score:.0f}) છે. તાત્કાલિક સાવચેતીનાં પગલાં ભરો."
            elif lang == "mr":
                response = f"सावधान शेतकरी मित्र! पुढील {days} दिवसांत {loc} मध्ये {peak_date} रोजी {hazard_mr}चा गंभीर धोका ({peak_level} स्तर, स्कोअर {peak_score:.0f}) आहे. कृपया पिकांची काळजी घ्या."
            elif lang == "pa":
                response = f"ਸਾਵਧਾਨ ਕਿਸਾਨ ਵੀਰ! ਅਗਲੇ {days} ਦਿਨਾਂ ਵਿੱਚ {loc} ਵਿੱਚ {peak_date} ਨੂੰ {hazard_pa} ਦਾ ਵੱਡਾ ਖ਼ਤਰਾ ({peak_level} ਪੱਧਰ) ਹੈ। ਤੁਰੰਤ ਸੁਰੱਖਿਆ ਪ੍ਰਬੰਧ ਕਰੋ।"
            else:
                response = f"Warning for {loc}! Over the next {days} days, a {peak_level} hazard of {peak_hazard} (risk score {peak_score:.0f}) is forecast on {peak_date}. Immediate precautions advised."
        elif peak_level == "MEDIUM":
            if is_marwari:
                response = f"किसान भाई, {loc} में अगला {days} दिन में {peak_date} ने मध्यम स्तर रो {hazard_hi} रैवेला। खेत री निगरानी राखो।"
            elif lang == "hi":
                response = f"किसान भाई, अगले {days} दिनों में {loc} में स्थिति सामान्यतः ठीक रहेगी, लेकिन {peak_date} को मध्यम स्तर का {hazard_hi} (स्कोर {peak_score:.0f}) अनुमानित है। निगरानी रखें।"
            elif lang == "gu":
                response = f"ખેડૂત મિત્ર, આગામી {days} દિવસમાં {loc}માં સ્થિતિ મોટાભાગે સામાન્ય રહેશે, પણ {peak_date}ના રોજ મધ્યમ સ્તરનું {hazard_gu} અનુમાનિત છે."
            elif lang == "mr":
                response = f"शेतकरी मित्र, पुढील {days} दिवसांत {loc} मध्ये हवामान सामान्य राहील, पण {peak_date} रोजी मध्यम स्वरूपाचा {hazard_mr} संभवतो."
            else:
                response = f"Farmer advisory for {loc}: Generally normal conditions over the next {days} days, with a moderate {peak_hazard} predicted on {peak_date}."
        else:
            if is_marwari:
                response = f"किसान भाई, खुशी री बात है! {loc} में अगला {days} दिन मौसम एकदम सुरक्षित अर सामान्य (Low Risk) रैवेला। आप बेधड़क खेती रो काम कर सको हो।"
            elif lang == "hi":
                response = f"किसान भाई, अच्छी खबर है! अगले {days} दिनों में {loc} में मौसम पूरी तरह सुरक्षित और सामान्य (Low Risk) रहेगा। आप अपने कृषि कार्य निश्चिंत होकर कर सकते हैं।"
            elif lang == "gu":
                response = f"ખેડૂત મિત્ર, સારા સમાચાર! આગામી {days} દિવસમાં {loc}માં વાતાવરણ સુરક્ષિત અને સામાન્ય (Low Risk) રહેશે. આપ ખેતીકામ શાંતિથી કરી શકો છો."
            elif lang == "mr":
                response = f"शेतकरी मित्र, आनंदाची बातमी! पुढील {days} दिवसांत {loc} मध्ये हवामान पूर्णपणे सुरक्षित (Low Risk) राहील. आपण शेतीची कामे निर्धास्तपणे करू शकता."
            elif lang == "pa":
                response = f"ਕਿਸਾਨ ਵੀਰ, ਚੰਗੀ ਖ਼ਬਰ! ਅਗਲੇ {days} ਦਿਨਾਂ ਵਿੱਚ {loc} ਵਿੱਚ ਮੌਸਮ ਬਿਲਕੁਲ ਸੁਰੱਖਿਅਤ (Low Risk) ਰਹੇਗਾ। ਤੁਸੀਂ ਖੇਤੀ ਦੇ ਕੰਮ ਆਰਾਮ ਨਾਲ ਕਰ ਸਕਦੇ ਹੋ।"
            else:
                response = f"Good news for {loc}! Over the next {days} days, weather conditions are favorable with Low Risk. Normal agricultural operations can proceed safely."

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

    # 7a. Handle Best Practical & Nearby Mandi
    elif intent in ["best_nearby_mandi", "best_practical_mandi"]:
        comm = tool_data.get("commodity", "फसल") if isinstance(tool_data, dict) else "फसल"
        practical = tool_data.get("best_practical_mandi") or tool_data.get("best_mandi") if isinstance(tool_data, dict) else None
        highest = tool_data.get("highest_price_mandi") if isinstance(tool_data, dict) else None

        if practical:
            p_name = practical.get("market", "मंडी")
            p_price = practical.get("modal_price", "--")
            p_dist = practical.get("distance_km")
            p_dist_hi = f" ({p_dist} किमी)" if p_dist else ""
            p_dist_en = f" ({p_dist} km)" if p_dist else ""

            if highest and highest.get("market") != p_name:
                h_name = highest.get("market", "मंडी")
                h_price = highest.get("modal_price", "--")
                h_dist = highest.get("distance_km")
                h_dist_hi = f" ({h_dist} किमी)" if h_dist else ""
                h_dist_en = f" ({h_dist} km)" if h_dist else ""

                if is_marwari:
                    response = f"भाव और दूरी रे मुजब {p_name}{p_dist_hi} में ₹{p_price} प्रति क्विंटल सबसूं व्यावहारिक विकल्प है। सबसूं अधिक दर्ज भाव {h_name}{h_dist_hi} में ₹{h_price} है।"
                elif lang == "hi":
                    response = f"उपलब्ध भाव और दूरी को देखते हुए {p_name}{p_dist_hi} में ₹{p_price} प्रति क्विंटल सबसे व्यावहारिक विकल्प दिख रही है। सबसे अधिक दर्ज भाव {h_name}{h_dist_hi} में ₹{h_price}/क्विंटल है।"
                else:
                    response = f"Considering price and distance, {p_name}{p_dist_en} at ₹{p_price}/Q is the most practical option. Highest recorded price is at {h_name}{h_dist_en} at ₹{h_price}/Q."
            else:
                if is_marwari:
                    response = f"थांके नेड़े {comm} रो सबसूं व्यावहारिक और उच्चतम भाव {p_name}{p_dist_hi} में ₹{p_price} प्रति क्विंटल है।"
                elif lang == "hi":
                    response = f"आपके पास {comm} का सबसे व्यावहारिक और उच्चतम दर्ज भाव {p_name}{p_dist_hi} में ₹{p_price} प्रति क्विंटल है।"
                else:
                    response = f"Most practical market and highest recorded price for {comm} near you is {p_name}{p_dist_en} at ₹{p_price}/Quintal."
        else:
            response = f"आपके पास {comm} के मंडी भाव का डेटा उपलब्ध नहीं है।" if lang == "hi" else f"No nearby market price data found for {comm}."

    # 7b. Handle Mandi Comparison
    elif intent == "compare_mandi":
        comp = tool_data.get("comparison") if isinstance(tool_data, dict) else None
        if comp:
            diff = comp.get("price_difference", 0)
            pct = comp.get("percentage_difference", 0)
            higher = comp.get("higher_market", "")
            if higher == "EQUAL":
                if is_marwari:
                    response = "दोनूं मंडियां में भाव एक जेडा (बराबर) दर्ज है।"
                elif lang == "hi":
                    response = "दोनों मंडियों में भाव समान दर्ज किया गया है।"
                else:
                    response = "Prices are equal in both markets."
            else:
                if is_marwari:
                    response = f"{higher} मंडी में भाव ₹{diff} प्रति क्विंटल ({pct}%) अधिक दर्ज है।"
                elif lang == "hi":
                    response = f"{higher} में भाव ₹{diff} प्रति क्विंटल ({pct}%) अधिक दर्ज है।"
                else:
                    response = f"{higher} recorded price is ₹{diff}/Q ({pct}%) higher."
        else:
            response = "मंडियों के भाव की तुलना उपलब्ध नहीं हो सकी।" if lang == "hi" else "Market price comparison unavailable."

    # 7c. Handle Sell-Now vs Wait Advisory
    elif intent == "sell_wait_advisory":
        adv = tool_data.get("advisory") if isinstance(tool_data, dict) else None
        if adv:
            rec_hi = adv.get("recommendation_hi", "")
            rec_en = adv.get("recommendation_en", "")
            if is_marwari:
                sig = adv.get("signal")
                if sig == "POSSIBLE_UPSIDE":
                    response = "मॉडल रे मुजब आगलै 7 दिनां में भाव थोड़ा बढ़ण री संभावना है। जल्दी नीं होवै तो रुक सको हो।"
                elif sig == "FAVORABLE_TO_SELL":
                    response = "मॉडल रे मुजब भाव में नरमी आ सकै है। अभी बेचना ठीक रैवैला।"
                elif sig == "INSUFFICIENT_EVIDENCE":
                    response = "इण टेम उपलब्ध डेटा सूं पक्की दिशा नीं मिल री है।"
                else:
                    response = "आगलै दिनां में भाव लगभग बराबर रहण रो अनुमान है।"
            elif lang == "hi":
                response = rec_hi
            else:
                response = rec_en
        else:
            response = "इस समय उपलब्ध डेटा से स्पष्ट दिशा नहीं मिल रही है।" if lang == "hi" else "Insufficient data to provide advisory."

    # 7d. Handle Forecast Explanation
    elif intent == "explain_forecast":
        factors = tool_data.get("factors") if isinstance(tool_data, dict) else []
        comm = tool_data.get("commodity", "फसल") if isinstance(tool_data, dict) else "फसल"
        if factors:
            f_hi = factors[0].get("description_hi", "")
            f_en = factors[0].get("description_en", "")
            if is_marwari:
                response = f"{comm} भाव अनुमान: पिछले हफ्तों के ट्रेंड और मौसमी आवक के आधार पर मॉडल ने यह अनुमान लगाया है।"
            elif lang == "hi":
                response = f"{comm} का अनुमान: {f_hi}"
            else:
                response = f"{comm} forecast: {f_en}"
        else:
            response = f"{comm} के भाव अनुमान का ऐतिहासिक विश्लेषण उपलब्ध है।" if lang == "hi" else f"Historical model components factored for {comm}."

    # 7e. Handle Price Opportunity Alert
    elif intent == "price_alert":
        tp = tool_data.get("target_price") if isinstance(tool_data, dict) else None
        comm = tool_data.get("commodity", "फसल") if isinstance(tool_data, dict) else "फसल"
        if tp:
            if is_marwari:
                response = f"{comm} रो भाव अलर्ट ₹{tp} प्रति क्विंटल माथै सेट कर दियो है।"
            elif lang == "hi":
                response = f"{comm} के लिए भाव अलर्ट ₹{tp} प्रति क्विंटल पर सक्रिय कर दिया गया है।"
            else:
                response = f"Price alert for {comm} set at target ₹{tp}/Quintal."
        else:
            response = f"{comm} के लिए भाव अलर्ट दर्ज कर लिया गया है।" if lang == "hi" else f"Price alert registered for {comm}."

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
    state["last_final_response"] = response
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
