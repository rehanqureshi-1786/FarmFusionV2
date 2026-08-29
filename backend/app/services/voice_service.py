"""
Voice Assistant Service - intent detection and action handling.
Uses Groq as the primary model for voice reasoning.
Weather responses use real Open-Meteo data and support Hinglish.
"""
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.agents.groq_client import groq_client
from app.models.voice import (
    ActionType,
    DetectedIntent,
    IntentType,
    LanguageType,
    VoiceQueryRequest,
    VoiceQueryResponse,
)
from app.services.weather_service import WeatherService


logger = logging.getLogger(__name__)


class VoiceService:
    async def detect_intent(self, query: str, language_hint: Optional[str] = None) -> DetectedIntent:
        system_prompt = """You are FarmFusion AI, a premium agricultural assistant for Indian farmers.
You understand English, Hindi, Hinglish, and regional Indian languages like Marathi, Gujarati, Punjabi, and Telugu.

Your goal is to extract the user's intent and entities to help them manage their farm.

Return ONLY valid JSON with this structure:
{
  "intent": "get_weather|get_mandi_price|crop_prediction|disease_detection|general_query|unknown",
  "crop": "lowercase english crop name or null",
  "location": "location in lowercase english or auto",
  "language": "hi|en|hi-en|mr|gu|pa|te|ta|kn|ml|bn|unknown",
  "confidence": 0.0,
  "extracted_entities": {
    "timeframe": "today|tomorrow|next week|last week|null",
    "specific_info": "short extracted detail or null"
  }
}

Rules:
1. Weather intent includes queries about rain, forecast, temperature, humidity, wind.
2. Mandi Price intent includes questions about rates, prices, or selling crops.
3. Crop Prediction includes advice on what to sow or plant.
4. Disease Detection includes mentions of pests, yellow leaves, dying plants, or "checking" a plant.
5. Hinglish (Hindi written in Roman script) must be tagged as 'hi-en'.
6. If the user asks in a regional language (Marathi, Gujarati, Punjabi, Telugu), tag it correctly (mr, gu, pa, te).
7. If unsure, pick the closest likely intent based on keywords.
"""
        try:
            response = await self._chat_completion(
                system_prompt=system_prompt,
                user_prompt=query,
                temperature=0.2,
                max_tokens=400
            )

            if not response.get("success"):
                return self._create_fallback_intent(query, language_hint)

            content = response.get("content", "").strip()
            content = re.sub(r"^```json\s*", "", content)
            content = re.sub(r"^```\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            parsed = json.loads(content)

            return DetectedIntent(
                intent=IntentType(parsed.get("intent", "unknown")),
                crop=parsed.get("crop"),
                location=parsed.get("location", "auto"),
                language=LanguageType(parsed.get("language", language_hint or "unknown")),
                confidence=float(parsed.get("confidence", 0.5)),
                extracted_entities=parsed.get("extracted_entities", {}) or {}
            )
        except Exception as exc:
            logger.error("Intent detection failed: %s", exc)
            return self._create_fallback_intent(query, language_hint)

    def _create_fallback_intent(self, query: str, language_hint: Optional[str] = None) -> DetectedIntent:
        query_lower = query.lower()

        # Keyword mapping for multiple languages
        mandi_keywords = ["rate", "price", "bhav", "daam", "रेट", "भाव", "कीमत", "दर", "ભાવ", "ਕੀਮਤ", "ధర"]
        weather_keywords = ["mausam", "weather", "baarish", "rain", "मौसम", "पाऊस", "વરસાદ", "ਮੀਂਹ", "వర్షం"]
        crop_keywords = ["fasal", "crop", "beej", "बीज", "फसल", "ਪੀਕ", "పంట", "વાવેતર"]
        disease_keywords = ["bimari", "disease", "rog", "kida", "रोग", "बीमारी", "रोग", "ਰੋਗ", "వ్యాధి"]

        if any(word in query_lower for word in mandi_keywords):
            intent = IntentType.GET_MANDI_PRICE
        elif any(word in query_lower for word in weather_keywords):
            intent = IntentType.GET_WEATHER
        elif any(word in query_lower for word in crop_keywords):
            intent = IntentType.CROP_PREDICTION
        elif any(word in query_lower for word in disease_keywords):
            intent = IntentType.DISEASE_DETECTION
        else:
            intent = IntentType.GENERAL_QUERY

        lang = self._normalize_language(language_hint) if language_hint else self._detect_language_fallback(query)
        return DetectedIntent(
            intent=intent,
            crop=None,
            location="auto",
            language=lang,
            confidence=0.5,
            extracted_entities={"timeframe": self._extract_timeframe(query_lower)}
        )

    def _detect_language_fallback(self, query: str) -> LanguageType:
        # Script detection
        if re.search(r"[\u0900-\u097F]", query): # Devanagari (Hindi/Marathi)
            return LanguageType.HINDI
        if re.search(r"[\u0A00-\u0A7F]", query): # Gurmukhi (Punjabi)
            return LanguageType.PUNJABI
        if re.search(r"[\u0A80-\u0AFF]", query): # Gujarati
            return LanguageType.GUJARATI
        if re.search(r"[\u0C00-\u0C7F]", query): # Telugu
            return LanguageType.TELUGU
        
        hinglish_patterns = ["hai", "ka", "ki", "ko", "mein", "se", "hain", "kya", "nahi", "agle", "hafte", "pichhle"]
        if any(pattern in query.lower() for pattern in hinglish_patterns):
            return LanguageType.HINGLISH
        return LanguageType.ENGLISH

    async def execute_action(
        self,
        intent: DetectedIntent,
        query: str,
        request: VoiceQueryRequest
    ) -> Dict[str, Any]:
        handlers = {
            IntentType.GET_WEATHER: self._handle_weather,
            IntentType.GET_MANDI_PRICE: self._handle_mandi_price,
            IntentType.CROP_PREDICTION: self._handle_crop_prediction,
            IntentType.DISEASE_DETECTION: self._handle_disease_detection,
            IntentType.GENERAL_QUERY: self._handle_general_query,
            IntentType.UNKNOWN: self._handle_unknown,
        }
        handler = handlers.get(intent.intent, self._handle_unknown)
        return await handler(intent, query, request)

    async def _handle_weather(
        self,
        intent: DetectedIntent,
        query: str,
        request: VoiceQueryRequest
    ) -> Dict[str, Any]:
        if request.latitude is None or request.longitude is None:
            return {
                "action": ActionType.ASK_CLARIFICATION,
                "response": self._location_needed_response(intent.language),
                "data": {"missing": "coordinates"}
            }

        current = await WeatherService.get_current_weather(request.latitude, request.longitude)
        if not current.get("success"):
            return {
                "action": ActionType.ERROR,
                "response": self._weather_unavailable_response(intent.language),
                "data": {"error": current.get("error")}
            }

        forecast = await WeatherService.get_forecast(request.latitude, request.longitude, days=7)
        if not forecast.get("success"):
            return {
                "action": ActionType.ERROR,
                "response": self._weather_unavailable_response(intent.language),
                "data": {"error": forecast.get("error")}
            }

        timeline = await WeatherService.get_weather_timeline(
            request.latitude,
            request.longitude,
            forecast_days=7,
            past_days=7
        )

        weather_payload = self._build_weather_payload(
            intent=intent,
            current=current,
            forecast=forecast,
            timeline=timeline,
            requested_location=request.location
        )
        response_text = await self._generate_weather_response(intent.language, query, weather_payload)

        return {
            "action": ActionType.SHOW_RESULT,
            "response": response_text,
            "data": weather_payload
        }

    async def _handle_mandi_price(
        self,
        intent: DetectedIntent,
        query: str,
        request: VoiceQueryRequest
    ) -> Dict[str, Any]:
        from app.tools.registry import tool_registry
        crop = intent.crop or "Wheat"
        tool_res = await tool_registry.execute(
            "market_price_tool",
            {"commodity": crop, "state": request.location or "Rajasthan"}
        )
        if tool_res.data:
            price_data = {
                "crop": crop,
                "market_name": tool_res.data.get("current_price", {}).get("market", "Local Mandi"),
                "price_per_quintal": tool_res.data.get("current_price", {}).get("modal_price", 2400),
                "price_trend": "stable",
                "last_updated": datetime.now().isoformat(),
                "forecast": tool_res.data.get("forecast")
            }
            return {
                "action": ActionType.SHOW_RESULT,
                "response": self._generate_price_response(intent.language, price_data),
                "data": price_data
            }
        return {
            "action": ActionType.SHOW_RESULT,
            "response": tool_res.message,
            "data": {"crop": crop, "status": "unavailable"}
        }

    async def _handle_crop_prediction(
        self,
        intent: DetectedIntent,
        query: str,
        request: VoiceQueryRequest
    ) -> Dict[str, Any]:
        from app.tools.registry import tool_registry
        lat = request.latitude or 24.6178
        lon = request.longitude or 73.9937
        soil = intent.extracted_entities.get("soil_type") or "Sandy Soil"
        tool_res = await tool_registry.execute(
            "crop_recommendation_tool",
            {"latitude": lat, "longitude": lon, "soil_type": soil, "has_soil_report": False}
        )
        recs = []
        if tool_res.data and "recommendations" in tool_res.data:
            recs = [r.get("crop_name") for r in tool_res.data["recommendations"][:3]]
        prediction_data = {
            "recommended_crops": recs or ["Groundnut (Peanut)", "Pearl Millet (Bajra)", "Green Gram (Moong)"],
            "soil_type": soil,
            "confidence": 0.90,
            "reasoning": tool_res.message,
            "provenance": tool_res.provenance.model_dump()
        }
        return {
            "action": ActionType.SHOW_RESULT,
            "response": self._generate_crop_prediction_response(intent.language, prediction_data),
            "data": prediction_data
        }

    async def _handle_disease_detection(
        self,
        intent: DetectedIntent,
        query: str,
        request: VoiceQueryRequest
    ) -> Dict[str, Any]:
        response_text = self._generate_disease_response(intent.language)
        return {
            "action": ActionType.OPEN_CAMERA,
            "response": response_text,
            "data": {"action": "open_camera", "message": response_text}
        }

    async def _handle_general_query(
        self,
        intent: DetectedIntent,
        query: str,
        request: VoiceQueryRequest
    ) -> Dict[str, Any]:
        system_prompt = """You are a helpful farming assistant for Indian farmers.
Answer simply and practically in at most 3 short sentences.
Return the answer in the SAME language as the farmer's question.
Supported languages: Hindi (hi), Marathi (mr), Gujarati (gu), Punjabi (pa), Telugu (te), English (en), Hinglish (hi-en).
Keep the tone helpful and professional."""

        response = await self._chat_completion(
            system_prompt=system_prompt,
            user_prompt=f"Farmer language: {self._response_language(intent.language).value}\nFarmer query: {query}",
            temperature=0.5,
            max_tokens=250
        )

        answer = response.get("content") if response.get("success") else self._get_fallback_response(intent.language)
        
        # Consistent language for TTS readback
        tts_lang = intent.language
        if tts_lang == LanguageType.HINGLISH:
            tts_lang = LanguageType.HINDI

        return {
            "action": ActionType.SHOW_RESULT,
            "response": answer,
            "data": {"query": query},
            "detected_language": tts_lang # Return hi instead of hi-en for Hinglish to aid TTS
        }

    async def _handle_unknown(
        self,
        intent: DetectedIntent,
        query: str,
        request: VoiceQueryRequest
    ) -> Dict[str, Any]:
        return {
            "action": ActionType.ASK_CLARIFICATION,
            "response": self._get_fallback_response(intent.language),
            "data": {"suggestions": self._get_follow_up_suggestions(IntentType.UNKNOWN)}
        }

    async def process_query(self, request: VoiceQueryRequest) -> VoiceQueryResponse:
        try:
            intent = await self.detect_intent(request.query, request.language_hint)
            action_result = await self.execute_action(intent, request.query, request)
            return VoiceQueryResponse(
                intent=intent.intent,
                action=action_result["action"],
                response=action_result["response"],
                data=action_result.get("data"),
                detected_language=self._response_language(intent.language),
                confidence=intent.confidence,
                follow_up_suggestions=self._get_follow_up_suggestions(intent.intent),
                timestamp=datetime.now().isoformat()
            )
        except Exception as exc:
            logger.error("Error processing voice query: %s", exc)
            return self._create_error_response(request)

    async def _generate_weather_response(
        self,
        language: LanguageType,
        query: str,
        weather_payload: Dict[str, Any]
    ) -> str:
        timeframe = weather_payload.get("timeframe") or "today"
        system_prompt = """You are FarmFusion weather assistant for Indian farmers.
Use the provided real weather data only.
Answer in Hinglish if the farmer language is hi-en.
Answer in Hindi if the farmer language is hi.
Answer in English if the farmer language is en.
Answer in Marathi if the farmer language is mr.
Answer in Punjabi if the farmer language is pa.
Answer in Telugu if the farmer language is te.
Keep it practical, short, and direct.
If the query asks about rain probability, mention the most relevant day.
If the query asks about last week, summarize only the past week data.
If the query asks about next week, summarize only the next week data.
Do not invent data beyond the provided weather JSON."""

        user_prompt = (
            f"Farmer query: {query}\n"
            f"Farmer language: {self._response_language(language).value}\n"
            f"Timeframe: {timeframe}\n"
            f"Weather JSON: {json.dumps(weather_payload, ensure_ascii=False)}"
        )

        response = await self._chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=220
        )
        if response.get("success") and response.get("content"):
            return response["content"].strip()

        return self._generate_weather_response_fallback(language, weather_payload)

    def _build_weather_payload(
        self,
        intent: DetectedIntent,
        current: Dict[str, Any],
        forecast: Dict[str, Any],
        timeline: Dict[str, Any],
        requested_location: Optional[str]
    ) -> Dict[str, Any]:
        timeframe = intent.extracted_entities.get("timeframe") or "today"
        rainy_days = [
            day for day in forecast.get("forecast", [])
            if float(day.get("rain_chance", 0)) >= 40 or float(day.get("precipitation_mm", 0)) > 1
        ]
        return {
            "location": requested_location or current.get("location") or "your area",
            "temperature_c": current.get("temperature_c"),
            "humidity_percent": current.get("humidity_percent"),
            "wind_speed_ms": current.get("wind_speed_ms"),
            "weather": current.get("weather"),
            "farming_advice": current.get("farming_advice"),
            "timeframe": timeframe,
            "forecast_days": forecast.get("forecast", []),
            "rainy_days": rainy_days,
            "last_week_days": timeline.get("history", []) if timeline.get("success") else [],
            "forecast_advice": forecast.get("farming_advice"),
            "source": current.get("source")
        }

    def _generate_weather_response_fallback(self, lang: LanguageType, data: Dict[str, Any]) -> str:
        location = data.get("location", "your area")
        temperature = round(float(data.get("temperature_c", 0) or 0))
        weather = data.get("weather", "weather update")
        rainy_days = data.get("rainy_days", [])
        history_days = data.get("last_week_days", [])
        timeframe = str(data.get("timeframe", "today")).lower()
        response_language = self._response_language(lang)

        if timeframe == "last week":
            rainy_history = [day for day in history_days if day.get("precipitation_mm", 0) > 0.5]
            if response_language == LanguageType.HINGLISH:
                if rainy_history:
                    return f"{location} mein pichhle hafte kuch din baarish hui thi. Sabse zyada baarish {rainy_history[0].get('date')} ke aas-paas thi."
                return f"{location} mein pichhle hafte mausam mostly dry aur stable raha."
            if response_language == LanguageType.HINDI:
                if rainy_history:
                    return f"{location} में पिछले हफ्ते कुछ दिनों में बारिश हुई थी। सबसे ज्यादा बारिश {rainy_history[0].get('date')} के आसपास रही।"
                return f"{location} में पिछले हफ्ते मौसम ज्यादातर सूखा और स्थिर रहा।"
            return f"Last week in {location}, weather stayed mostly stable."

        if timeframe == "next week":
            if rainy_days:
                first_day = rainy_days[0].get("date", "upcoming days")
                rain_chance = round(float(rainy_days[0].get("rain_chance", 0) or 0))
                if response_language == LanguageType.HINGLISH:
                    return f"{location} mein agle hafte baarish ki sambhavna hai. Sabse zyada chance {first_day} ko lagbhag {rain_chance}% hai."
                if response_language == LanguageType.HINDI:
                    return f"{location} में अगले हफ्ते बारिश की संभावना है। सबसे ज्यादा संभावना {first_day} को लगभग {rain_chance}% है।"
                return f"In {location}, rain is most likely around {first_day} with about {rain_chance}% chance."
            if response_language == LanguageType.HINGLISH:
                return f"{location} mein agle hafte tez baarish ka chance kam lag raha hai."
            if response_language == LanguageType.HINDI:
                return f"{location} में अगले हफ्ते तेज बारिश की संभावना कम दिख रही है।"
            return f"In {location}, next week does not show strong rain chances."

        if response_language == LanguageType.HINGLISH:
            return f"{location} mein abhi temperature {temperature}°C hai aur weather {weather} hai. {data.get('farming_advice', '')}".strip()
        if response_language == LanguageType.HINDI:
            return f"{location} में अभी तापमान {temperature}°C है और मौसम {weather} है। {data.get('farming_advice', '')}".strip()
        return f"In {location}, the current temperature is {temperature}°C with {weather}. {data.get('farming_advice', '')}".strip()

    async def _chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        try:
            if groq_client.is_available():
                response = await groq_client.chat_completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                if response.get("success"):
                    return response
        except Exception as e:
            logger.warning("Groq failed, using fallback: %s", e)

        return {"success": False, "error": "No AI provider available"}

    def _normalize_language(self, language_hint: str) -> LanguageType:
        try:
            return LanguageType(language_hint)
        except Exception:
            return LanguageType.UNKNOWN

    def _response_language(self, language: LanguageType) -> LanguageType:
        return LanguageType.HINGLISH if language == LanguageType.UNKNOWN else language

    def _extract_timeframe(self, query_lower: str) -> str:
        if "next week" in query_lower or "agle hafte" in query_lower or "अगले हफ्ते" in query_lower:
            return "next week"
        if "last week" in query_lower or "pichhle hafte" in query_lower or "पिछले हफ्ते" in query_lower:
            return "last week"
        if "tomorrow" in query_lower or "kal" in query_lower or "कल" in query_lower:
            return "tomorrow"
        return "today"

    def _location_needed_response(self, lang: LanguageType) -> str:
        response_language = self._response_language(lang)
        if response_language == LanguageType.HINGLISH:
            return "Weather batane ke liye mujhe aapki current location permission chahiye. Please location allow karke dobara poochhiye."
        if response_language == LanguageType.HINDI:
            return "मौसम बताने के लिए मुझे आपकी वर्तमान लोकेशन चाहिए। कृपया लोकेशन अनुमति दें और फिर पूछें।"
        return "Weather answer needs your current location permission. Please allow location and try again."

    def _weather_unavailable_response(self, lang: LanguageType) -> str:
        response_language = self._response_language(lang)
        if response_language == LanguageType.HINGLISH:
            return "Abhi real weather data available nahi hai. Thodi der baad dobara try kijiye."
        if response_language == LanguageType.HINDI:
            return "अभी वास्तविक मौसम डेटा उपलब्ध नहीं है। कृपया थोड़ी देर बाद फिर पूछें।"
        return "Real weather data is unavailable right now. Please try again in a moment."

    def _generate_price_response(self, lang: LanguageType, data: Dict[str, Any]) -> str:
        crop = data["crop"].capitalize()
        price = data["price_per_quintal"]
        response_language = self._response_language(lang)
        if response_language == LanguageType.HINGLISH:
            return f"{crop} ka current rate lagbhag {price} rupaye per quintal hai."
        if response_language == LanguageType.HINDI:
            return f"{crop} का वर्तमान भाव करीब {price} रुपये प्रति क्विंटल है।"
        return f"Current {crop} price is Rs {price} per quintal in the nearby mandi."

    def _generate_crop_prediction_response(self, lang: LanguageType, data: Dict[str, Any]) -> str:
        crops = ", ".join(data["recommended_crops"][:3])
        response_language = self._response_language(lang)
        if response_language == LanguageType.HINGLISH:
            return f"Aapki zameen ke liye behtar faslen hain: {crops}."
        if response_language == LanguageType.HINDI:
            return f"आपकी जमीन के लिए बेहतर फसलें हैं: {crops}।"
        return f"Best crops for your land are {crops}."

    def _generate_disease_response(self, lang: LanguageType) -> str:
        response_language = self._response_language(lang)
        if response_language == LanguageType.HINGLISH:
            return "Please affected plant ki ek clear photo lijiye. Camera open ho raha hai."
        if response_language == LanguageType.HINDI:
            return "कृपया प्रभावित पौधे की साफ फोटो लें। कैमरा खोला जा रहा है।"
        return "Please take a clear photo of the affected plant. Opening camera."

    def _get_fallback_response(self, lang: LanguageType) -> str:
        response_language = self._response_language(lang)
        if response_language == LanguageType.HINGLISH:
            return "Main ise clearly samajh nahi paya. Please short mein dobara poochhiye."
        if response_language == LanguageType.HINDI:
            return "मैं इसे ठीक से समझ नहीं पाया। कृपया छोटा और साफ सवाल फिर से पूछें।"
        return "I could not understand that clearly. Please ask again in a short way."

    def _get_follow_up_suggestions(self, intent: IntentType) -> List[str]:
        suggestions = {
            IntentType.GET_WEATHER: [
                "kal baarish hogi kya",
                "agle hafte baarish ki sambhavna",
                "pichhle hafte mausam kaisa tha"
            ],
            IntentType.GET_MANDI_PRICE: [
                "gehu ka bhav kya hai",
                "chawal ka rate batao",
                "padosi mandi ka rate"
            ],
            IntentType.CROP_PREDICTION: [
                "meri zameen ke liye kaunsi fasal theek hai",
                "beej ki salah do",
                "khad ki salah do"
            ],
            IntentType.UNKNOWN: [
                "aaj mausam kaisa hai",
                "gehu ka bhav kya hai",
                "kaunsi fasal lagau"
            ]
        }
        return suggestions.get(intent, suggestions[IntentType.UNKNOWN])

    def _get_mock_price(self, crop: str) -> float:
        prices = {
            "wheat": 2150,
            "rice": 1880,
            "corn": 1850,
            "cotton": 6050,
            "sugarcane": 290,
            "potato": 1250,
            "onion": 2800,
            "tomato": 1500,
            "soybean": 3900,
        }
        return prices.get(crop.lower(), 2000)

    def _create_error_response(self, request: VoiceQueryRequest) -> VoiceQueryResponse:
        language = self._normalize_language(request.language_hint or "hi-en")
        if language == LanguageType.HINDI:
            message = "कृपया फिर से कोशिश करें।"
        elif language == LanguageType.ENGLISH:
            message = "Please try again."
        else:
            message = "Please dobara try kijiye."
        return VoiceQueryResponse(
            intent=IntentType.UNKNOWN,
            action=ActionType.ERROR,
            response=message,
            data={"error": "processing_failed"},
            detected_language=self._response_language(language),
            confidence=0.0,
            follow_up_suggestions=self._get_follow_up_suggestions(IntentType.UNKNOWN),
            timestamp=datetime.now().isoformat()
        )


voice_service = VoiceService()
