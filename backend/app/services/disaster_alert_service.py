"""
DisasterAlertService - Deterministic Alert Decision Engine and Vobiz Telephony Bridge.
Enforces strict hazard thresholds, stateful deduplication, escalation detection,
and non-blocking asynchronous dispatch via existing KisanCallingService.
"""

import asyncio
import time
import structlog
from typing import Dict, Any, Optional, Tuple

from app.schemas.calling import KisanCallRequest
from app.calling_agent.service import kisan_calling_service
from app.core.language import resolve_language_code

logger = structlog.get_logger(__name__)

# 5-minute cooldown for same disaster hazard to same farmer
COOLDOWN_SECONDS = 300

# Severity ranking for escalation logic
SEVERITY_RANKS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

# Localized Voice Alert Templates
VOICE_MESSAGES = {
    "Flood Risk": {
        "hi": "फार्मफ्यूजन आपातकालीन चेतावनी। अगले 24 से 48 घंटों में आपके खेत के लिए भारी बाढ़ का गंभीर खतरा है। कृपया अपने कृषि उपकरण और पशुधन को तुरंत ऊंचे स्थान पर ले जाएं और खेत की जल निकासी खोलें।",
        "gu": "ફાર્મફ્યુઝન કટોકટી ચેતવણી. આગામી 24 થી 48 કલાકમાં તમારા ખેતરમાં ભારે પૂરનું જોખમ છે. કૃપા કરીને પશુધન અને સાધનોને ઊંચા સ્થળે ખસેડો અને પાણીના નિકાલની વ્યવસ્થા કરો.",
        "mr": "फार्मफ्युजन आणीबाणी इशारा. पुढील २४ ते ४८ तासांत आपल्या शेतासाठी महापुराचा गंभीर धोका आहे. कृपया आपली जनावरे व कृषी यंत्रसामग्री तातडीने उंच सुरक्षित ठिकाणी हलवा.",
        "pa": "ਫਾਰਮਫਿਊਜ਼ਨ ਸੰਕਟਕਾਲੀਨ ਚੇਤਾਵਨੀ। ਅਗਲੇ 24 ਤੋਂ 48 ਘੰਟਿਆਂ ਵਿੱਚ ਭਾਰੀ ਹੜ੍ਹ ਦਾ ਖ਼ਤਰਾ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਪਸ਼ੂਆਂ ਅਤੇ ਖੇਤੀਬਾੜੀ ਉਪਕਰਣਾਂ ਨੂੰ ਤੁਰੰਤ ਉੱਚੇ ਸੁਰੱਖਿਅਤ ਸਥਾਨ 'ਤੇ ਪਹੁੰਚਾਓ।",
        "bn": "ফার্মফিউশন জরুরি সতর্কতা। আগামী ২৪ থেকে ৪৮ ঘণ্টায় আপনার জমিতে তীব্র বন্যার আশঙ্কা রয়েছে। অনুগ্রহ করে গবাদি পশু ও কৃষিজ যন্ত্রপাতি অবিলম্বে নিরাপদ উঁচু স্থানে সরিয়ে নিন।",
        "en": "FarmFusion emergency alert. Heavy rainfall has created a high flood risk for your farm in the next 24 to 48 hours. Please move equipment and livestock to higher ground immediately and clear field drainage.",
    },
    "Cyclone Risk": {
        "hi": "फार्मफ्यूजन तूफान चेतावनी। अगले 24 से 48 घंटों में आपके क्षेत्र में तेज चक्रवाती हवाओं और तूफान का गंभीर खतरा है। कृपया अपनी कटी हुई फसल सुरक्षित ढकें और लंबी फसलों को सहारा दें।",
        "gu": "ફાર્મફ્યુઝન વાવાઝોડાની ચેતવણી. આગામી 24 થી 48 કલાકમાં તેજ ચક્રવાતી પવનનું ગંભીર જોખમ છે. કૃપા કરીને લણેલા પાકને સુરક્ષિત ઢાંકો અને ખેતરમાં સાવચેતી રાખો.",
        "mr": "फार्मफ्युजन वादळ इशारा. पुढील २४ ते ४८ तासांत तीव्र चक्रीवादळाचा धोका निर्माण झाला आहे. कृपया काढणी केलेले पीक त्वरित सुरक्षित जागी ठेवा आणि शेतात दक्षता बाळगा.",
        "pa": "ਫਾਰਮਫਿਊਜ਼ਨ ਚੱਕਰਵਾਤ ਚੇਤਾਵਨੀ। ਅਗਲੇ 24 ਤੋਂ 48 ਘੰਟਿਆਂ ਵਿੱਚ ਭਾਰੀ ਤੂਫਾਨ ਦਾ ਖਤਰਾ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਫਸਲ ਅਤੇ ਉਪਕਰਣ ਸੁਰੱਖਿਅਤ ਥਾਂ ਰੱਖੋ।",
        "bn": "ফার্মফিউশন ঘূর্ণিঝড় সতর্কতা। আগামী ২৪ থেকে ৪৮ ঘণ্টায় তীব্র ঘূর্ণিঝড়ের প্রবল আশঙ্কা রয়েছে। দয়া করে কাটা ফসল নিরাপদে ঢেকে রাখুন এবং মাঠে প্রবেশ এড়িয়ে চলুন।",
        "en": "FarmFusion cyclone alert. Severe cyclonic wind gusts are expected in your area in the next 24 to 48 hours. Please secure loose structures, support standing crops, and protect harvested produce.",
    },
    "Drought Risk": {
        "hi": "फार्मफ्यूजन मौसम सूचना। अत्यधिक तापमान और शुष्कता के कारण सूखे जैसी स्थिति उत्पन्न हो रही है। कृपया सुबह या शाम के समय ड्रिप सिंचाई करें और फसल में मल्चिंग अपनाएं।",
        "gu": "ફાર્મફ્યુઝન હવામાન ચેતવણી. વધુ પડતી ગરમી અને પાણીની અછતને લીધે જમીનમાં ભેજ જાળવવા હળવું પિયત આપો અને મલ્ચિંગનો ઉપયોગ કરો.",
        "mr": "फार्मफ्युजन दुष्काळ सल्ला. तीव्र उष्णतेमुळे पिकांचे संरक्षण करण्यासाठी ठिबक सिंचनाचा वापर करा व जमिनीतील ओलावा टिकवून ठेवा.",
        "pa": "ਫਾਰਮਫਿਊਜ਼ਨ ਮੌਸਮ ਸਲਾਹ। ਗਰਮੀ ਅਤੇ ਨਮੀ ਦੀ ਘਾਟ ਕਾਰਨ ਤੁਪਕਾ ਸਿੰਚਾਈ ਦਾ ਪ੍ਰਯੋਗ ਕਰੋ ਅਤੇ ਫਸਲਾਂ ਨੂੰ ਲੂ ਤੋਂ ਬਚਾਓ।",
        "bn": "ফার্মফিউশন খরা সতর্কতা। তীব্র তাপপ্রবাহের কারণে জমিতে আর্দ্রতা বজায় রাখতে ড্রিপ সেচ প্রয়োগ করুন।",
        "en": "FarmFusion drought warning. Prolonged heat and moisture deficit detected. Conserve soil moisture using mulch and schedule micro-irrigation during early morning hours.",
    },
}


class DisasterAlertService:
    """
    Evaluates disaster predictions, enforces stateful deduplication,
    determines if farmer should be telephoned, and triggers Vobiz asynchronously.
    """

    def __init__(self):
        # Memory cache for alert tracking: key -> (timestamp, severity, call_id)
        self.alert_history: Dict[str, Tuple[float, str, Optional[str]]] = {}

    def _build_dedup_key(self, phone: str, disaster_type: str, location: str) -> str:
        loc_norm = (location or "default").strip().lower()
        return f"{phone}:{disaster_type}:{loc_norm}"

    def evaluate_alert_decision(
        self,
        prediction: Dict[str, Any],
        farmer_phone: Optional[str],
        farmer_name: Optional[str],
        location_name: Optional[str],
        language: Optional[str] = "hi"
    ) -> Dict[str, Any]:
        """
        Deterministic alert policy:
        - LOW: Display only
        - MEDIUM: Display warning banner
        - HIGH: Warning banner + Eligible for Vobiz call
        - CRITICAL: Emergency banner + Priority Vobiz call
        
        Handles deduplication:
        - HIGH -> HIGH within 300s: Suppressed
        - HIGH -> CRITICAL: Escalation allowed immediately
        - LOW/MEDIUM -> HIGH: Allowed immediately
        """
        disaster_type = prediction["disaster_type"]
        risk_level = prediction["risk_level"]
        risk_score = prediction["risk_score"]
        confidence = prediction["confidence"]
        trigger_factors = prediction.get("trigger_factors", [])

        # Low or Medium risks are display-only
        if risk_level not in ["HIGH", "CRITICAL"]:
            return {
                "should_alert": False,
                "severity": risk_level,
                "reason": f"Risk level {risk_level} (score {risk_score}) does not exceed outbound calling threshold (>=75.0).",
                "alert_status": "DISPLAY_ONLY",
                "call_id": None,
                "alert_message": None,
                "cooldown_remaining_seconds": None
            }

        # Validate farmer phone
        if not farmer_phone or not farmer_phone.strip():
            logger.info("disaster_alert_no_phone", disaster=disaster_type, level=risk_level)
            return {
                "should_alert": False,
                "severity": risk_level,
                "reason": f"High risk {disaster_type} detected (score {risk_score}), but no verified farmer phone number is available.",
                "alert_status": "NO_PHONE",
                "call_id": None,
                "alert_message": None,
                "cooldown_remaining_seconds": None
            }

        try:
            normalized_phone = kisan_calling_service.validate_and_normalize_phone(farmer_phone)
        except ValueError as val_err:
            logger.warning("disaster_alert_invalid_phone", phone=farmer_phone, error=str(val_err))
            return {
                "should_alert": False,
                "severity": risk_level,
                "reason": f"Farmer phone number '{farmer_phone}' failed E.164 validation: {val_err}",
                "alert_status": "NO_PHONE",
                "call_id": None,
                "alert_message": None,
                "cooldown_remaining_seconds": None
            }

        # Deduplication & Escalation Check
        dedup_key = self._build_dedup_key(normalized_phone, disaster_type, location_name or "Farm")
        now = time.time()
        last_record = self.alert_history.get(dedup_key)

        if last_record:
            last_time, last_severity, last_call_id = last_record
            elapsed = now - last_time
            last_rank = SEVERITY_RANKS.get(last_severity, 1)
            current_rank = SEVERITY_RANKS.get(risk_level, 1)

            # If within cooldown and severity has NOT escalated
            if elapsed < COOLDOWN_SECONDS and current_rank <= last_rank:
                remaining = int(COOLDOWN_SECONDS - elapsed)
                logger.info(
                    "disaster_alert_cooldown_suppressed",
                    phone=normalized_phone,
                    disaster=disaster_type,
                    remaining=remaining
                )
                return {
                    "should_alert": False,
                    "severity": risk_level,
                    "reason": (
                        f"Duplicate alert suppressed: A {last_severity} alert was dispatched to {normalized_phone} "
                        f"{int(elapsed)}s ago. Cooldown active for {remaining}s."
                    ),
                    "alert_status": "SKIPPED_COOLDOWN",
                    "call_id": last_call_id,
                    "alert_message": None,
                    "cooldown_remaining_seconds": remaining
                }
            elif elapsed < COOLDOWN_SECONDS and current_rank > last_rank:
                logger.info(
                    "disaster_alert_escalation_detected",
                    phone=normalized_phone,
                    disaster=disaster_type,
                    from_severity=last_severity,
                    to_severity=risk_level
                )

        # Build concise localized alert message
        alert_msg = self._generate_localized_alert_message(disaster_type, language)

        return {
            "should_alert": True,
            "severity": risk_level,
            "reason": (
                f"Severe {disaster_type} (score {risk_score:.1f}, level {risk_level}) "
                f"breached alert threshold. Outbound voice alert qualified for {normalized_phone}."
            ),
            "alert_status": "ELIGIBLE",
            "call_id": None,
            "alert_message": alert_msg,
            "cooldown_remaining_seconds": 0,
            "_normalized_phone": normalized_phone,
            "_dedup_key": dedup_key
        }

    def _generate_localized_alert_message(self, disaster_type: str, language: Optional[str]) -> str:
        lang_ctx = resolve_language_code(language or "hi")
        target_lang = lang_ctx.canonical_code

        hazard_dict = VOICE_MESSAGES.get(disaster_type, VOICE_MESSAGES["Flood Risk"])
        return hazard_dict.get(target_lang, hazard_dict.get("en", hazard_dict["hi"]))

    async def dispatch_vobiz_alert_async(
        self,
        decision: Dict[str, Any],
        farmer_name: str,
        location_name: Optional[str],
        crop_name: Optional[str],
        language: str
    ) -> Optional[str]:
        """
        Executes outbound call via KisanCallingService asynchronously.
        Records call in dedup cache.
        """
        normalized_phone = decision.get("_normalized_phone")
        dedup_key = decision.get("_dedup_key")
        alert_msg = decision.get("alert_message")
        severity = decision.get("severity", "HIGH")

        if not normalized_phone or not alert_msg:
            return None

        try:
            call_req = KisanCallRequest(
                phone=normalized_phone,
                farmer_name=farmer_name or "Farmer",
                call_type="weather_warning",
                language=language or "hi",
                location=location_name or "Farm",
                crop_name=crop_name,
                weather_summary=alert_msg,
                agent_instruction=(
                    f"URGENT DISASTER ALERT: Inform {farmer_name} immediately that a {severity} "
                    f"hazard has been detected for their farm. Deliver this vital message: '{alert_msg}'. "
                    f"Advise them on protective agricultural steps and reassure them calmly."
                )
            )

            # Dispatch via KisanCallingService with cooldown bypass since we handled dedup/escalation
            call_resp = await kisan_calling_service.trigger_call(call_req, bypass_cooldown=True)
            call_id = call_resp.call_id

            # Update local alert history
            if dedup_key:
                self.alert_history[dedup_key] = (time.time(), severity, call_id)

            logger.info(
                "disaster_vobiz_alert_dispatched",
                call_id=call_id,
                phone=normalized_phone,
                severity=severity
            )
            return call_id

        except Exception as exc:
            logger.error("disaster_vobiz_alert_failed", error=str(exc), phone=normalized_phone)
            return None


disaster_alert_service = DisasterAlertService()
