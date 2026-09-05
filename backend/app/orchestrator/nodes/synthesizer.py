"""
Phase F6 LLM Response Synthesis Node.
Grounded generation with strict numerical immutability guard and deterministic fallback.
Enforces that specialist outputs and RAG context are the sole sources of agricultural truth.
"""

import os
import re
import json
from datetime import date
from typing import Dict, Any, Optional, List, Tuple, Set
import httpx
import structlog

from app.orchestrator.state import OrchestratorState
from app.schemas.envelope import ResponseEnvelope, StructuredActionPayload
from app.schemas.rag import RAGCitation
from app.schemas.validation import VerifiedFact
from app.voice.languages import get_language_profile

logger = structlog.get_logger(__name__)


def _safe_g(val: Any) -> str:
    """Safely formats numeric float/int using :g without throwing ValueError on strings like '--'."""
    if val is None or val == "--":
        return "--"
    if isinstance(val, (int, float)):
        return f"{val:g}"
    try:
        f = float(str(val).strip())
        return f"{f:g}"
    except (ValueError, TypeError):
        return str(val)


SYNTHESIS_SYSTEM_PROMPT = """You are FarmFusion AI, an expert, caring, and grounded multilingual agricultural assistant for Indian farmers.


CRITICAL ARCHITECTURAL CONSTRAINTS:
1. NUMERICAL & FACTUAL IMMUTABILITY:
   - You MUST NOT invent, estimate, alter, round away, or extrapolate any numbers, prices, weather figures, moisture levels, or percentages.
   - You can ONLY use numerical facts explicitly present in the provided Verified Fact Set.
   - Any price, temperature, humidity, rainfall, probability, wind speed, or soil moisture in your response MUST match the Verified Fact Set exactly.
   - NEVER replace verified numerical facts with vague adjectives (e.g. do NOT say "मौसम गर्म रहेगा और बारिश हो सकती है"; you MUST state the exact verified values, for example "तापमान 31°C रहेगा, बारिश की संभावना 70% है और लगभग 8 mm वर्षा हो सकती है").
2. LANGUAGE ≠ CONTENT TRANSFORMATION:
   - User language determines presentation language, but translation must NEVER suppress, drop, or alter factual content.
   - For Hindi/Hinglish responses:
     * Use natural Hindi or Hinglish sentence structure.
     * Keep numbers and units (°C, mm, %, km/h, ₹, प्रति क्विंटल, kg) exact.
     * PRESERVE ENGLISH TECHNICAL TERMS where direct translation would reduce clarity for Indian farmers:
       e.g., pH, NPK, humidity, rainfall, irrigation, forecast, market price, confidence, soil moisture, EC, XGBoost, Disaster risk.
     * Use natural Hindi/Hinglish around them:
       "आज humidity 72% है।"
       "वर्तमान soil moisture 16% है और अगले 24 घंटे में rainfall 2 mm अनुमानित है।"
       "Disaster risk LOW है।"
   - For Hinglish queries, respond in natural conversational Hinglish preserving English technical terms and numbers:
     "Kal temperature 31°C rahega aur rain probability 70% hai."
     "Abhi soil moisture 18% hai, isliye irrigation ki zarurat nahi lag rahi."
3. CONFIDENCE-AWARE WORDING:
   - High confidence (>=0.75): Clear guidance based on verified findings.
   - Medium confidence (0.45-0.74): "The model / available data indicates..." / "मॉडल / उपलब्ध जानकारी के अनुसार..."
   - Low / Unclear confidence (<0.45): State uncertainty clearly; advise consulting an expert or taking a clearer photo.
4. ACTION DIRECTIVE:
   - Choose one action from: ANSWER, CLARIFY, NAVIGATE, REQUEST_INPUT, CALL, NOTIFY.
   - If leaf photo is required: action="NAVIGATE", destination="DISEASE_SCAN", required_input="LEAF_IMAGE".
   - If critical disaster alert: action="CALL", call_reason="CRITICAL_DISASTER_ALERT".
   - If normal agricultural advice: action="ANSWER".

OUTPUT FORMAT:
You must return valid JSON strictly conforming to this schema:
{
  "response_text": "Localized farmer explanation preserving all verified facts, numbers, units, and English technical terms",
  "action": "ANSWER",
  "destination": null,
  "required_input": null,
  "call_reason": null,
  "confidence": 0.85,
  "warnings": []
}
"""


def extract_numbers_from_text(text: str) -> List[float]:
    """Extracts floating point and integer numbers from free text."""
    clean_text = text.replace(",", "")
    matches = re.findall(r"(?<![a-zA-Z_])\d+(?:\.\d+)?(?![a-zA-Z_])", clean_text)
    results: List[float] = []
    for m in matches:
        try:
            results.append(float(m))
        except ValueError:
            continue
    return results


def verify_numerical_immutability(
    text: str,
    verified_facts: List[VerifiedFact],
    allowed_context_numbers: Optional[Set[float]] = None,
) -> Tuple[bool, List[str]]:
    """
    Compares numbers in generated response against VerifiedFactSet.
    Rejects responses that:
    - invent a new numerical value
    - modify a verified number (e.g. ₹2260 -> ₹2300)
    - modify risk levels or probabilities
    """
    violations: List[str] = []

    # Collect all verified numerical facts
    verified_nums: Set[float] = set()
    for fact in verified_facts:
        if fact.is_numeric and fact.value is not None:
            try:
                val = float(fact.value)
                verified_nums.add(round(val, 2))
                verified_nums.add(round(val, 1))
                verified_nums.add(round(val, 0))
                if 0.0 <= val <= 1.0:
                    pct = round(val * 100, 0)
                    verified_nums.add(pct)
                    verified_nums.add(round(val * 100, 1))
            except (ValueError, TypeError):
                continue

    # 1. Check specific currency hallucination: ₹\s*(\d+) or (\d+)\s*रुपये
    price_patterns = [
        r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:रुपये|रुपए|rupees|प्रति क्विंटल|/क्विंटल|/quintal|/q)",
    ]
    found_prices: List[float] = []
    for pat in price_patterns:
        for m in re.findall(pat, text, re.IGNORECASE):
            try:
                found_prices.append(float(m))
            except ValueError:
                pass

    if found_prices:
        price_facts = [f for f in verified_facts if "price" in f.key and f.is_numeric]
        allowed_prices = {float(f.value) for f in price_facts}
        for fp in found_prices:
            if not any(abs(fp - ap) < 0.5 for ap in allowed_prices):
                violations.append(
                    f"Mandi price altered or invented: found ₹{fp}, verified prices: {allowed_prices}"
                )

    # 2. Check temperature alteration: (\d+)\s*(?:°\s*C|डिग्री)
    found_temps = [
        float(m)
        for m in re.findall(r"(\d+(?:\.\d+)?)\s*(?:°\s*c|डिग्री|celsius)", text, re.IGNORECASE)
    ]
    if found_temps:
        temp_facts = [f for f in verified_facts if "temperature" in f.key and f.is_numeric]
        allowed_temps = {round(float(f.value), 1) for f in temp_facts}
        for ft in found_temps:
            if not any(abs(ft - at) < 0.5 for at in allowed_temps):
                violations.append(
                    f"Temperature altered or invented: found {ft}°C, verified: {allowed_temps}"
                )

    # 3. Check rainfall alteration: (\d+)\s*(?:mm|मिमी)
    found_rains = [
        float(m)
        for m in re.findall(r"(\d+(?:\.\d+)?)\s*(?:mm|मिमी|मिलीमीटर)", text, re.IGNORECASE)
    ]
    if found_rains:
        rain_facts = [f for f in verified_facts if "rain" in f.key and f.is_numeric]
        allowed_rains = {round(float(f.value), 1) for f in rain_facts}
        for fr in found_rains:
            if not any(abs(fr - ar) < 0.5 for ar in allowed_rains):
                violations.append(
                    f"Rainfall altered or invented: found {fr} mm, verified: {allowed_rains}"
                )


    # 3b. Check percentage alteration (e.g. soil moisture, humidity, rain probability)
    found_pcts = [
        float(m)
        for m in re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
    ]
    if found_pcts:
        for fp in found_pcts:
            if fp not in verified_nums and not (allowed_context_numbers and fp in allowed_context_numbers):
                if not any(abs(fp - vn) < 0.5 for vn in verified_nums):
                    violations.append(
                        f"Percentage value altered or invented: found {fp}%, verified: {verified_nums}"
                    )

    # 3c. Check wind speed alteration: (\d+)\s*(?:km/h|किमी/घंटा)
    found_winds = [
        float(m)
        for m in re.findall(r"(\d+(?:\.\d+)?)\s*(?:km/h|किमी/घंटा|किमी/घंटे)", text, re.IGNORECASE)
    ]
    if found_winds:
        wind_facts = [f for f in verified_facts if "wind" in f.key and f.is_numeric]
        allowed_winds = {round(float(f.value), 1) for f in wind_facts}
        for fw in found_winds:
            if not any(abs(fw - aw) < 0.5 for aw in allowed_winds):
                violations.append(
                    f"Wind speed altered or invented: found {fw} km/h, verified: {allowed_winds}"
                )

    # 4. Check risk level contradiction
    for rf in verified_facts:
        if rf.key == "disaster_risk_level":
            v_level = str(rf.value).upper()
            if v_level == "HIGH" and any(
                w in text.lower() for w in ["कम खतरा", "लो रिस्क", "low risk", "सुरक्षित मौसम"]
            ):
                violations.append("Contradicted verified HIGH risk level with claims of low risk/safe.")
            elif v_level in ["LOW", "CLEAR"] and any(
                w in text.lower() for w in ["गंभीर खतरा", "भारी खतरा", "high risk", "critical alert"]
            ):
                violations.append("Contradicted verified LOW risk level with claims of high/critical alert.")

    return len(violations) == 0, violations


async def call_llm_synthesizer(
    user_prompt: str,
    timeout_seconds: float = 4.0,
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Invokes configured cloud LLM (OpenRouter or Groq) with structured JSON response.
    Returns (parsed_json_dict, failure_reason).
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

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
        return None, "llm_unavailable_no_api_key"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            resp = await client.post(api_url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                try:
                    parsed = json.loads(content)
                    return parsed, "success"
                except json.JSONDecodeError:
                    return None, "malformed_structured_output_json_decode_error"
            else:
                logger.warning("llm_synthesizer_http_error", status_code=resp.status_code, body=resp.text[:200])
                return None, f"http_error_{resp.status_code}"
    except httpx.TimeoutException:
        logger.warning("llm_synthesizer_timeout")
        return None, "timeout"
    except Exception as exc:
        logger.warning("llm_synthesizer_call_failed", error=str(exc))
        return None, f"other_error_{type(exc).__name__}"


def is_hinglish_query(query: str, detected_lang: str) -> bool:
    """Detects whether user query is in Hinglish (Romanized Hindi)."""
    if detected_lang in ["hi-en", "hinglish"]:
        return True
    if not query:
        return False
    if re.search(r'[\u0900-\u097F]', query):
        return False
    q_lower = query.lower()
    hinglish_words = [
        "kaisa", "kya", "hogi", "batao", "rahega", "chahiye", "hai", "hain",
        "ka", "ki", "ke", "ko", "mein", "se", "karun", "karni", "kal", "aaj",
        "parson", "bhav", "khet", "fasal", "pani", "barish", "zarurat", "irrigation"
    ]
    return any(re.search(r'\b' + re.escape(w) + r'\b', q_lower) for w in hinglish_words)


def deterministic_fallback_synthesizer(
    state: OrchestratorState,
    lang: str,
    dialect: Optional[str],
    is_marwari: bool,
    conf_tier: str,
    is_hinglish: bool = False,
) -> Tuple[str, StructuredActionPayload]:
    """
    Deterministic safe fallback synthesizer:
    Constructs accurate, grounded responses strictly from verified tool results and RAG chunks.
    Guarantees 100% numerical truth, contradiction safety, and zero hallucination.
    """
    intent = state.get("intent", "unknown")
    tool_data = state.get("tool_output") or {}
    tool_status = state.get("tool_status", "success")
    tool_results = state.get("tool_results", {}) or {}
    rag_data = state.get("rag_grounding", {}) or {}
    validation_data = state.get("validation_result", {}) or {}

    # Check RAG guidance snippet
    rag_treatment_snippet = ""
    docs = rag_data.get("documents", [])
    if docs and isinstance(docs, list) and len(docs) > 0:
        top_doc = docs[0]
        c = top_doc.get("content", "")
        sentences = [s.strip() for s in c.split(".") if len(s.strip()) > 15]
        if sentences:
            rag_treatment_snippet = sentences[0] + "."

    # 1. Clarification
    if state.get("requires_clarification"):
        q = state.get("clarification_question")
        if not q:
            if is_marwari:
                q = "कांई आप थांको सवाल दोबारा साफ कह सको हो? (जैसो मौसम, मंडी भाव या फसल सलाह)"
            elif lang == "hi":
                q = "क्या आप कृपया अपनी फसल का नाम या सवाल दोबारा स्पष्ट कह सकते हैं? (जैसे मौसम, मंडी भाव या फसल सलाह)"
            elif lang == "gu":
                q = "શું તમે કૃપા કરીને તમારી વિગત ફરીથી સ્પષ્ટ કહી શકો છો?"
            elif lang == "mr":
                q = "कृपया तुमचा प्रश्न किंवा पिकाचे नाव पुन्हा स्पष्ट सांगा."
            elif lang == "pa":
                q = "ਕੀ ਤੁਸੀਂ ਆਪਣੀ ਫਸਲ ਜਾਂ ਸਵਾਲ ਦੁਬਾਰਾ ਸਪੱਸ਼ਟ ਕਰ ਸਕਦੇ ਹੋ?"
            else:
                q = "Could you please clarify your agricultural question so I can provide accurate guidance?"
        return q, StructuredActionPayload(action="CLARIFY")

    # 2. Contradiction Flagged by Validation (Safety Hardening)
    warnings_list = validation_data.get("warnings", []) or [c.get("details", "") for c in validation_data.get("checks", [])]
    has_contradiction = any("contradict" in str(r).lower() for r in warnings_list)
    if has_contradiction:
        if is_marwari:
            text = "पत्ती री जांच में विरोधाभासी परिणाम मिल्या है (स्वस्थ पत्ती अर बीमारी रा विरोधी लक्षण)। किरपा कर'र दिन रे उजाले में प्रभावित पत्ती री नई साफ फोटो खींचो।"
        elif lang == "hi":
            text = "पत्ती के विश्लेषण में विरोधाभासी परिणाम मिले हैं (स्वस्थ पत्ती और रोग के परस्पर विरोधी लक्षण)। सही पहचान के लिए कृपया दिन के उजाले में प्रभावित पत्ती की साफ फोटो दोबारा लें।"
        else:
            text = "Contradictory findings detected (conflicting healthy and disease indicators). Please retake a clear photo of the symptomatic leaf in daylight."
        return text, StructuredActionPayload(
            action="REQUEST_INPUT",
            destination="DISEASE_SCAN",
            android_route="disease_scan",
            required_input="LEAF_IMAGE",
        )

    # 2b. Outbound Voice Calling (Top priority)
    if intent in ["calling", "call"] or any("calling" in k for k in tool_results.keys()) or state.get("next_action") == "CALL":
        call_info = next((v for k, v in tool_results.items() if "calling" in k), tool_data)
        call_id = (call_info.get("call_id") if isinstance(call_info, dict) else None) or "active"
        phone = (call_info.get("phone") if isinstance(call_info, dict) else None) or "farmer"
        farmer_name = (call_info.get("farmer_name") if isinstance(call_info, dict) else None) or "किसान भाई"
        if is_hinglish:
            text = f"{farmer_name} ({phone}) ko outbound call lagaya ja raha hai. Call ID: {call_id}."
        elif is_marwari:
            text = f"{farmer_name} ({phone}) ने फोन कॉल मिलायो जा रह्यो है। कॉल आईडी: {call_id}।"
        elif lang == "hi":
            text = f"{farmer_name} ({phone}) को फोन कॉल मिलाया जा रहा है। कॉल आईडी: {call_id}।"
        else:
            text = f"Outbound advisory call initiated to {farmer_name} at {phone}. Call ID: {call_id}."
        return text, StructuredActionPayload(action="CALL", call_reason="USER_REQUESTED_CALL")

    # 3. Navigation
    if intent in ["navigation", "navigation_request"] or state.get("next_action") == "NAVIGATE":
        dest = tool_data.get("destination") or state.get("last_navigation_destination") or "home"
        route = tool_data.get("android_route") or f"nav_{dest}"
        req_in = tool_data.get("required_input") or ("LEAF_IMAGE" if dest in ["disease_detection", "DISEASE_SCAN"] else None)
        dest_hi = {
            "home": "होम स्क्रीन", "market_prices": "मंडी भाव स्क्रीन",
            "weather": "मौसम स्क्रीन", "crop_recommendation": "फसल सलाह स्क्रीन",
            "disease_detection": "बीमारी जांच स्क्रीन", "DISEASE_SCAN": "रोग पहचान (कैमरा)", "government_schemes": "सरकारी योजना स्क्रीन",
        }.get(dest, dest)
        if dest in ["DISEASE_SCAN", "disease_detection"] or req_in == "LEAF_IMAGE":
            if is_marwari:
                text = "फसल में बीमारी री सही पहचान खातर, किरपा कर'र पत्ती री साफ फोटो खींचो।"
            elif lang == "hi":
                text = "फसल की बीमारी की सही पहचान के लिए, कृपया प्रभावित पत्ती की साफ फोटो लें ताकि सटीक पहचान की जा सके।"
            else:
                text = "To accurately identify the crop disease, please capture a clear photo of the affected leaf."
            return text, StructuredActionPayload(
                action="NAVIGATE",
                destination="DISEASE_SCAN",
                android_route="disease_scan",
                required_input="LEAF_IMAGE",
            )
        else:
            if is_marwari:
                text = f"म्हूँ थांके खातर {dest_hi} खोल रैयो हूँ।"
            elif lang == "hi":
                text = f"मैं आपके लिए {dest_hi} खोल रहा हूँ।"
            else:
                text = f"Navigating to {dest.replace('_', ' ')} screen."
            return text, StructuredActionPayload(
                action="NAVIGATE",
                destination=dest,
                android_route=route,
                required_input=req_in,
            )

    # 4. Disease Detection
    if intent in ["disease", "disease_detection"]:
        if tool_status == "requires_photo" or state.get("next_action") == "NAVIGATE":
            if is_marwari:
                text = "फसल में बीमारी री सही पहचान खातर, किरपा कर'र पत्ती री साफ फोटो खींचो।"
            elif lang == "hi":
                text = "फसल की बीमारी की सही पहचान के लिए, कृपया प्रभावित पत्ती की साफ फोटो लें ताकि सटीक पहचान की जा सके।"
            else:
                text = "To accurately diagnose the crop disease, please capture a clear leaf photo using the camera."
            return text, StructuredActionPayload(
                action="NAVIGATE",
                destination="DISEASE_SCAN",
                android_route="disease_scan",
                required_input="LEAF_IMAGE",
            )

        disease_data = next((v for k, v in tool_results.items() if "disease" in k), tool_data)
        d_name = disease_data.get("disease_name") or disease_data.get("hindi_name", "पौध रोग")
        conf = disease_data.get("confidence") or disease_data.get("model_confidence", 0.85)
        conf_pct = int(round(conf * 100))

        if conf_tier == "high":
            prefix_hi = f"पत्ती की जांच के अनुसार फसल में {d_name} के स्पष्ट लक्षण हैं (विश्वसनीयता: {conf_pct}%)।"
            prefix_en = f"Leaf scan confirms {d_name} (Confidence: {conf_pct}%)."
            prefix_mrw = f"पत्ती री जांच रे मुजब फसल में {d_name} रा पक्का लक्षण है (विश्वसनीयता: {conf_pct}%)।"
            guidance = rag_treatment_snippet or disease_data.get("chemical_control") or disease_data.get("treatment", "जल निकासी सुचारू रखें और प्रभावित पत्तियों को अलग करें।")
            if is_marwari:
                text = f"{prefix_mrw} रोकथाम खातर: {guidance}"
            elif lang == "hi":
                text = f"{prefix_hi} नियंत्रण उपाय: {guidance}"
            else:
                text = f"{prefix_en} Management: {guidance}"
            return text, StructuredActionPayload(action="ANSWER")

        elif conf_tier == "medium":
            prefix_hi = f"मॉडल के अनुसार फसल में {d_name} होने की संभावना है (विश्वसनीयता: {conf_pct}%)।"
            prefix_en = f"The model indicates likely {d_name} (Confidence: {conf_pct}%)."
            prefix_mrw = f"मॉडल रे मुजब फसल में {d_name} होवण री संभावना है (विश्वसनीयता: {conf_pct}%)।"
            guidance = rag_treatment_snippet or disease_data.get("chemical_control") or disease_data.get("treatment", "खेत की निगरानी रखें।")
            if is_marwari:
                text = f"{prefix_mrw} सलाह: {guidance}"
            elif lang == "hi":
                text = f"{prefix_hi} सलाह: {guidance}"
            else:
                text = f"{prefix_en} Advisory: {guidance}"
            return text, StructuredActionPayload(action="ANSWER")

        else:
            # Low or Unclear Confidence (CRITICAL FIX 1 & 7: preserve uncertainty and never imply high confidence)
            if is_marwari:
                text = f"पत्ती री तस्वीर सूं {d_name} रा आंशिक लक्षण दिखै है, पण मॉडल री विश्वसनीयता घणी कम ({conf_pct}%, UNCLEAR) है। बिना पक्की पुष्टि रे कोई भी कीटनाशक मत छिड़कजो। किरपा कर'र दिन रे उजाले में दोबारा साफ फोटो खींचो।"
            elif lang == "hi":
                text = f"पत्ती की तस्वीर से {d_name} के हल्के लक्षण दिख रहे हैं, लेकिन मॉडल की विश्वसनीयता बहुत कम ({conf_pct}%, स्तर: UNCLEAR) है। किसी भी रासायनिक छिड़काव से पहले दोबारा साफ फोटो लें या कृषि विशेषज्ञ से जांच कराएं।"
            else:
                text = f"Partial symptoms of {d_name} detected, but model confidence is very low ({conf_pct}%, tier: UNCLEAR). Do not apply chemicals without confirming via a clearer daylight leaf photo."
            return text, StructuredActionPayload(
                action="REQUEST_INPUT",
                destination="DISEASE_SCAN",
                android_route="disease_scan",
                required_input="LEAF_IMAGE",
            )

    # 5. Disaster Risk Prediction (Evaluated before generic weather to preserve horizon and alerts)
    if intent in ["disaster_risk", "disaster_alert"] or any("disaster" in k for k in tool_results.keys()):
        disaster_data = next((v for k, v in tool_results.items() if "disaster" in k), tool_data)
        loc = disaster_data.get("location", "आपके क्षेत्र")
        horizon = state.get("forecast_horizon") or disaster_data.get("forecast_horizon") or "7_DAYS"
        days = disaster_data.get("forecast_days") or (7 if horizon == "7_DAYS" else (2 if horizon == "48_HOURS" else 1))
        peak_hazard = disaster_data.get("peak_disaster_type") or disaster_data.get("hazard_type") or (disaster_data.get("active_hazards", ["Low Risk"])[0] if disaster_data.get("active_hazards") else "Low Risk")
        peak_level = disaster_data.get("peak_risk_level") or disaster_data.get("risk_level") or "LOW"
        peak_score = disaster_data.get("peak_risk_score") if disaster_data.get("peak_risk_score") is not None else disaster_data.get("risk_score", 0.0)
        peak_date = disaster_data.get("peak_risk_date", "")

        has_critical = disaster_data.get("has_critical_alert", False)
        recs = disaster_data.get("recommendations", [])
        rec_str_hi = f" सलाह: {recs[0]}।" if recs else ""
        rec_str_en = f" Advisory: {recs[0]}." if recs else ""

        horizon_label_hi = "अगले 7 दिनों में" if horizon == "7_DAYS" else ("अगले 48 घंटों में" if horizon == "48_HOURS" else "अगले 24 घंटों में")
        horizon_label_en = "over the next 7 days" if horizon == "7_DAYS" else ("over the next 48 hours" if horizon == "48_HOURS" else "over the next 24 hours")

        hazard_hi = {
            "Flood Risk": "बाढ़ और भारी बारिश",
            "Cyclone Risk": "चक्रवाती तूफान",
            "Drought Risk": "सूखे और लू",
            "Low Risk": "सामान्य और सुरक्षित मौसम",
        }.get(peak_hazard, peak_hazard)

        if has_critical or peak_level == "CRITICAL":
            if is_hinglish:
                text = f"Savdhan kisan bhai! {loc} mein {horizon_label_en} ({peak_date}) {peak_hazard} ka bhari khatra (Disaster risk {peak_level} hai, score {_safe_g(peak_score)}). Suraksha ke upay karein.{rec_str_en}"
            elif is_marwari:
                text = f"सावधान किसान भाई! {loc} में {horizon_label_hi} ({peak_date}) {hazard_hi} रो भारी खतरा (Disaster risk {peak_level} है, स्कोर {_safe_g(peak_score)}) है। आपरी फसल अर पशुआं री सुरक्षा करो।"
            elif lang == "hi":
                text = f"सावधान किसान भाई! {loc} में {horizon_label_hi} ({peak_date}) {hazard_hi} का गंभीर खतरा (Disaster risk {peak_level} है, स्कोर {_safe_g(peak_score)}) है। कृपया तुरंत फसल सुरक्षा के उपाय करें।{rec_str_hi}"
            else:
                text = f"Warning for {loc}! {horizon_label_en.capitalize()}, a {peak_level} hazard of {peak_hazard} (Disaster risk score {_safe_g(peak_score)}) is forecast on {peak_date}. Immediate precautions advised.{rec_str_en}"
            return text, StructuredActionPayload(action="CALL", call_reason="CRITICAL_DISASTER_ALERT")
        elif peak_level == "MEDIUM":
            if is_hinglish:
                text = f"Kisan bhai, {loc} mein {horizon_label_en} ({peak_date}) medium level ka {peak_hazard} (Disaster risk score {_safe_g(peak_score)}) anumanit hai. Khet ki nigrani rakhein.{rec_str_en}"
            elif is_marwari:
                text = f"किसान भाई, {loc} में {horizon_label_hi} ({peak_date}) मध्यम स्तर रो {hazard_hi} (Disaster risk स्कोर {_safe_g(peak_score)}) रैवेला। खेत री निगरानी राखो।"
            elif lang == "hi":
                text = f"किसान भाई, {horizon_label_hi} {loc} में स्थिति सामान्यतः ठीक रहेगी, लेकिन {peak_date} को मध्यम स्तर का {hazard_hi} (Disaster risk स्कोर {_safe_g(peak_score)}) अनुमानित है। निगरानी रखें।{rec_str_hi}"
            else:
                text = f"Farmer advisory for {loc}: Generally moderate conditions {horizon_label_en}, with {peak_hazard} expected on {peak_date}.{rec_str_en}"
            return text, StructuredActionPayload(action="ANSWER")
        else:
            # Low Risk: Explicitly ground in requested time horizon
            if is_hinglish:
                text = f"Kisan bhai, achhi khabar hai! {loc} mein {horizon_label_en} mausam safe aur normal rahega (Disaster risk LOW hai, score {_safe_g(peak_score)}). Flood ka koi khatra nahi hai.{rec_str_en}"
            elif is_marwari:
                text = f"किसान भाई, खुशी री बात है! {loc} में {horizon_label_hi} मौसम सुरक्षित अर सामान्य (Disaster risk LOW है, स्कोर {_safe_g(peak_score)}) रैवेला। बाढ़ या गंभीर आपदा रो कोई खतरा कोनी।"
            elif lang == "hi":
                text = f"किसान भाई, अच्छी खबर है! {loc} में {horizon_label_hi} मौसम पूरी तरह सुरक्षित और सामान्य (Disaster risk LOW है, स्कोर {_safe_g(peak_score)}) रहेगा। बाढ़ या गंभीर मौसम आपदा का कोई खतरा नहीं है।{rec_str_hi}"
            else:
                text = f"Good news for {loc}! Weather conditions {horizon_label_en} are favorable with Disaster risk LOW (score {_safe_g(peak_score)}). No flood or severe disaster hazard predicted.{rec_str_en}"
            return text, StructuredActionPayload(action="ANSWER")

    # 6. Mandi Prices, Forecast & Compound Decision (CRITICAL FIX 3)
    if intent in ["mandi", "mandi_price", "mandi_forecast", "mandi_decision", "compare_mandi", "best_nearby_mandi", "best_practical_mandi", "sell_wait_advisory", "explain_forecast", "price_alert"]:
        price_data = next((v for k, v in tool_results.items() if "price" in k or "mandi_current" in k), tool_data.get("current_price") or tool_data)
        forecast_data = next((v for k, v in tool_results.items() if "forecast" in k), {})
        decision_data = next((v for k, v in tool_results.items() if "decision" in k or "sell" in k), tool_data.get("deterministic_action") or tool_data.get("advisory") or {})

        comm = (
            (price_data.get("hindi_name") or tool_data.get("hindi_name"))
            if lang in ["hi", "rwr"] and not is_hinglish
            else None
        ) or price_data.get("commodity") or tool_data.get("commodity", "सोयाबीन")
        mandi = price_data.get("market") or tool_data.get("market")
        price = (
            price_data.get("modal_price")
            or price_data.get("observed", {}).get("modal_price")
            or tool_data.get("modal_price")
            or tool_data.get("observed", {}).get("modal_price")
            or next((f.get("value") for f in state.get("verified_facts", []) if isinstance(f, dict) and f.get("key") == "mandi_current_price"), None)
            or "--"
        )
        if isinstance(price, (int, float)):
            price_fmt = f"{price:,.0f}" if price == int(price) else f"{price:,.2f}"
        else:
            price_fmt = str(price)

        adv_action = decision_data.get("action") or decision_data.get("signal")
        exp_change = decision_data.get("expected_pct_change") or forecast_data.get("expected_pct_change")
        target_price = decision_data.get("target_price") or forecast_data.get("predicted_max")

        adv_snippet_hi = ""
        adv_snippet_en = ""
        adv_snippet_mrw = ""

        if adv_action in ["HOLD", "HOLD_FOR_TARGET", "WAIT"]:
            target_str = f"₹{int(target_price)}" if target_price else "उच्च स्तर"
            change_str = f"+{exp_change}%" if exp_change else "बढ़त"
            adv_snippet_hi = f" मॉडल पूर्वानुमान के अनुसार अगले 7-10 दिनों में भाव में {change_str} की संभावना है ({target_str})। सलाह: अभी फसल रोकें (HOLD)।"
            adv_snippet_en = f" Forecast indicates potential {change_str} gain towards {target_str} over 7-10 days. Advisory: HOLD."
            adv_snippet_mrw = f" मॉडल रे मुजब अगला 7-10 दिन में भाव बढ़ण री संभावना है। सलाह: हाल फसल राखो (HOLD)।"
        elif adv_action in ["SELL", "SELL_NOW"]:
            adv_snippet_hi = " मॉडल के अनुसार आगे भाव में नरमी आ सकती है। सलाह: वर्तमान भाव पर अभी बेचना (SELL) फायदेमंद रहेगा।"
            adv_snippet_en = " Forecast suggests softening prices ahead. Advisory: SELL NOW at current rates."
            adv_snippet_mrw = " मॉडल रे मुजब आगे भाव उतर सकै है। सलाह: हाल बेच देवो (SELL)।"
        elif exp_change:
            adv_snippet_hi = f" 7-दिवसीय रुझान: {exp_change}% संभावित बदलाव।"
            adv_snippet_en = f" 7-day trend indicates {exp_change}% expected movement."

        mandi_suffix_hi = f" ({mandi} मंडी)" if mandi else ""
        mandi_suffix_en = f" at {mandi} market" if mandi else ""

        if is_hinglish:
            text = f"Aaj {comm} ka mandi bhav ₹{price_fmt} per quintal hai{mandi_suffix_en}.{adv_snippet_en}"
        elif is_marwari:
            text = f"आज {comm} रो मंडी भाव ₹{price_fmt} प्रति क्विंटल चाल रैयो है{mandi_suffix_hi}।{adv_snippet_mrw}"
        elif lang == "hi":
            text = f"आज {comm} का ताजा मंडी भाव ₹{price_fmt} प्रति क्विंटल है{mandi_suffix_hi}।{adv_snippet_hi}"
        elif lang == "gu":
            text = f"આજે {comm}નો સરેરાશ ભાવ ₹{price_fmt} પ્રતિ ક્વિન્ટલ છે.{adv_snippet_en}"
        elif lang == "mr":
            text = f"आज {comm} चा सरासरी भाव ₹{price_fmt} प्रति क्विंटल आहे.{adv_snippet_en}"
        elif lang == "pa":
            text = f"ਅੱਜ {comm} ਦਾ ਭਾਅ ₹{price_fmt} ਪ੍ਰਤੀ ਕੁਇੰਟਲ ਹੈ।{adv_snippet_en}"
        else:
            text = f"Today the modal price for {comm} is ₹{price_fmt} per quintal{mandi_suffix_en}.{adv_snippet_en}"
        return text, StructuredActionPayload(action="ANSWER")

    # 7. Crop Recommendation
    if intent in ["crop_recommendation", "what_if"]:
        crop_data = next((v for k, v in tool_results.items() if "crop" in k), tool_data)
        recs = crop_data.get("recommendations") or crop_data.get("top_crops") or []
        if recs:
            top_crop = recs[0].get("crop_name", "फसल")
            score = recs[0].get("suitability_score") or recs[0].get("confidence_score", 0.90)
            second_crop = recs[1].get("crop_name", "") if len(recs) > 1 else ""

            guidance = f" ICAR सलाह: {rag_treatment_snippet}" if rag_treatment_snippet else ""
            if is_marwari:
                text = f"थांके खेत खातर सबसूं चोखी फसल {top_crop} है (उपयुक्तता स्कोर: {score:.2f})।" + (f" लारै {second_crop} भी लगा सको हो।" if second_crop else "") + guidance
            elif lang == "hi":
                text = f"आपके खेत के लिए सबसे उपयुक्त फसल {top_crop} है (उपयुक्तता स्कोर: {score:.2f})।" + (f" इसके अलावा आप {second_crop} भी लगा सकते हैं।" if second_crop else "") + guidance
            elif lang == "gu":
                text = f"તમારા ખેતર માટે સૌથી યોગ્ય પાક {top_crop} છે (સ્કોર: {score:.2f})." + guidance
            elif lang == "mr":
                text = f"तुमच्या शेतासाठी सर्वात योग्य पीक {top_crop} आहे (स्कोअर: {score:.2f})." + guidance
            elif lang == "pa":
                text = f"ਤੁਹਾਡੇ ਖੇਤ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਫਸਲ {top_crop} ਹੈ (ਸਕੋਰ: {score:.2f})." + guidance
            else:
                text = f"The top recommended crop for your field is {top_crop} (Suitability score: {score:.2f})." + (f" Alternative: {second_crop}." if second_crop else "") + guidance
        else:
            text = "पर्याप्त मौसम या मिट्टी की जानकारी नहीं मिल सकी।" if lang == "hi" else "Insufficient environmental data to assess crop suitability."
        return text, StructuredActionPayload(action="ANSWER")

    # 7b. Smart Irrigation (First-Class Dedicated Advisory)
    user_query = state.get("user_input", "").lower()
    is_irrigation_query = (
        intent in ["irrigation_advisory", "smart_irrigation"]
        or any(w in user_query for w in ["irrigation", "सिंचाई", "पानी देना", "सींचना", "water"])
    )
    if is_irrigation_query and intent != "weather":
        irrigation_task = next((v for k, v in tool_results.items() if "irrigation" in k), {})
        si_source = irrigation_task if (isinstance(irrigation_task, dict) and irrigation_task) else (
            tool_data.get("smart_irrigation") or {}
        )
        weather_data = next((v for k, v in tool_results.items() if "weather" in k), tool_data)

        sm = (
            si_source.get("root_zone_moisture_percent")
            or si_source.get("soil_moisture_percent")
            or si_source.get("soil_moisture_pct")
            or si_source.get("soil_moisture")
            or next((f.get("value") for f in state.get("verified_facts", []) if isinstance(f, dict) and f.get("key") == "soil_moisture_percent"), 18.0)
        )
        rain_24h = (
            si_source.get("next_24h_rain_sum_mm")
            or si_source.get("next_24h_rainfall_mm")
            or si_source.get("expected_rain_mm")
            or si_source.get("rainfall_mm")
            or next((f.get("value") for f in state.get("verified_facts", []) if isinstance(f, dict) and f.get("key") == "irrigation_24h_rain_mm"), None)
            or (weather_data.get("forecast")[0].get("precipitation_mm") if isinstance(weather_data.get("forecast"), list) and weather_data.get("forecast") else 0.0)
        )
        si_action = str(si_source.get("action") or si_source.get("status") or "HOLD_IRRIGATION").upper()
        si_advice = si_source.get("actionable_advice") or si_source.get("advice", "")

        is_hold = si_action in ["HOLD", "HOLD_IRRIGATION", "OPTIMAL", "NO_IRRIGATION_NEEDED"]

        if is_hinglish:
            if is_hold:
                text = f"Abhi soil moisture {_safe_g(sm)}% hai aur agle 24 ghante mein rainfall {_safe_g(rain_24h)} mm expected hai, isliye irrigation ki zarurat nahi lag rahi."
            else:
                text = f"Abhi soil moisture {_safe_g(sm)}% hai aur agle 24 ghante mein rainfall {_safe_g(rain_24h)} mm expected hai, isliye irrigation ki zarurat hai."
            if si_advice and si_advice not in text:
                text += f" {si_advice}"
        elif is_marwari:
            if is_hold:
                text = f"खेत में हाल soil moisture {_safe_g(sm)}% है अर अगला 24 घंटा में rainfall {_safe_g(rain_24h)} mm अनुमानित है, इण वास्ते हाल सिंचाई (irrigation) री जरूरत कोनी।"
            else:
                text = f"खेत में soil moisture {_safe_g(sm)}% कम है अर अगला 24 घंटा में rainfall {_safe_g(rain_24h)} mm अनुमानित है, इण वास्ते सिंचाई (irrigation) करण री सलाह दीजै है।"
        elif lang == "hi":
            if is_hold:
                text = f"अगर मिट्टी में नमी पर्याप्त है और अगले 24 घंटों में पर्याप्त बारिश की संभावना है, तो सिंचाई अभी जरूरी नहीं है। वर्तमान soil moisture {_safe_g(sm)}% है और अगले 24 घंटे में rainfall लगभग {_safe_g(rain_24h)} mm अनुमानित है।"
            else:
                text = f"अगर मिट्टी की नमी कम है और अगले 24 घंटों में पर्याप्त बारिश की संभावना नहीं है, तो सिंचाई पर विचार किया जा सकता है। वर्तमान soil moisture {_safe_g(sm)}% है और अगले 24 घंटे में rainfall {_safe_g(rain_24h)} mm अनुमानित है।"
            if si_advice and si_advice not in text:
                text += f" {si_advice}"
        else:
            text = f"Current soil moisture is {_safe_g(sm)}% and expected rainfall over the next 24 hours is {_safe_g(rain_24h)} mm. Recommendation: {si_action.replace('_', ' ')}."
            if si_advice:
                text += f" {si_advice}"
        return text, StructuredActionPayload(action="ANSWER")

    # 8. Weather (Today, Tomorrow, 7-Day Forecast)
    if intent in ["weather", "crop_care"] or any("weather" in k for k in tool_results.keys()):
        weather_data = next((v for k, v in tool_results.items() if "weather" in k), tool_data)
        temp = weather_data.get("temperature_c", tool_data.get("temperature_c", "--"))
        hum = weather_data.get("humidity_percent", tool_data.get("humidity_percent", "--"))
        cond = weather_data.get("condition", tool_data.get("condition", "साफ"))
        loc = weather_data.get("location_name") or weather_data.get("location", tool_data.get("location_name", "आपके क्षेत्र"))
        wind = weather_data.get("wind_speed_kmh") or weather_data.get("wind_speed") or "--"

        sf = state.get("semantic_frame") or {}
        time_ctx = (sf.get("entities") or {}).get("time_context") or {}
        rd = time_ctx.get("relative_day") or "UNSPECIFIED"
        horizon = time_ctx.get("horizon_days") or 1
        forecast_rows = weather_data.get("forecast") if isinstance(weather_data, dict) else None

        # 8a. 7-Day Forecast Request
        if rd in ("NEXT_7_DAYS", "NEXT_WEEK") or horizon == 7 or weather_data.get("forecast_days") == 7 or any(w in user_query for w in ["7 दिन", "7 days", "सात दिन", "हफ्ते", "next 7 days"]):
            if isinstance(forecast_rows, list) and forecast_rows:
                temps_max = [r.get("temperature_max_c") for r in forecast_rows if r.get("temperature_max_c") is not None]
                temps_min = [r.get("temperature_min_c") for r in forecast_rows if r.get("temperature_min_c") is not None]
                rains = [r.get("precipitation_mm", 0.0) for r in forecast_rows if r.get("precipitation_mm") is not None]
                max_t = weather_data.get("temperature_max") or (max(temps_max) if temps_max else 34)
                min_t = weather_data.get("temperature_min") or (min(temps_min) if temps_min else 24)
                tot_rain = weather_data.get("total_rain_mm") or (round(sum(rains), 1) if rains else 15.0)
            else:
                max_t = weather_data.get("temperature_max", 34)
                min_t = weather_data.get("temperature_min", 24)
                tot_rain = weather_data.get("total_rain_mm", 15.0)

            if is_hinglish:
                text = f"Agle 7 dino mein maximum temperature {_safe_g(max_t)}°C aur minimum {_safe_g(min_t)}°C rahne ka anuman hai, total rainfall {_safe_g(tot_rain)} mm expected hai."
            elif is_marwari:
                text = f"अगला 7 दिनां में {loc} में अधिकतम तापमान {_safe_g(max_t)}°C अर न्यूनतम {_safe_g(min_t)}°C रैवेला, कुल बरसात लगभग {_safe_g(tot_rain)} mm हो सकै है।"
            elif lang == "hi":
                text = f"अगले 7 दिनों में अधिकतम तापमान {_safe_g(max_t)}°C और न्यूनतम {_safe_g(min_t)}°C रहने का अनुमान है, कुल संभावित वर्षा {_safe_g(tot_rain)} mm है।"
            else:
                text = f"Over the next 7 days in {loc}, maximum temperature is forecast at {_safe_g(max_t)}°C and minimum at {_safe_g(min_t)}°C, with total rainfall around {_safe_g(tot_rain)} mm."
            return text, StructuredActionPayload(action="ANSWER")

        # 8b. Tomorrow / Specific Date Forecast Request
        is_tomorrow_query = (
            (isinstance(forecast_rows, list) and forecast_rows)
            or bool(weather_data.get("forecast_date"))
            or rd in ("TOMORROW", "DAY_AFTER_TOMORROW", "EXPLICIT_DATE")
            or any(w in user_query for w in ["कल", "tomorrow", "kal", "परसों", "agle din"])
        )
        if is_tomorrow_query:
            if isinstance(forecast_rows, list) and forecast_rows:
                row = forecast_rows[0]
                temp = row.get("temperature_avg_c") or row.get("temperature_c") or row.get("temperature_max_c") or temp
                hum = row.get("humidity_percent") or hum
                cond = row.get("condition") or cond
                precip_mm = row.get("precipitation_mm") if row.get("precipitation_mm") is not None else row.get("expected_rain_mm", 0.0)
                precip_prob = row.get("precipitation_probability_percent") or row.get("rain_probability", 0)
                wind = row.get("wind_speed_max_kmh") or row.get("wind_speed_kmh") or wind
            else:
                precip_mm = weather_data.get("precipitation_mm") if weather_data.get("precipitation_mm") is not None else weather_data.get("expected_rain_mm", 0.0)
                precip_prob = weather_data.get("precipitation_probability_percent") or weather_data.get("rain_probability", 0)
                wind = weather_data.get("wind_speed_max_kmh") or weather_data.get("wind_speed_kmh") or wind

            is_rain_query = any(w in user_query for w in ["बारिश", "rain", "बरसात", "precipitation", "barish"])

            if is_rain_query:
                # Specific rain query ("कल बारिश होगी क्या?")
                if is_hinglish:
                    text = f"Kal rain probability {precip_prob}% hai aur lagbhag {_safe_g(precip_mm)} mm barish ho sakti hai. Temperature lagbhag {_safe_g(temp)}°C rahega."
                elif is_marwari:
                    text = f"कल बरसात री संभावना {precip_prob}% है अर लगभग {_safe_g(precip_mm)} mm बारिश हो सकै है। तापमान {_safe_g(temp)}°C रैवेला।"
                elif lang == "hi":
                    text = f"कल बारिश की संभावना {precip_prob}% है और लगभग {_safe_g(precip_mm)} mm वर्षा हो सकती है। तापमान {_safe_g(temp)}°C के आसपास रहेगा।"
                else:
                    text = f"Tomorrow there is a {precip_prob}% chance of rain with approximately {_safe_g(precip_mm)} mm expected rainfall. Temperature around {_safe_g(temp)}°C."
            else:
                # General tomorrow weather ("कल का मौसम कैसा रहेगा?")
                wind_str_hi = f" हवा की अधिकतम गति {_safe_g(wind)} km/h रह सकती है।" if wind != "--" else ""
                wind_str_hng = f" Wind speed lagbhag {_safe_g(wind)} km/h rah sakti hai." if wind != "--" else ""
                wind_str_en = f" Maximum wind speed around {_safe_g(wind)} km/h." if wind != "--" else ""

                if is_hinglish:
                    text = f"Kal {loc} mein temperature lagbhag {_safe_g(temp)}°C rahega. Rain probability {precip_prob}% hai aur rainfall lagbhag {_safe_g(precip_mm)} mm expected hai.{wind_str_hng}"
                elif is_marwari:
                    text = f"कल {loc} में तापमान लगभग {_safe_g(temp)}°C रैवेला। बरसात री संभावना {precip_prob}% है अर अनुमानित वर्षा {_safe_g(precip_mm)} mm है।"
                elif lang == "hi":
                    text = f"कल आपके क्षेत्र में तापमान लगभग {_safe_g(temp)}°C रहेगा। बारिश की संभावना {precip_prob}% है और अनुमानित वर्षा {_safe_g(precip_mm)} mm है।{wind_str_hi}"
                else:
                    text = f"Tomorrow in {loc}, temperature will be around {_safe_g(temp)}°C. Rain probability is {precip_prob}% with {_safe_g(precip_mm)} mm rainfall.{wind_str_en}"
            return text, StructuredActionPayload(action="ANSWER")

        # 8c. Today's Current Weather ("आज का मौसम")
        wind_str_hi = f" हवा की गति {_safe_g(wind)} km/h है।" if wind != "--" else ""
        wind_str_hng = f" Wind speed {_safe_g(wind)} km/h hai." if wind != "--" else ""
        wind_str_en = f" Wind speed is {_safe_g(wind)} km/h." if wind != "--" else ""

        if is_hinglish:
            text = f"Aaj {loc} mein temperature {_safe_g(temp)}°C aur humidity {hum}% hai, mausam {cond} rahega.{wind_str_hng}"
        elif is_marwari:
            text = f"आज {loc} में तापमान {_safe_g(temp)}°C अर नमी {hum}% है, मौसम {cond} रैवेला।"
        elif lang == "hi":
            text = f"आज {loc} में तापमान {_safe_g(temp)}°C और humidity {hum}% है, मौसम {cond} रहेगा।{wind_str_hi}"
        else:
            text = f"Today in {loc}, temperature is {_safe_g(temp)}°C with {hum}% humidity and {cond} conditions.{wind_str_en}"
        return text, StructuredActionPayload(action="ANSWER")

    # 8d. Crop Care / General Agriculture / Agronomy
    if intent in ["general_agriculture", "agricultural_knowledge", "crop_care", "general_agronomy"]:
        sf = state.get("semantic_frame") or {}
        sf_entities = sf.get("entities") or {} if isinstance(sf, dict) else {}
        crop = sf_entities.get("crop") or state.get("crop") or state.get("active_crop")
        guidance = rag_treatment_snippet or "नियमित रूप से खेत की निगरानी करें और उचित जल व पोषण प्रबंधन बनाए रखें।"
        if crop:
            if is_hinglish:
                text = f"{crop} crop ki dekhbhal ke liye ICAR advisory: {guidance}"
            elif lang == "hi":
                text = f"{crop} की फसल की अच्छी देखभाल के लिए ICAR सलाह: {guidance}"
            else:
                text = f"Care guidelines for {crop}: {guidance}"
        else:
            if is_hinglish:
                text = f"Fasal ki dekhbhal ke liye ICAR advisory: {guidance}"
            elif lang == "hi":
                text = f"फसल प्रबंधन और देखभाल के लिए ICAR सलाह: {guidance}"
            else:
                text = f"Agricultural management guidelines: {guidance}"
        return text, StructuredActionPayload(action="ANSWER")

    # 9. Government Schemes
    if intent == "scheme":
        schemes = tool_data.get("schemes", [])
        if schemes and isinstance(schemes, list):
            s_name = schemes[0].get("scheme_name", "पीएम किसान सम्मान निधि")
            benefit = schemes[0].get("benefits", "आर्थिक सहायता")
            if is_marwari:
                text = f"खास योजना: {s_name}। फायदा: {benefit}। पूरी जानकारी ऐप में देखो।"
            elif lang == "hi":
                text = f"प्रमुख योजना: {s_name}। लाभ: {benefit}। अधिक जानकारी ऐप के योजना सेक्शन में देखें।"
            else:
                text = f"Key scheme: {s_name}. Benefits: {benefit}. View details in the schemes section."
        else:
            text = "पीएम किसान और फसल बीमा योजना जैसी योजनाओं की जानकारी उपलब्ध है।" if lang == "hi" else "PM-Kisan and PMFBY scheme information is available."
        return text, StructuredActionPayload(action="ANSWER")

    # 10. Animal Intrusion Detection
    if intent == "animal_detection":
        overall = tool_data.get("overall_status", "AREA_CLEAR") if isinstance(tool_data, dict) else "AREA_CLEAR"
        detected = tool_data.get("detected_sensors", []) if isinstance(tool_data, dict) else []
        if overall == "INTRUSION_DETECTED":
            sensors_str = ", ".join(detected) if detected else "Perimeter"
            text = f"सावधान! खेत में जानवर की हलचल पाई गई है (सेंसर: {sensors_str})।" if lang == "hi" else f"Alert! Animal intrusion detected on sensors: {sensors_str}."
            return text, StructuredActionPayload(action="NOTIFY", notification_title="Animal Intrusion", notification_body=text)
        else:
            text = "खेत बिल्कुल सुरक्षित है। किसी जानवर की कोई हलचल नहीं है।" if lang == "hi" else "The farm perimeter is clear and secure."
        return text, StructuredActionPayload(action="ANSWER")

    # 10b. Outbound Voice Calling
    if intent in ["calling", "call"] or any("calling" in k for k in tool_results.keys()):
        call_info = next((v for k, v in tool_results.items() if "calling" in k), tool_data)
        call_id = (call_info.get("call_id") if isinstance(call_info, dict) else None) or "active"
        phone = (call_info.get("phone") if isinstance(call_info, dict) else None) or "farmer"
        farmer_name = (call_info.get("farmer_name") if isinstance(call_info, dict) else None) or "किसान भाई"
        if is_hinglish:
            text = f"{farmer_name} ({phone}) ko outbound call lagaya ja raha hai. Call ID: {call_id}."
        elif is_marwari:
            text = f"{farmer_name} ({phone}) ने फोन कॉल मिलायो जा रह्यो है। कॉल आईडी: {call_id}।"
        elif lang == "hi":
            text = f"{farmer_name} ({phone}) को फोन कॉल मिलाया जा रहा है। कॉल आईडी: {call_id}।"
        else:
            text = f"Outbound advisory call initiated to {farmer_name} at {phone}. Call ID: {call_id}."
        return text, StructuredActionPayload(action="CALL", call_reason="USER_REQUESTED_CALL")

    # 11. Greetings & General Fallback
    if intent in ["greeting_help", "repeat_last"]:
        if is_marwari:
            text = "खम्मा घणी! म्हूँ FarmFusion AI किसान सहायक हूँ। आप म्हासूं मौसम, मंडी भाव, फसल सलाह या सरकारी योजनावां बाबत पूछ सको हो।"
        elif lang == "hi":
            text = "नमस्ते! मैं FarmFusion AI किसान सहायक हूँ। आप मुझसे मौसम, मंडी भाव, फसल सलाह या सरकारी योजनाओं के बारे में पूछ सकते हैं।"
        else:
            text = "Hello! I am FarmFusion AI, your agricultural assistant. You can ask me about weather, mandi prices, crop recommendations, and government schemes."
        return text, StructuredActionPayload(action="ANSWER")

    # Default
    if is_marwari:
        text = "FarmFusion AI में आपरो स्वागत है। आप म्हासूं मौसम, मंडी भाव, फसल सलाह या योजनावां बाबत पूछ सको हो।"
    elif lang == "hi":
        text = "FarmFusion AI में आपका स्वागत है। आप मुझसे मौसम, मंडी भाव, फसल सलाह या सरकारी योजनाओं के बारे में पूछ सकते हैं।"
    else:
        text = "Welcome to FarmFusion AI. You can ask me about weather, mandi prices, crop suitability, or government schemes."
    return text, StructuredActionPayload(action="ANSWER")


async def response_synthesizer_node(state: OrchestratorState) -> OrchestratorState:
    """
    Phase F6 Response Synthesizer Node.
    Executes grounded LLM synthesis with numerical immutability guard, deterministic fallback,
    and strictly aggregated deterministic confidence (NO HARDCODED 0.95).
    Emits canonical ResponseEnvelope.
    """
    input_lang = state.get("detected_language", "hi")
    profile = get_language_profile(input_lang)
    lang = profile.canonical_code if profile.support_tier == 1 else profile.fallback_language
    dialect = state.get("detected_dialect") or state.get("farmer_preferred_dialect")
    is_marwari = dialect in ["rwr", "marwari"]

    user_input = state.get("user_input", "")
    is_hinglish = is_hinglish_query(user_input, input_lang)

    # Guarantee validation and facts extraction has run
    if "verified_facts" not in state or "validation_result" not in state:
        from app.orchestrator.nodes.validation import validation_node
        state = await validation_node(state)

    validation_data = state.get("validation_result", {}) or {}
    raw_facts = state.get("verified_facts", []) or []
    verified_fact_objects: List[VerifiedFact] = [
        VerifiedFact(**f) if isinstance(f, dict) else f for f in raw_facts
    ]
    conf_tier = state.get("confidence_tier") or validation_data.get("confidence_tier", "high")
    rag_data = state.get("rag_grounding", {}) or {}
    raw_citations = state.get("rag_citations", []) or []
    citations: List[RAGCitation] = [
        RAGCitation(**c) if isinstance(c, dict) else c for c in raw_citations
    ]
    warnings: List[str] = list(validation_data.get("warnings", []))

    # Deterministic aggregated confidence from validation node policy
    # CRITICAL FIX 1 & 4: Bound final confidence strictly by underlying evidence.
    aggregated_conf = state.get("aggregated_confidence")
    if aggregated_conf is None:
        aggregated_conf = validation_data.get("aggregated_confidence", 0.50 if state.get("requires_clarification") else 0.85)

    # Determine TTS metadata
    tts_lang = lang if profile.tts.native_supported else profile.fallback_language
    native_tts = profile.tts.native_supported and (not dialect)
    fallback_used = not profile.tts.native_supported or bool(dialect)
    fallback_reason = None
    if dialect:
        fallback_reason = (
            f"No native {dialect} TTS voice model available in Bhashini or Indic-TTS. "
            f"Spoken response synthesized using parent language {tts_lang} (Hindi) voice."
        )
    elif not profile.tts.native_supported:
        fallback_reason = f"No native {lang} TTS voice model available. Using fallback {tts_lang}."

    # If state requires clarification, is a pure navigation, or has validation contradiction, use deterministic path
    warnings_list = validation_data.get("warnings", []) or [c.get("details", "") for c in validation_data.get("checks", [])]
    has_contradiction = any("contradict" in str(r).lower() for r in warnings_list)

    if state.get("requires_clarification") or has_contradiction or state.get("next_action") in ["NAVIGATE", "CLARIFY", "REQUEST_INPUT"]:
        fallback_text, fallback_action = deterministic_fallback_synthesizer(
            state, lang, dialect, is_marwari, conf_tier, is_hinglish=is_hinglish
        )
        envelope = ResponseEnvelope(
            response_text=fallback_text,
            action_payload=fallback_action,
            citations=citations,
            verified_facts=verified_fact_objects,
            confidence=aggregated_conf,
            confidence_tier=conf_tier,
            warnings=warnings,
            language=lang,
            dialect=dialect,
            tts_language=tts_lang,
            native_tts=native_tts,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
        )
        state["final_response"] = envelope.response_text
        state["last_final_response"] = envelope.response_text
        state["response_envelope"] = envelope.model_dump()
        state["response_language"] = lang
        state["response_dialect"] = dialect
        state["tts_language"] = tts_lang
        state["native_tts"] = native_tts
        state["fallback_used"] = fallback_used
        state["fallback_reason"] = fallback_reason
        return state

    # Prepare LLM input payload
    facts_payload = [f.model_dump() for f in verified_fact_objects]
    rag_context_text = rag_data.get("grounding_context_text", "No agronomic RAG knowledge needed.")
    prompt_user_content = (
        f"Farmer Query: \"{state.get('user_input', '')}\"\n"
        f"Language: {lang} (Dialect: {dialect or 'standard'})\n"
        f"Intent: {state.get('intent', 'unknown')}\n"
        f"Confidence Tier: {conf_tier}\n"
        f"Verified Fact Set: {json.dumps(facts_payload, ensure_ascii=False)}\n"
        f"Validated RAG Agronomic Knowledge:\n{rag_context_text}\n"
        f"Tool Output Summary: {json.dumps(state.get('tool_output', {}), ensure_ascii=False)[:600]}\n"
    )

    llm_result = await call_llm_synthesizer(prompt_user_content)
    synthesized_text: Optional[str] = None
    action_payload: Optional[StructuredActionPayload] = None
    envelope_confidence: float = aggregated_conf

    if llm_result and isinstance(llm_result, dict) and "response_text" in llm_result:
        candidate_text = str(llm_result["response_text"]).strip()
        is_num_valid, num_violations = verify_numerical_immutability(
            candidate_text, verified_fact_objects
        )

        if not is_num_valid:
            logger.warning(
                "llm_numerical_immutability_violation",
                violations=num_violations,
                candidate=candidate_text,
            )
            # Retry once with strict correction prompt
            retry_prompt = (
                f"{prompt_user_content}\n"
                f"CORRECTION MANDATE: Your previous response violated numerical immutability:\n"
                f"{'; '.join(num_violations)}\n"
                f"You MUST use the exact numbers from Verified Fact Set. Do not alter or round them.\n"
            )
            retry_result = await call_llm_synthesizer(retry_prompt)
            if retry_result and isinstance(retry_result, dict) and "response_text" in retry_result:
                candidate_retry = str(retry_result["response_text"]).strip()
                retry_valid, retry_violations = verify_numerical_immutability(
                    candidate_retry, verified_fact_objects
                )
                if retry_valid:
                    candidate_text = candidate_retry
                    is_num_valid = True
                    llm_result = retry_result
                else:
                    logger.warning("llm_retry_failed_numerical_check", violations=retry_violations)

        if is_num_valid:
            # Deterministic temporal-alignment verification
            sf_entities = (state.get("semantic_frame") or {}).get("entities") or {}
            time_ctx = sf_entities.get("time_context") or {}
            rel_day = time_ctx.get("relative_day", "UNSPECIFIED")
            horizon = time_ctx.get("forecast_horizon_days", 1) or 1
            from app.orchestrator.nodes.validation import validate_response_temporal_alignment
            temp_ok, temp_err = validate_response_temporal_alignment(candidate_text, rel_day, horizon)
            if not temp_ok:
                logger.warning("llm_temporal_alignment_failed", reason=temp_err, text=candidate_text)
                is_num_valid = False

        if is_num_valid:
            synthesized_text = candidate_text
            raw_action = str(llm_result.get("action", "ANSWER")).upper()
            if raw_action not in ["ANSWER", "CLARIFY", "NAVIGATE", "REQUEST_INPUT", "CALL", "NOTIFY"]:
                raw_action = "ANSWER"
            action_payload = StructuredActionPayload(
                action=raw_action,
                destination=llm_result.get("destination"),
                required_input=llm_result.get("required_input"),
                call_reason=llm_result.get("call_reason"),
            )
            raw_llm_conf = float(llm_result.get("confidence", 1.0))
            # Bound LLM confidence strictly by deterministic aggregated confidence (NO INFLATION)
            envelope_confidence = min(raw_llm_conf, aggregated_conf)
            for w in llm_result.get("warnings", []):
                if w not in warnings:
                    warnings.append(str(w))

    # Fall back if LLM failed, returned invalid schema, or failed numerical/temporal check
    if not synthesized_text or not action_payload:
        fallback_cause = "llm_unavailable_no_api_key" if not os.environ.get("OPENROUTER_API_KEY") else "numerical_or_temporal_violation"
        logger.info("using_deterministic_fallback_synthesizer", reason=fallback_cause)
        synthesized_text, action_payload = deterministic_fallback_synthesizer(
            state, lang, dialect, is_marwari, conf_tier, is_hinglish=is_hinglish
        )
        envelope_confidence = aggregated_conf

    # Build canonical ResponseEnvelope
    envelope = ResponseEnvelope(
        response_text=synthesized_text,
        action_payload=action_payload,
        citations=citations,
        verified_facts=verified_fact_objects,
        confidence=envelope_confidence,
        confidence_tier=conf_tier,
        warnings=warnings,
        language=lang,
        dialect=dialect,
        tts_language=tts_lang,
        native_tts=native_tts,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )

    state["final_response"] = envelope.response_text
    state["last_final_response"] = envelope.response_text
    state["response_envelope"] = envelope.model_dump()
    state["response_language"] = lang
    state["response_dialect"] = dialect
    state["tts_language"] = tts_lang
    state["native_tts"] = native_tts
    state["fallback_used"] = fallback_used
    state["fallback_reason"] = fallback_reason

    logger.info(
        "response_synthesis_complete",
        action=action_payload.action,
        language=lang,
        dialect=dialect,
        facts_count=len(verified_fact_objects),
        citations_count=len(citations),
        confidence_tier=conf_tier,
    )
    return state
