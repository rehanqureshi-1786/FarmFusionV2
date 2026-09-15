"""
Weather Agent powered by Open-Meteo with TTL caching, dynamic location awareness,
deterministic alert evaluation, and separate agronomic interpretations.
"""
from datetime import datetime, timezone
import structlog
import time
from typing import Any, Dict, List, Optional

import httpx
from app.schemas.weather import (
    CurrentWeather,
    DailyForecastItem,
    WeatherForecastResponse,
    WeatherCurrentResponse,
    AgriculturalAdvisory,
    WeatherAlertItem,
    SmartIrrigationAdvisor,
    SoilMoistureDepthItem
)
from app.services.weather_alert_engine import weather_alert_engine

import structlog
logger = structlog.get_logger(__name__)


class WeatherAgent:
    def __init__(self) -> None:
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.historical_url = "https://archive-api.open-meteo.com/v1/archive"
        # In-process TTL cache: key -> {"timestamp": float, "data": dict}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl_seconds = 900  # 15 minutes cache freshness

    def is_available(self) -> bool:
        return True

    def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(key)
        if entry and (time.time() - entry["timestamp"] < self.cache_ttl_seconds):
            return entry["data"]
        return None

    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    async def _resolve_location_name(self, lat: float, lon: float, explicit_name: Optional[str] = None) -> tuple[str, str]:
        """Resolves location name with fallback hierarchy: Explicit -> Reverse Geocode -> Coordinates String."""
        if explicit_name and explicit_name.strip() and explicit_name.lower() not in ("unknown", "string", "none"):
            return explicit_name.strip(), "user_or_farm"

        # Safe coordinate string representation
        coord_name = f"{round(lat, 2)}°N, {round(lon, 2)}°E"
        return coord_name, "coordinates_only"

    async def get_current_weather(
        self,
        lat: float,
        lon: float,
        location_name: Optional[str] = None,
        location_source: str = "coordinates_only",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetches and parses current physical weather observations with structured typing."""
        from app.core.language import resolve_language_code, get_current_language
        lang_code = resolve_language_code(language or get_current_language()).canonical_code
        loc_name, loc_src = await self._resolve_location_name(lat, lon, location_name)
        if location_source != "coordinates_only":
            loc_src = location_source

        try:
            payload = await self._fetch_weather_bundle(lat, lon, forecast_days=1, past_days=0)
            current = payload.get("current", {})
            daily = payload.get("daily", {})

            sunrise = daily.get("sunrise", [None])[0]
            sunset = daily.get("sunset", [None])[0]
            temperature = float(current.get("temperature_2m", 0.0))
            humidity = int(current.get("relative_humidity_2m", 0))
            wind_kmh = float(current.get("wind_speed_10m", 0.0))
            wind_ms = self._kmh_to_ms(wind_kmh)
            weather_code = int(current.get("weather_code", 0))
            condition_text = self._weather_code_to_text(weather_code, language=lang_code)

            smart_irrig = self._calculate_smart_irrigation(
                payload.get("hourly", {}),
                daily,
                language=lang_code
            )

            current_schema = CurrentWeather(
                latitude=lat,
                longitude=lon,
                location_name=loc_name,
                location_source=loc_src,
                timestamp=current.get("time", datetime.now(timezone.utc).isoformat()),
                temperature_c=temperature,
                feels_like_c=float(current.get("apparent_temperature", temperature)),
                humidity_percent=humidity,
                pressure_hpa=int(current.get("pressure_msl", 1013)),
                wind_speed_kmh=wind_kmh,
                wind_speed_ms=wind_ms,
                weather_code=weather_code,
                condition=condition_text,
                cloudiness_percent=int(current.get("cloud_cover", 0)),
                visibility_m=int(current.get("visibility", 10000)),
                sunrise=sunrise,
                sunset=sunset,
                source="Open-Meteo",
                language=lang_code,
                smart_irrigation=smart_irrig
            )

            advice = self._generate_farming_advice(
                temperature_c=temperature,
                humidity_percent=float(humidity),
                wind_speed_kmh=wind_kmh,
                weather_code=weather_code,
                language=lang_code
            )

            # Return dict for backward compatibility, with full schema fields
            res = current_schema.model_dump()
            res["success"] = True
            res["location"] = loc_name
            res["weather"] = condition_text
            res["farming_advice"] = advice
            res["language"] = lang_code
            res["smart_irrigation"] = smart_irrig.model_dump() if smart_irrig else None
            return res

        except Exception as exc:
            logger.error("open_meteo_current_failed", lat=lat, lon=lon, error=str(exc))
            return {
                "success": False,
                "error": f"Open-Meteo weather request failed: {str(exc)}",
                "source": "Open-Meteo",
                "latitude": lat,
                "longitude": lon,
                "location": loc_name
            }

    async def get_forecast(
        self,
        lat: float,
        lon: float,
        days: int = 7,
        location_name: Optional[str] = None,
        location_source: str = "coordinates_only",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetches real physical forecast (1-7 days) from Open-Meteo NWP."""
        from app.core.language import resolve_language_code, get_current_language
        lang_code = resolve_language_code(language or get_current_language()).canonical_code
        loc_name, loc_src = await self._resolve_location_name(lat, lon, location_name)
        if location_source != "coordinates_only":
            loc_src = location_source

        days = max(1, min(days, 7))

        try:
            payload = await self._fetch_weather_bundle(lat, lon, forecast_days=days, past_days=0)
            daily = payload.get("daily", {})
            forecast_items = self._build_daily_schema_rows(daily, days, language=lang_code)

            smart_irrig = self._calculate_smart_irrigation(
                payload.get("hourly", {}),
                daily,
                language=lang_code
            )

            advice = self._generate_forecast_advice(
                [item.model_dump() for item in forecast_items],
                language=lang_code
            )

            return {
                "success": True,
                "latitude": lat,
                "longitude": lon,
                "location": loc_name,
                "location_name": loc_name,
                "location_source": loc_src,
                "forecast_days": days,
                "forecast": [item.model_dump() for item in forecast_items],
                "farming_advice": advice,
                "language": lang_code,
                "smart_irrigation": smart_irrig.model_dump() if smart_irrig else None,
                "source": "Open-Meteo",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as exc:
            logger.error("open_meteo_forecast_failed", lat=lat, lon=lon, error=str(exc))
            return {
                "success": False,
                "error": f"Open-Meteo forecast request failed: {str(exc)}",
                "source": "Open-Meteo",
                "latitude": lat,
                "longitude": lon,
                "location": loc_name
            }

    async def get_weather_alerts(
        self,
        lat: float,
        lon: float,
        days: int = 7,
        location_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[WeatherAlertItem]:
        """Evaluates upcoming forecast against deterministic agricultural alert thresholds."""
        forecast_res = await self.get_forecast(lat, lon, days=days, location_name=location_name, language=language)
        if not forecast_res.get("success"):
            return []

        raw_items = forecast_res.get("forecast", [])
        daily_items = [DailyForecastItem(**item) for item in raw_items]
        loc = forecast_res.get("location_name") or location_name
        return weather_alert_engine.evaluate_forecast(
            lat=lat,
            lon=lon,
            forecasts=daily_items,
            location_name=loc,
            language=language or "hi"
        )

    async def get_agricultural_advisory(
        self,
        lat: float,
        lon: float,
        crop_name: Optional[str] = None,
        growth_stage: Optional[str] = None,
        soil_type: Optional[str] = None,
        language: str = "hi"
    ) -> AgriculturalAdvisory:
        """Constructs an explicit agricultural interpretation grounded in real forecast values."""
        forecast_res = await self.get_forecast(lat, lon, days=3, language=language)
        forecast_items = forecast_res.get("forecast", [])

        total_rain_next_3_days = sum(float(d.get("precipitation_mm", 0)) for d in forecast_items)
        max_rain_chance = max((int(d.get("precipitation_probability_percent", 0)) for d in forecast_items), default=0)
        max_temp = max((float(d.get("temperature_max_c", 0)) for d in forecast_items), default=30.0)
        min_temp = min((float(d.get("temperature_min_c", 0)) for d in forecast_items), default=20.0)
        max_wind = max((float(d.get("wind_speed_max_kmh", 0)) for d in forecast_items), default=10.0)

        from app.core.language import resolve_language_code
        lang = resolve_language_code(language).canonical_code
        if lang == "od":
            lang = "or"

        assumptions = []
        if crop_name:
            crop_prefix = {
                "gu": "પાક", "mr": "पीक", "pa": "ਫਸਲ", "bn": "ফসল", "ta": "பயிர்",
                "te": "పంట", "kn": "ಬೆಳೆ", "ml": "വിള", "or": "ଫସଲ", "as": "শস্য",
                "ur": "فصل", "mai": "फसल", "en": "Crop", "hi": "फसल"
            }.get(lang, "फसल")
            assumptions.append(f"{crop_prefix}: {crop_name}")
        if growth_stage:
            stage_prefix = {
                "gu": "વિકાસ તબક્કો", "mr": "वाढीची अवस्था", "pa": "ਵਾਧੇ ਦਾ ਪੜਾਅ", "bn": "বৃদ্ধির পর্যায়", "ta": "வளர்ச்சி நிலை",
                "te": "పెరుగుదల దశ", "kn": "ಬೆಳವಣಿಗೆಯ ಹಂತ", "ml": "വളർച്ചാ ഘട്ടം", "or": "ବୃଦ୍ଧି ଅବସ୍ଥା", "as": "বৃদ্ধিৰ স্তৰ",
                "ur": "نشوونما کا مرحلہ", "mai": "विकास चरण", "en": "Growth Stage", "hi": "वृद्धि अवस्था"
            }.get(lang, "वृद्धि अवस्था")
            assumptions.append(f"{stage_prefix}: {growth_stage}")
        if soil_type:
            soil_prefix = {
                "gu": "જમીન પ્રકાર", "mr": "मातीचा प्रकार", "pa": "ਮਿੱਟੀ ਦੀ ਕਿਸਮ", "bn": "মাটির ধরন", "ta": "மண் வகை",
                "te": "నేల రకం", "kn": "ಮಣ್ಣಿನ ವಿಧ", "ml": "മണ്ണ് തരം", "or": "ମାଟି ପ୍ରକାର", "as": "মাটিৰ প্ৰকাৰ",
                "ur": "مٹی کی قسم", "mai": "माटी प्रकार", "en": "Soil Type", "hi": "मिट्टी का प्रकार"
            }.get(lang, "मिट्टी का प्रकार")
            assumptions.append(f"{soil_prefix}: {soil_type}")
        if not assumptions:
            default_assumption = {
                "gu": "સામાન્ય ભારતીય કૃષિ ધોરણ; વિશિષ્ટ પાક/જમીન આપવામાં આવેલ નથી",
                "mr": "सामान्य भारतीय कृषी मानके; विशिष्ट पीक/माती दिलेली नाही",
                "pa": "ਆਮ ਭਾਰਤੀ ਖੇਤੀਬਾੜੀ ਮਿਆਰ; ਖਾਸ ਫਸਲ/ਮਿੱਟੀ ਨਹੀਂ ਦਿੱਤੀ ਗਈ",
                "bn": "সাধারণ ভারতীয় কৃষি মানদণ্ড; নির্দিষ্ট ফসল/মাটি প্রদান করা হয়নি",
                "ta": "பொதுவான இந்திய வேளாண் தரம்; குறிப்பிட்ட பயிர்/மண் குறிப்பிடப்படவில்லை",
                "te": "సాధారణ భారతీయ వ్యవసాయ ప్రమాణం; నిర్దిష్ట పంట/నేల ఇవ్వబడలేదు",
                "kn": "ಸಾಮಾನ್ಯ ಭಾರತೀಯ ಕೃಷಿ ಮಾನದಂಡ; ನಿರ್ದಿಷ್ಟ ಬೆಳೆ/ಮಣ್ಣು ಒದಗಿಸಲಾಗಿಲ್ಲ",
                "ml": "പൊതുവായ ഇന്ത്യൻ കാർഷിക മാനദണ്ഡം; പ്രത്യേക വിള/മണ്ണ് നൽകിയിട്ടില്ല",
                "or": "ସାଧାରଣ ଭାରତୀୟ କୃଷି ମାନକ; ନିର୍ଦ୍ଦିଷ୍ଟ ଫସଲ/ମାଟି ପ୍ରଦାନ କରାଯାଇ ନାହିଁ",
                "as": "সাধাৰণ ভাৰতীয় কৃষি মানদণ্ড; নিৰ্দিষ্ট শস্য/মাটি উল্লেখ কৰা নাই",
                "ur": "عام ہندوستانی زرعی معیارات؛ مخصوص فصل/مٹی فراہم نہیں کی گئی",
                "mai": "सामान्य भारतीय कृषि मानक; कोनो विशिष्ट फसल/माटी निर्दिष्ट नहि",
                "en": "General Indian agronomic standard; specific crop/soil not provided",
                "hi": "सामान्य भारतीय कृषि मानक; विशिष्ट फसल/मिट्टी निर्दिष्ट नहीं"
            }.get(lang, "सामान्य भारतीय कृषि मानक; विशिष्ट फसल/मिट्टी निर्दिष्ट नहीं")
            assumptions.append(default_assumption)

        # Deterministic advisory rules for all 14 languages
        if lang == "gu":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"આગામી 3 દિવસમાં {round(total_rain_next_3_days, 1)} મીમી વરસાદની શક્યતા છે. પિયત આપવાનું મુલતવી રાખો."
            elif max_temp >= 38.0:
                irrig = "ગરમી વધુ હોવાથી બાષ્પીભવન વધશે. સાંજના સમયે હળવું પિયત આપો."
            else:
                irrig = "જમીનમાં ભેજ ચકાસીને સામાન્ય પિયત આપી શકાય છે."

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "પવન અથવા વરસાદના જોખમને કારણે દવાનો છંટકાવ મોકૂફ રાખો."
            else:
                spray = "હવામાન અનુકૂળ છે. સવાર અથવા સાંજે દવાનો છંટકાવ કરી શકાય છે."

            field = "સામાન્ય ખેતી કાર્યો માટે હવામાન અનુકૂળ છે."
            summary = f"તાપમાન {round(min_temp, 1)}°C થી {round(max_temp, 1)}°C રહેશે. સંભવિત વરસાદ: {round(total_rain_next_3_days, 1)} મીમી."

        elif lang == "mr":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"पुढील 3 दिवसांत {round(total_rain_next_3_days, 1)} मिमी पावसाचा अंदाज आहे. पिकांना पाणी देणे टाळा."
            elif max_temp >= 38.0:
                irrig = "उन्हाची तीव्रता जास्त असल्याने बाष्पीभवन वाढेल. संध्याकाळी हलके पाणी द्या."
            else:
                irrig = "मातीतील ओलावा तपासून आवश्यकतेनुसार नियमित पाणी द्या."

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "वारा किंवा पावसाच्या शक्यतेमुळे कीटकनाशक फवारणी पुढे ढकला."
            else:
                spray = "फवारणीसाठी हवामान अनुकूल आहे. सकाळच्या किंवा संध्याकाळच्या वेळी फवारणी करा."

            field = "आंतरमशागत, खुरपणी आणि काढणीसाठी हवामान योग्य आहे."
            summary = f"तापमान {round(min_temp, 1)}°C ते {round(max_temp, 1)}°C राहील. 3 दिवसांतील पाऊस: {round(total_rain_next_3_days, 1)} मिमी."

        elif lang == "pa":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"ਅਗਲੇ 3 ਦਿਨਾਂ 'ਚ {round(total_rain_next_3_days, 1)} ਮਿਮੀ ਬਾਰਿਸ਼ ਦੀ ਸੰਭਾਵਨਾ ਹੈ। ਸਿੰਚਾਈ ਰੋਕੋ।"
            elif max_temp >= 38.0:
                irrig = "ਗਰਮੀ ਕਾਰਨ ਸ਼ਾਮ ਨੂੰ ਹਲਕਾ ਪਾਣੀ ਲਗਾਓ।"
            else:
                irrig = "ਮੌਸਮ ਆਮ ਹੈ। ਨਮੀ ਅਨੁਸਾਰ ਆਮ ਸਿੰਚਾਈ ਕਰੋ।"

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "ਤੇਜ਼ ਹਵਾ ਜਾਂ ਮੀਂਹ ਕਾਰਨ ਸਪਰੇਅ ਟਾਲ ਦਿਓ।"
            else:
                spray = "ਸਵੇਰ ਜਾਂ ਸ਼ਾਮ ਵੇਲੇ ਸਪਰੇਅ ਕਰਨ ਲਈ ਮੌਸਮ ਅਨੁਕੂਲ ਹੈ।"

            field = "ਖੇਤ ਦੇ ਕੰਮਾਂ ਅਤੇ ਕਟਾਈ ਲਈ ਮੌਸਮ ਅਨੁਕੂਲ ਹੈ।"
            summary = f"ਤਾਪਮਾਨ {round(min_temp, 1)}°C ਤੋਂ {round(max_temp, 1)}°C ਰਹੇਗਾ। ਕੁੱਲ ਮੀਂਹ: {round(total_rain_next_3_days, 1)} ਮਿਮੀ।"

        elif lang == "bn":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"আগামী ৩ দিনে {round(total_rain_next_3_days, 1)} মিমি বৃষ্টির সম্ভাবনা। সেচ স্থগিত রাখুন।"
            elif max_temp >= 38.0:
                irrig = "অতিরিক্ত গরমে আর্দ্রতা বজায় রাখতে বিকেলে হালকা সেচ দিন।"
            else:
                irrig = "মাটিতে আর্দ্রতা পরীক্ষা করে নিয়মিত সেচ দিন।"

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "ঝড়ো বাতাস বা বৃষ্টির আশঙ্কায় স্প্রে স্থগিত রাখুন।"
            else:
                spray = "সকাল বা বিকেলে কীটনাশক স্প্রে করার উপযোগী আবহাওয়া।"

            field = "ফসল তোলা ও নিড়ানির কাজের জন্য আবহাওয়া অনুকূল।"
            summary = f"তাপমাত্রা {round(min_temp, 1)}°C থেকে {round(max_temp, 1)}°C থাকবে। মোট বৃষ্টি: {round(total_rain_next_3_days, 1)} মিমি।"

        elif lang == "ta":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"அடுத்த 3 நாட்களில் {round(total_rain_next_3_days, 1)} மிமீ மழை பெய்ய வாய்ப்புள்ளது. நீர்ப்பாசனத்தை நிறுத்துங்கள்."
            elif max_temp >= 38.0:
                irrig = "அதிக வெப்பம் உள்ளதால் மாலையில் லேசான நீர்ப்பாசனம் செய்யுங்கள்."
            else:
                irrig = "மண்ணின் ஈரப்பதத்தைப் பொறுத்து வழக்கமான பாசனம் செய்யலாம்."

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "காற்று அல்லது மழையால் மருந்து தெளிப்பதை ஒத்திவைக்கவும்."
            else:
                spray = "காலை அல்லது மாலை வேளையில் மருந்து தெளிக்க ஏற்ற வானிலை."

            field = "அறுவடை மற்றும் களப்பணிகளுக்கு வானிலை உகந்தது."
            summary = f"வெப்பநிலை {round(min_temp, 1)}°C முதல் {round(max_temp, 1)}°C வரை இருக்கும். மழை: {round(total_rain_next_3_days, 1)} மிமீ."

        elif lang == "te":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"రాబోయే 3 రోజుల్లో {round(total_rain_next_3_days, 1)} మి.మీ వర్షం పడే అవకాశం ఉంది. నీటిపారుదల ఆపండి."
            elif max_temp >= 38.0:
                irrig = "ఎండ తీవ్రత వల్ల సాయంత్రం వేళల్లో తేలికపాటి తడులు ఇవ్వండి."
            else:
                irrig = "నేల తేమను బట్టి సాధారణ నీటిపారుదల చేయండి."

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "గాలి లేదా వర్షం వల్ల పిచికారీ వాయిదా వేయండి."
            else:
                spray = "ఉదయం లేదా సాయంత్రం పిచికారీ చేయడానికి అనుకూలం."

            field = "పొలం పనులు మరియు కోతలకు వాతావరణం అనుకూలంగా ఉంది."
            summary = f"ఉష్ణోగ్రత {round(min_temp, 1)}°C నుండి {round(max_temp, 1)}°C వరకు ఉంటుంది. వర్షపాతం: {round(total_rain_next_3_days, 1)} మి.మీ."

        elif lang == "kn":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"ಮುಂದಿನ 3 ದಿನಗಳಲ್ಲಿ {round(total_rain_next_3_days, 1)} ಮಿಮೀ ಮಳೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ. ನೀರಾವರಿ ನಿಲ್ಲಿಸಿ."
            elif max_temp >= 38.0:
                irrig = "ಹೆಚ್ಚಿನ ಶಾಖದಿಂದಾಗಿ ಸಂಜೆ ಲಘು ನೀರಾವರಿ ಮಾಡಿ."
            else:
                irrig = "ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಪರೀಕ್ಷಿಸಿ ನಿಯಮಿತವಾಗಿ ನೀರು ಹಾಯಿಸಿ."

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "ಗಾಳಿ ಅಥವಾ ಮಳೆಯ ಕಾರಣ ಸಿಂಪಡಣೆಯನ್ನು ಮುಂದೂಡಿ."
            else:
                spray = "ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ಔಷಧ ಸಿಂಪಡಿಸಲು ಸೂಕ್ತ ಸಮಯ."

            field = "ಕಟಾವು ಮತ್ತು ಕೃಷಿ ಕೆಲಸಗಳಿಗೆ ಹವಾಮಾನ ಅನುಕೂಲಕರವಾಗಿದೆ."
            summary = f"ತಾಪಮಾನ {round(min_temp, 1)}°C ರಿಂದ {round(max_temp, 1)}°C ಇರುತ್ತದೆ. ಮಳೆ: {round(total_rain_next_3_days, 1)} ಮಿಮೀ."

        elif lang == "ml":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"അടുത്ത 3 ദിവസങ്ങളിൽ {round(total_rain_next_3_days, 1)} മിമി മഴയ്ക്ക് സാധ്യത. നനയ്ക്കുന്നത് ഒഴിവാക്കുക."
            elif max_temp >= 38.0:
                irrig = "ചൂട് കൂടുതലായതിനാൽ വൈകുന്നേരങ്ങളിൽ നനയ്ക്കുക."
            else:
                irrig = "മണ്ണിലെ ഈർപ്പത്തിനനുസരിച്ച് നനയ്ക്കാം."

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "മഴയോ കാറ്റോ ഉള്ളപ്പോൾ മരുന്ന് തളിക്കുന്നത് മാറ്റിവയ്ക്കുക."
            else:
                spray = "രാവിലെയോ വൈകുന്നേരമോ മരുന്ന് തളിക്കാൻ അനുകൂല സമയം."

            field = "വിളവെടുപ്പിനും കൃഷിപ്പണികൾക്കും അനുകൂല കാലാവസ്ഥ."
            summary = f"താപനില {round(min_temp, 1)}°C മുതൽ {round(max_temp, 1)}°C വരെ. മഴ: {round(total_rain_next_3_days, 1)} മിമി."

        elif lang == "or":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"ଆଗାମୀ ୩ ଦିନରେ {round(total_rain_next_3_days, 1)} ମିମି ବର୍ଷା ସମ୍ଭାବନା। ଜଳସେଚନ ବନ୍ଦ ରଖନ୍ତୁ।"
            elif max_temp >= 38.0:
                irrig = "ଅଧିକ ଖରା ଥିବାରୁ ସନ୍ଧ୍ୟାରେ ହାଲୁକା ପାଣି ଦିଅନ୍ତୁ।"
            else:
                irrig = "ମାଟିର ଓଦା ଅନୁଯାୟୀ ନିୟମିତ ଜଳସେଚନ କରନ୍ତୁ।"

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "ପବନ କିମ୍ବା ବର୍ଷା ଯୋଗୁଁ ସ୍ପ୍ରେ ସ୍ଥଗିତ ରଖନ୍ତୁ।"
            else:
                spray = "ସକାଳ କିମ୍ବା ସନ୍ଧ୍ୟାରେ ଔଷଧ ସ୍ପ୍ରେ କରିବା ଉପଯୁକ୍ତ।"

            field = "ଅମଳ ଏବଂ କୃଷି କାର୍ଯ୍ୟ ପାଇଁ ପାଣିପାଗ ଅନୁକୂଳ।"
            summary = f"ତାପମାତ୍ରା {round(min_temp, 1)}°C ରୁ {round(max_temp, 1)}°C ରହିବ। ବର୍ଷା: {round(total_rain_next_3_days, 1)} ମିମି।"

        elif lang == "as":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"অহা ৩ দিনত {round(total_rain_next_3_days, 1)} মিমি বৰষুণৰ সম্ভাৱনা। পানী দিয়া স্থগিত ৰাখক।"
            elif max_temp >= 38.0:
                irrig = "অধিক গৰমৰ বাবে গধূলি সময়ত লঘু পানী দিয়ক।"
            else:
                irrig = "মাটিৰ আৰ্দ্ৰতা চাই নিয়মীয়া জলসিঞ্চন কৰক।"

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "বতাহ বা বৰষুণৰ বাবে স্প্ৰে' কৰা পিছুৱাই দিয়ক।"
            else:
                spray = "ৰাতিপুৱা বা গধূলি ঔষধ স্প্ৰে' কৰাৰ বাবে বতৰ অনুকূল।"

            field = "শস্য চপোৱা আৰু পথাৰৰ কামৰ বাবে বতৰ উপযোগী।"
            summary = f"উষ্ণতা {round(min_temp, 1)}°C ৰ পৰা {round(max_temp, 1)}°C থাকিব। মুঠ বৰষুণ: {round(total_rain_next_3_days, 1)} মিমি।"

        elif lang == "ur":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"اگلے 3 دنوں میں {round(total_rain_next_3_days, 1)} ملی میٹر بارش کا امکان ہے۔ آبپاشی روک دیں۔"
            elif max_temp >= 38.0:
                irrig = "شدید گرمی کی وجہ سے شام کے وقت ہلکی آبپاشی کریں۔"
            else:
                irrig = "مٹی کی نمی دیکھ کر معمول کے مطابق آبپاشی کریں۔"

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "تیز ہوا یا بارش کے امکان پر اسپرے موخر کریں۔"
            else:
                spray = "صبح یا شام کے وقت اسپرے کے لیے موسم سازگار ہے۔"

            field = "فصل کی کٹائی اور کھیت کے کاموں کے لیے موسم بہترین ہے۔"
            summary = f"درجہ حرارت {round(min_temp, 1)}°C سے {round(max_temp, 1)}°C رہے گا۔ کل بارش: {round(total_rain_next_3_days, 1)} ملی میٹر۔"

        elif lang == "mai":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"आबय बला 3 दिन मे {round(total_rain_next_3_days, 1)} मिमी वर्षा केर सम्भावना अछि। पटौनी रोकि दिअ।"
            elif max_temp >= 38.0:
                irrig = "कड़ा घाम केर कारणे संझुका हल्का पटौनी करू।"
            else:
                irrig = "माटी मे नमी देखि क नियमित पटौनी करू।"

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "तेज हवा वा वर्षा केर सम्भावना पर छिड़काव रोकि दिअ।"
            else:
                spray = "भिनसरिया वा संझुका कीटनाशक छिड़काव लेल मौसम नीक अछि।"

            field = "दवनी, कटनी आ खेत केर काज लेल मौसम अनुकूल अछि।"
            summary = f"तापमान {round(min_temp, 1)}°C सं {round(max_temp, 1)}°C रहत। कुल वर्षा: {round(total_rain_next_3_days, 1)} मिमी।"

        elif lang == "en":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"Rainfall of {round(total_rain_next_3_days, 1)} mm is forecast over the next 3 days. Pause irrigation to prevent waterlogging."
            elif max_temp >= 38.0:
                irrig = "High temperatures increase evapotranspiration. Provide light evening irrigation to maintain root-zone moisture."
            else:
                irrig = "Weather conditions are stable. Proceed with regular scheduled irrigation based on soil moisture."

            if max_wind >= 25.0:
                spray = f"Wind speed of {round(max_wind, 1)} km/h presents spray drift hazard. Postpone foliar applications."
            elif max_rain_chance >= 60:
                spray = "High rain probability may wash away applied agrochemicals. Delay chemical spraying."
            else:
                spray = "Wind and moisture conditions are favorable for spraying during morning or late afternoon."

            field = "Field conditions are suitable for harvest, intercultural operations, and tilling."
            summary = f"Temperature range: {round(min_temp, 1)}°C to {round(max_temp, 1)}°C. 3-day precipitation: {round(total_rain_next_3_days, 1)} mm."

        else:
            # Default Hindi
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"अगले 3 दिनों में {round(total_rain_next_3_days, 1)} मिमी बारिश का अनुमान है। सिंचाई रोक दें ताकि जलभराव न हो।"
            elif max_temp >= 38.0:
                irrig = "तेज गर्मी के कारण वाष्पीकरण अधिक होगा। फसलों में नमी बनाए रखने के लिए शाम को हल्की सिंचाई करें।"
            else:
                irrig = "मौसम सामान्य रहेगा। मिट्टी की नमी की जांच कर आवश्यकतानुसार नियमित सिंचाई करें।"

            if max_wind >= 25.0:
                spray = f"हवा की गति {round(max_wind, 1)} किमी/घंटा है। दवा के बहाव (ड्रिफ्ट) के खतरे से छिड़काव अभी न करें।"
            elif max_rain_chance >= 60:
                spray = "बारिश की संभावना के कारण कीटनाशक धुल सकते हैं। शुष्क मौसम की प्रतीक्षा करें।"
            else:
                spray = "हवा एवं मौसम अनुकूल है। सुबह या शाम के समय छिड़काव सुरक्षित रूप से किया जा सकता है।"

            if total_rain_next_3_days >= 30.0:
                field = "खेत में नमी अधिक रहेगी। जुताई और कटी फसल की गहाई (थ्रेशिंग) कुछ दिन टालें।"
            else:
                field = "खेत कार्य, निराई-गुड़ाई एवं कटाई के लिए मौसम अनुकूल है।"

            summary = f"तापमान {round(min_temp, 1)}°C से {round(max_temp, 1)}°C रहेगा। 3 दिनों में कुल वर्षा: {round(total_rain_next_3_days, 1)} मिमी।"

        return AgriculturalAdvisory(
            irrigation_advice=irrig,
            spraying_advice=spray,
            fieldwork_advice=field,
            summary=summary,
            language=lang,
            assumptions=assumptions
        )

    def _calculate_smart_irrigation(
        self,
        hourly: Dict[str, Any],
        daily: Dict[str, Any],
        language: str = "hi"
    ) -> Optional[SmartIrrigationAdvisor]:
        """
        Computes deterministic, agronomic smart irrigation advisory based on Open-Meteo
        volumetric soil moisture across root depths (0-1cm, 3-9cm, 9-27cm) and upcoming precipitation.
        """
        try:
            m_0_1_list = hourly.get("soil_moisture_0_to_1cm", [])
            m_3_9_list = hourly.get("soil_moisture_3_to_9cm", [])
            m_9_27_list = hourly.get("soil_moisture_9_to_27cm", [])
            s_temp_list = hourly.get("soil_temperature_0cm", [])

            if not m_3_9_list:
                return None

            # Determine index for current hour
            idx = 0
            times = hourly.get("time", [])
            now_hour_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
            if now_hour_iso in times:
                idx = times.index(now_hour_iso)

            # Volumetric moisture is m3/m3 (e.g. 0.24 = 24%)
            m_0_1 = float(m_0_1_list[idx] if idx < len(m_0_1_list) and m_0_1_list[idx] is not None else 0.22)
            m_3_9 = float(m_3_9_list[idx] if idx < len(m_3_9_list) and m_3_9_list[idx] is not None else 0.25)
            m_9_27 = float(m_9_27_list[idx] if idx < len(m_9_27_list) and m_9_27_list[idx] is not None else 0.28)
            s_temp = float(s_temp_list[idx] if idx < len(s_temp_list) and s_temp_list[idx] is not None else 25.0)

            pct_0_1 = round(m_0_1 * 100.0, 1)
            pct_3_9 = round(m_3_9 * 100.0, 1)
            pct_9_27 = round(m_9_27 * 100.0, 1)

            # Check next 24 hours rainfall forecast
            precip_forecast = daily.get("precipitation_sum", [0.0])
            next_24h_rain = float(precip_forecast[0] or 0.0) if len(precip_forecast) > 0 else 0.0

            # Deterministic thresholds based on 3-9cm active root zone
            if pct_3_9 < 18.0:
                if next_24h_rain >= 8.0:
                    status = "DEFICIT"
                    status_badge = "NEEDS_WATER"
                    irrigation_score = 45
                    hours = 0.0
                    window = "Wait for Rain" if language == "en" else "बारिश की प्रतीक्षा करें"
                    advice_hi = f"जड़ क्षेत्र में नमी कम है ({pct_3_9}%), लेकिन आज {next_24h_rain:.1f} मिमी बारिश की संभावना है। पानी और बिजली बचाने के लिए सिंचाई अभी रोकें।"
                    advice = (
                        f"Root-zone soil moisture is low ({pct_3_9}%), but {next_24h_rain:.1f} mm rain is forecasted today. Hold irrigation to conserve water and fuel."
                        if language == "en" else advice_hi
                    )
                    title = "Moisture Low (Rain Expected)" if language == "en" else "नमी कम (बारिश संभावित)"
                else:
                    status = "DEFICIT"
                    status_badge = "NEEDS_WATER"
                    irrigation_score = min(95, int(80 + (18.0 - pct_3_9) * 2))
                    hours = 2.5
                    window = "This Evening" if language == "en" else "आज शाम (ड्रिप/नलकूप)"
                    advice_hi = f"जड़ क्षेत्र में मिट्टी की नमी कम है ({pct_3_9}%)। फसलों में पानी की कमी का तनाव हो सकता है। आज शाम 2-3 घंटे हल्की सिंचाई करें।"
                    advice = (
                        f"Active root-zone soil moisture is critically low ({pct_3_9}%). Crops are under moisture stress. Apply light irrigation (2-3 hours) this evening."
                        if language == "en" else advice_hi
                    )
                    title = "Irrigation Recommended" if language == "en" else "सिंचाई की आवश्यकता"
            elif pct_3_9 > 34.0:
                status = "SATURATED"
                status_badge = "WATERLOGGED_RISK"
                irrigation_score = 10
                hours = 0.0
                window = "After 4-5 Days" if language == "en" else "4-5 दिन बाद"
                advice_hi = f"खेत में अत्यधिक नमी ({pct_3_9}%) है। बिल्कुल सिंचाई न करें। जल निकासी खुली रखें ताकि जलभराव से जड़ें न सड़ें।"
                advice = (
                    f"Soil is saturated ({pct_3_9}%). Do NOT irrigate. Keep field drainage open to avoid waterlogging and root asphyxiation."
                    if language == "en" else advice_hi
                )
                title = "Soil Saturated" if language == "en" else "अत्यधिक नमी (जलभराव जोखिम)"
            else:
                status = "OPTIMAL"
                status_badge = "OPTIMAL"
                irrigation_score = 25
                hours = 0.0
                window = "After 2-3 Days" if language == "en" else "2-3 दिन बाद"
                advice_hi = f"जड़ क्षेत्र में पर्याप्त नमी ({pct_3_9}%) उपलब्ध है। फसल के लिए उत्तम स्थिति है। आज पानी देने की कोई आवश्यकता नहीं है।"
                advice = (
                    f"Active root zone has optimal moisture ({pct_3_9}%). Crop hydration is healthy and field capacity is balanced. No watering needed today."
                    if language == "en" else advice_hi
                )
                title = "Optimal Moisture" if language == "en" else "पर्याप्त नमी (उत्तम स्थिति)"

            tillage_suitable = (pct_3_9 <= 33.0 and pct_0_1 <= 32.0)
            if 20.0 <= pct_3_9 <= 30.0 and pct_0_1 < 30.0:
                tillage = "Ideal moisture condition for sowing & tillage (वपसा स्थिति)" if language == "en" else "जुताई और बुवाई के लिए आदर्श वपसा स्थिति"
            elif pct_3_9 > 33.0:
                tillage = "Soil is too wet for tractor tillage" if language == "en" else "खेत अधिक गीला है, अभी ट्रैक्टर जुताई न करें"
            else:
                tillage = "Dry soil - pre-irrigate before ploughing" if language == "en" else "मिट्टी सूखी है, जुताई से पहले पलेवा (हल्की सिंचाई) करें"

            depth_items = [
                SoilMoistureDepthItem(
                    depth_cm="0-1 cm (Surface)",
                    moisture_percentage=pct_0_1,
                    moisture_m3m3=m_0_1,
                    status="DRY" if pct_0_1 < 15.0 else ("SATURATED" if pct_0_1 > 35.0 else "OPTIMAL")
                ),
                SoilMoistureDepthItem(
                    depth_cm="3-9 cm (Root Zone)",
                    moisture_percentage=pct_3_9,
                    moisture_m3m3=m_3_9,
                    status="DEFICIT" if pct_3_9 < 18.0 else ("SATURATED" if pct_3_9 > 34.0 else "OPTIMAL")
                ),
                SoilMoistureDepthItem(
                    depth_cm="9-27 cm (Subsoil)",
                    moisture_percentage=pct_9_27,
                    moisture_m3m3=m_9_27,
                    status="DEFICIT" if pct_9_27 < 20.0 else ("SATURATED" if pct_9_27 > 36.0 else "OPTIMAL")
                )
            ]

            return SmartIrrigationAdvisor(
                root_zone_moisture_percent=pct_3_9,
                surface_moisture_percent=pct_0_1,
                deep_moisture_percent=pct_9_27,
                soil_temperature_c=s_temp,
                status=status,
                status_badge=status_badge,
                status_title=title,
                irrigation_need_score=irrigation_score,
                actionable_advice=advice,
                actionable_advice_hi=advice_hi,
                watering_hours_recommended=hours,
                next_irrigation_window=window,
                tillage_suitability=tillage,
                tillage_suitable=tillage_suitable,
                next_24h_rain_sum_mm=round(next_24h_rain, 1),
                depth_breakdown=depth_items
            )
        except Exception as exc:
            logger.warning("smart_irrigation_calculation_failed", error=str(exc))
            return None

    async def _fetch_weather_bundle(
        self,
        lat: float,
        lon: float,
        forecast_days: int,
        past_days: int
    ) -> Dict[str, Any]:
        """Queries Open-Meteo API with TTL cache check."""
        cache_key = f"open_meteo:{round(lat, 3)}:{round(lon, 3)}:f{forecast_days}:p{past_days}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,pressure_msl,wind_speed_10m,weather_code,visibility,cloud_cover",
            "hourly": "soil_moisture_0_to_1cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,soil_temperature_0cm",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,sunrise,sunset",
            "forecast_days": forecast_days,
            "past_days": past_days,
            "timezone": "auto",
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0), trust_env=False) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            self._set_cache(cache_key, data)
            return data

    def _build_daily_schema_rows(self, daily: Dict[str, Any], days: int, language: str = "hi") -> List[DailyForecastItem]:
        items: List[DailyForecastItem] = []
        times = daily.get("time", [])
        limit = min(days, len(times))

        for i in range(limit):
            max_temp = float(daily.get("temperature_2m_max", [0.0])[i] or 0.0)
            min_temp = float(daily.get("temperature_2m_min", [0.0])[i] or 0.0)
            avg_temp = round((max_temp + min_temp) / 2.0, 1)
            precip = float(daily.get("precipitation_sum", [0.0])[i] or 0.0)
            rain_prob = int(daily.get("precipitation_probability_max", [0])[i] or 0)
            wind_kmh = float(daily.get("wind_speed_10m_max", [0.0])[i] or 0.0)
            code = int(daily.get("weather_code", [0])[i] or 0)
            cond = self._weather_code_to_text(code, language=language)

            sunrise = daily.get("sunrise", [None])[i] if i < len(daily.get("sunrise", [])) else None
            sunset = daily.get("sunset", [None])[i] if i < len(daily.get("sunset", [])) else None

            items.append(DailyForecastItem(
                date=times[i],
                temperature_max_c=max_temp,
                temperature_min_c=min_temp,
                temperature_avg_c=avg_temp,
                precipitation_mm=precip,
                precipitation_probability_percent=rain_prob,
                wind_speed_max_kmh=wind_kmh,
                wind_speed_max_ms=self._kmh_to_ms(wind_kmh),
                weather_code=code,
                condition=cond,
                sunrise=sunrise,
                sunset=sunset
            ))
        return items

    def _build_daily_rows(self, daily: Dict[str, Any], days: int, past: bool = False, language: str = "hi") -> List[Dict[str, Any]]:
        # Preserved for backward compatibility with existing tests
        rows = []
        for i in range(min(days, len(daily.get("time", [])))):
            max_temp = daily.get("temperature_2m_max", [None])[i]
            min_temp = daily.get("temperature_2m_min", [None])[i]
            avg_temp = None
            if max_temp is not None and min_temp is not None:
                avg_temp = round((max_temp + min_temp) / 2, 1)

            rows.append({
                "date": daily.get("time", [None])[i],
                "temperature_c": avg_temp,
                "humidity_percent": 0,
                "weather": self._weather_code_to_text(daily.get("weather_code", [0])[i], language=language),
                "wind_speed_ms": self._kmh_to_ms(daily.get("wind_speed_10m_max", [0])[i]),
                "rain_chance": float(daily.get("precipitation_probability_max", [0])[i] or 0),
                "precipitation_mm": float(daily.get("precipitation_sum", [0])[i] or 0),
                "temperature_max_c": max_temp,
                "temperature_min_c": min_temp,
            })
        return rows

    def _generate_farming_advice(
        self,
        temperature_c: float | None,
        humidity_percent: float | None,
        wind_speed_kmh: float | None,
        weather_code: int | None,
        language: str = "hi"
    ) -> str:
        advice_hi: List[str] = []
        advice_gu: List[str] = []
        advice_mr: List[str] = []
        advice_pa: List[str] = []
        advice_bn: List[str] = []
        advice_en: List[str] = []

        if temperature_c is not None and temperature_c > 35:
            advice_hi.append("उच्च तापमान - नमी बनाए रखने के लिए हल्की सिंचाई करें")
            advice_gu.append("ઊંચું તાપમાન - ભેજ જાળવવા હળવું પિયત આપો")
            advice_mr.append("उच्च तापमान - ओलावा टिकवण्यासाठी हलके पाणी द्या")
            advice_pa.append("ਉੱਚ ਤਾਪਮਾਨ - ਨਮੀ ਬਣਾਈ ਰੱਖਣ ਲਈ ਹਲਕੀ ਸਿੰਚਾਈ ਕਰੋ")
            advice_bn.append("উচ্চ তাপমাত্রা - আর্দ্রতা বজায় রাখতে হালকা সেচ দিন")
            advice_en.append("High temperature - irrigate lightly to preserve soil moisture")

        if humidity_percent is not None and humidity_percent > 85:
            advice_hi.append("अधिक नमी - कवक एवं फफूंद जनित रोगों की निगरानी करें")
            advice_gu.append("વધુ ભેજ - ફૂગજન્ય રોગોનું ધ્યાન રાખો")
            advice_mr.append("जास्त आर्द्रता - बुरशीजन्य रोगांचे निरीक्षण करा")
            advice_pa.append("ਵੱਧ ਨਮੀ - ਉੱਲੀ ਰੋਗਾਂ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ")
            advice_bn.append("অতিরিক্ত আর্দ্রতা - ছত্রাকজনিত রোগের লক্ষণ খেয়াল রাখুন")
            advice_en.append("High humidity - monitor crops for fungal disease symptoms")

        if wind_speed_kmh is not None and wind_speed_kmh > 25:
            advice_hi.append("तेज हवा - कीटनाशक का छिड़काव न करें")
            advice_gu.append("તેજ પવન - દવાનો છંટકાવ મોકૂફ રાખો")
            advice_mr.append("जोरदार वारा - कीटकनाशक फवारणी टाळा")
            advice_pa.append("ਤੇਜ਼ ਹਵਾ - ਸਪਰੇਅ ਕਰਨ ਤੋਂ ਬਚੋ")
            advice_bn.append("ঝড়ো বাতাস - কীটনাশক স্প্রে করা থেকে বিরত থাকুন")
            advice_en.append("High winds - avoid pesticide/fertilizer spraying")

        if weather_code is not None and weather_code in (61, 63, 65, 80, 81, 82, 95):
            advice_hi.append("बारिश/आंधी की संभावना - जल निकासी की व्यवस्था तैयार रखें")
            advice_gu.append("વરસાદની શક્યતા - પાણીના નિકાલની વ્યવસ્થા રાખો")
            advice_mr.append("पावसाची शक्यता - निचरा व्यवस्था तयार ठेवा")
            advice_pa.append("ਬਾਰਿਸ਼ ਦਾ ਖਦਸ਼ਾ - ਪਾਣੀ ਦੀ ਨਿਕਾਸੀ ਦਾ ਪ੍ਰਬੰਧ ਰੱਖੋ")
            advice_bn.append("বৃষ্টির সম্ভাবনা - নিষ্কাশন ব্যবস্থা প্রস্তুত রাখুন")
            advice_en.append("Rain/storm likely - ensure adequate drainage")

        if language == "gu":
            return " | ".join(advice_gu) if advice_gu else "હવામાન અનુકૂળ છે - ખેતીના કામ સામાન્ય રીતે કરો"
        elif language == "mr":
            return " | ".join(advice_mr) if advice_mr else "हवामान अनुकूल आहे - नियमित शेती कामे चालू ठेवा"
        elif language == "pa":
            return " | ".join(advice_pa) if advice_pa else "ਮੌਸਮ ਅਨੁਕੂਲ ਹੈ - ਖੇਤੀ ਕੰਮ ਆਮ ਵਾਂਗ ਕਰੋ"
        elif language == "bn":
            return " | ".join(advice_bn) if advice_bn else "আবহাওয়া অনুকূল - স্বাভাবিক চাষাবাদ চালিয়ে যান"
        elif language == "en":
            return " | ".join(advice_en) if advice_en else "Favorable weather conditions for farming operations"
        else:
            return " | ".join(advice_hi) if advice_hi else "मौसम अनुकूल है - सामान्य कृषि कार्य जारी रखें"

    def _generate_forecast_advice(self, forecasts: List[Dict[str, Any]], language: str = "hi") -> str:
        rainy_days = sum(1 for f in forecasts if (f.get("rain_chance", 0) > 40 or f.get("precipitation_probability_percent", 0) > 40))
        hot_days = sum(1 for f in forecasts if (f.get("temperature_c") or f.get("temperature_max_c") or 0) > 35)

        if language == "gu":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} દિવસ વરસાદની શક્યતા છે. સૂકા દિવસોમાં જ દવાનો છંટકાવ કરો.")
            if hot_days: parts.append(f"{hot_days} દિવસ તીવ્ર ગરમી રહેશે. પિયતની વ્યવસ્થા તૈયાર રાખો.")
            return " ".join(parts) if parts else "હવામાન સ્થિર રહેશે. ખેતી કામ માટે અનુકૂળ સમય."
        elif language == "mr":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} दिवस पावसाची शक्यता आहे. कोरड्या हवामानातच फवारणीचे नियोजन करा.")
            if hot_days: parts.append(f"{hot_days} दिवस कडक ऊन राहील. पाण्याची योग्य सोय ठेवा.")
            return " ".join(parts) if parts else "हवामान स्थिर राहील. शेतीच्या कामांसाठी उत्तम वेळ."
        elif language == "pa":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} ਦਿਨ ਬਾਰਿਸ਼ ਦੀ ਸੰਭਾਵਨਾ ਹੈ। ਸਪਰੇਅ ਖੁਸ਼ਕ ਮੌਸਮ ਵਿੱਚ ਹੀ ਕਰੋ।")
            if hot_days: parts.append(f"{hot_days} ਦਿਨ ਤੇਜ਼ ਗਰਮੀ ਰਹੇਗੀ। ਸਿੰਚਾਈ ਦਾ ਪ੍ਰਬੰਧ ਰੱਖੋ।")
            return " ".join(parts) if parts else "ਮੌਸਮ ਸਥਿਰ ਰਹੇਗਾ। ਆਮ ਖੇਤੀ ਕੰਮਾਂ ਲਈ ਵਧੀਆ ਸਮਾਂ।"
        elif language == "bn":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} দিন বৃষ্টির সম্ভাবনা রয়েছে। শুকনো দিনে স্প্রে করুন।")
            if hot_days: parts.append(f"{hot_days} দিন তীব্র গরম থাকবে। সেচের ব্যবস্থা প্রস্তুত রাখুন।")
            return " ".join(parts) if parts else "আবহাওয়া স্থিতিশীল থাকবে। মাঠের কাজের জন্য উপযুক্ত।"
        elif language == "en":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} rainy day(s) expected. Plan spraying around dry windows.")
            if hot_days: parts.append(f"{hot_days} hot day(s) ahead. Keep irrigation ready.")
            return " ".join(parts) if parts else "Stable weather expected. Good for field operations."
        else:
            parts = []
            if rainy_days: parts.append(f"{rainy_days} दिन बारिश की संभावना है। सूखे मौसम में ही छिड़काव की योजना बनाएं।")
            if hot_days: parts.append(f"{hot_days} दिन तेज गर्मी रहेगी। सिंचाई की व्यवस्था तैयार रखें।")
            return " ".join(parts) if parts else "मौसम स्थिर रहने की संभावना है। सामान्य खेती कार्यों के लिए अच्छा समय।"

    def _weather_code_to_text(self, code: int | None, language: str = "hi") -> str:
        code_val = code or 0
        if language == "od":
            language = "or"

        if language == "gu":
            gu_map = {
                0: "સ્વચ્છ આકાશ", 1: "સામાન્ય સ્વચ્છ", 2: "અંશતઃ વાદળછાયું", 3: "વાદળછાયું",
                45: "ધુમ્મસ", 51: "ઝરમર વરસાદ", 61: "હળવો વરસાદ", 63: "મધ્યમ વરસાદ",
                65: "ભારે વરસાદ", 80: "ઝાપટાં", 95: "ગાજવીજ સાથે વાવાઝોડું"
            }
            return gu_map.get(code_val, "હવામાન અપડેટ ઉપલબ્ધ")
        elif language == "mr":
            mr_map = {
                0: "निरभ्र आकाश", 1: "साधारण स्वच्छ", 2: "अंशतः ढगाळ", 3: "ढगाळ",
                45: "धुके", 51: "रिमझिम पाऊस", 61: "हलका पाऊस", 63: "मध्यम पाऊस",
                65: "मुसळधार पाऊस", 80: "पावसाच्या सरी", 95: "वादळी पाऊस"
            }
            return mr_map.get(code_val, "हवामान माहिती उपलब्ध")
        elif language == "pa":
            pa_map = {
                0: "ਸਾਫ ਅਸਮਾਨ", 1: "ਮੁੱਖ ਤੌਰ 'ਤੇ ਸਾਫ", 2: "ਅੰਸ਼ਕ ਬੱਦਲਵਾਈ", 3: "ਬੱਦਲਵਾਈ",
                45: "ਧੁੰਦ", 51: "ਫੁਹਾਰ", 61: "ਹਲਕੀ ਬਾਰਿਸ਼", 63: "ਦਰਮਿਆਨੀ ਬਾਰਿਸ਼",
                65: "ਭਾਰੀ ਬਾਰਿਸ਼", 80: "ਤੇਜ਼ ਬਾਰਿਸ਼ ਦੀਆਂ ਛੱਲਾਂ", 95: "ਗਰਜ ਨਾਲ ਤੂਫਾਨ"
            }
            return pa_map.get(code_val, "ਮੌਸਮ ਅਪਡੇਟ ਉਪਲਬਧ")
        elif language == "bn":
            bn_map = {
                0: "পরিষ্কার আকাশ", 1: "প্রধানত পরিষ্কার", 2: "আংশিক মেঘলা", 3: "মেঘলা আকাশ",
                45: "কুয়াশা", 51: "গুঁড়ি গুঁড়ি বৃষ্টি", 61: "হালকা বৃষ্টি", 63: "মাঝারি বৃষ্টি",
                65: "ভারী বৃষ্টি", 80: "বৃষ্টির ঝলক", 95: "বজ্রবিদ্যুৎসহ ঝড়"
            }
            return bn_map.get(code_val, "আবহাওয়া আপডেট উপলব্ধ")
        elif language == "ta":
            ta_map = {
                0: "தெளிவான வானம்", 1: "பெரும்பாலும் தெளிவானது", 2: "பகுதி மேகமூட்டம்", 3: "முழு மேகமூட்டம்",
                45: "மூடுபனி", 51: "தூறல்", 61: "லேசான மழை", 63: "மிதமான மழை",
                65: "கனமழை", 80: "மழை பொழிவு", 95: "இடி மின்னலுடன் மழை"
            }
            return ta_map.get(code_val, "வானிலை தகவல் உள்ளது")
        elif language == "te":
            te_map = {
                0: "స్పష్టమైన ఆకాశం", 1: "ఎక్కువగా స్పష్టం", 2: "పాక్షికంగా మేఘావృతం", 3: "పూర్తిగా మేఘావృతం",
                45: "పొగమంచు", 51: "తుంపర్లు", 61: "తేలికపాటి వర్షం", 63: "మితమైన వర్షం",
                65: "భారీ వర్షం", 80: "వర్షపు జల్లులు", 95: "ఉరుములతో కూడిన వర్షం"
            }
            return te_map.get(code_val, "వాతావరణ సమాచారం అందుబాటులో ఉంది")
        elif language == "kn":
            kn_map = {
                0: "ಸ್ವಚ್ಛ ಆಕಾಶ", 1: "ಹೆಚ್ಚಾಗಿ ಸ್ವಚ್ಛ", 2: "ಭಾಗಶಃ ಮೋಡ", 3: "ತುಂಬಾ ಮೋಡ",
                45: "ದಟ್ಟ ಮಂಜು", 51: "ತುಂತುರು ಮಳೆ", 61: "ಹಗುರ ಮಳೆ", 63: "ಮಧ್ಯಮ ಮಳೆ",
                65: "ಭಾರೀ ಮಳೆ", 80: "ಮಳೆಯ ಸಿಂಚನ", 95: "ಗುಡುಗು ಸಹಿತ ಬಿರುಗಾಳಿ"
            }
            return kn_map.get(code_val, "ಹವಾಮಾನ ಮಾಹಿತಿ ಲಭ್ಯವಿದೆ")
        elif language == "ml":
            ml_map = {
                0: "തെളിഞ്ഞ ആകാശം", 1: "മിക്കവാറും തെളിഞ്ഞത്", 2: "ഭാഗികമായി മേഘാവൃതം", 3: "കാർമേഘം",
                45: "മൂടൽമഞ്ഞ്", 51: "തുള്ളിമഴ", 61: "നേരിയ മഴ", 63: "മിതമായ മഴ",
                65: "കനത്ത മഴ", 80: "മഴച്ചാറ്റൽ", 95: "ഇടിമിന്നലോട് കൂടിയ മഴ"
            }
            return ml_map.get(code_val, "കാലാവസ്ഥ വിവരം ലഭ്യമാണ്")
        elif language == "or":
            or_map = {
                0: "ପରିଷ୍କାର ଆକାଶ", 1: "ମୁଖ୍ୟତଃ ପରିଷ୍କାର", 2: "ଆଂଶିକ ମେଘୁଆ", 3: "ପୂରା ମେଘୁଆ",
                45: "କୁହୁଡ଼ି", 51: "ଝିପିଝିପି ବର୍ଷା", 61: "ହାଲୁକା ବର୍ଷା", 63: "ମଧ୍ୟମ ବର୍ଷା",
                65: "ପ୍ରବଳ ବର୍ଷା", 80: "ବର୍ଷା ଝଲକ", 95: "ଘଡ଼ଘଡ଼ି ସହ ଝଡ଼ବର୍ଷା"
            }
            return or_map.get(code_val, "ପାଣିପାଗ ସୂଚନା ଉପଲବ୍ଧ")
        elif language == "as":
            as_map = {
                0: "পৰিষ্কাৰ আকাশ", 1: "প্ৰধানকৈ পৰিষ্কাৰ", 2: "আংশিক ডাৱৰীয়া", 3: "ডাৱৰীয়া",
                45: "কুঁৱলী", 51: "টোপাটোপে বৰষুণ", 61: "পাতলীয়া বৰষুণ", 63: "মজলীয়া বৰষুণ",
                65: "প্ৰবল বৰষুণ", 80: "বৰষুণৰ জাক", 95: "বজ্ৰপাতসহ ধুমুহা"
            }
            return as_map.get(code_val, "বতৰৰ তথ্য উপলব্ধ")
        elif language == "ur":
            ur_map = {
                0: "صاف آسمان", 1: "زیادہ تر صاف", 2: "جزوی ابر آلود", 3: "مکمل ابر آلود",
                45: "کہر", 51: "ہلکی بونداباندی", 61: "ہلکی بارش", 63: "معتدل بارش",
                65: "شدید بارش", 80: "تیز بچھاریں", 95: "گرج چمک کے ساتھ طوفان"
            }
            return ur_map.get(code_val, "موسم کی تفصیلات دستیاب ہیں")
        elif language == "mai":
            mai_map = {
                0: "साफ अकास", 1: "मुख्यतः साफ", 2: "आंशिक बादल", 3: "घने बादल",
                45: "कुहासा", 51: "हल्की बूंदाबांदी", 61: "हल्की वर्षा", 63: "मध्यम वर्षा",
                65: "भारी वर्षा", 80: "बरखा केर बौछार", 95: "ठनका आ आंधी संग वर्षा"
            }
            return mai_map.get(code_val, "मौसम केर जानकारी उपलब्ध अछि")
        elif language == "en":
            en_map = {
                0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
                45: "fog", 51: "light drizzle", 61: "light rain", 63: "rain",
                65: "heavy rain", 80: "rain showers", 95: "thunderstorm"
            }
            return en_map.get(code_val, "weather update available")
        else:
            hi_map = {
                0: "साफ आसमान", 1: "मुख्यतः साफ", 2: "आंशिक रूप से बादल", 3: "घने बादल",
                45: "कोहरा", 51: "हल्की बूंदाबांदी", 61: "हल्की बारिश", 63: "बारिश",
                65: "भारी बारिश", 80: "तेज बारिश की बौछारें", 95: "गरज-चमक के साथ आंधी"
            }
            return hi_map.get(code_val, "मौसम का पूर्वानुमान उपलब्ध")

    def _kmh_to_ms(self, speed_kmh: float | None) -> float:
        if speed_kmh is None:
            return 0.0
        return round(float(speed_kmh) / 3.6, 2)

    async def get_weather_timeline(
        self,
        lat: float,
        lon: float,
        forecast_days: int = 7,
        past_days: int = 7,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.core.language import resolve_language_code, get_current_language
        lang_code = resolve_language_code(language or get_current_language()).canonical_code
        loc_name, _ = await self._resolve_location_name(lat, lon)
        try:
            payload = await self._fetch_weather_bundle(lat, lon, forecast_days=forecast_days, past_days=past_days)
            daily = payload.get("daily", {})
            past_forecasts = self._build_daily_rows(daily, past_days, past=True, language=lang_code)
            future_forecasts = self._build_daily_rows(daily, forecast_days, language=lang_code)

            return {
                "success": True,
                "location": loc_name,
                "past_days": past_forecasts,
                "forecast_days": future_forecasts,
                "language": lang_code,
                "farming_advice": self._generate_forecast_advice(future_forecasts, language=lang_code),
                "source": "Open-Meteo"
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Open-Meteo timeline request failed: {str(exc)}",
                "source": "Open-Meteo"
            }

    async def get_historical_rainfall(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        cache_key = f"hist_rain:{round(lat, 3)}:{round(lon, 3)}:{start_date}:{end_date}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": "precipitation_sum",
                "timezone": "auto",
            }
            async with httpx.AsyncClient(timeout=httpx.Timeout(25.0), trust_env=False) as client:
                response = await client.get(self.historical_url, params=params)
                response.raise_for_status()
                payload = response.json()

            daily = payload.get("daily", {})
            precip_values = daily.get("precipitation_sum", [])
            valid_values = [p for p in precip_values if p is not None]
            total_rainfall = round(sum(valid_values), 1)

            res = {
                "success": True,
                "total_rainfall_mm": total_rainfall,
                "annual_rainfall_mm": total_rainfall,
                "total_precipitation_mm": total_rainfall,
                "daily_rainfall": valid_values,
                "days_count": len(valid_values),
                "start_date": start_date,
                "end_date": end_date,
                "source": "Open-Meteo-ERA5-Land",
                "rainfall_source": "Open-Meteo ERA5-Land",
            }
            self._set_cache(cache_key, res)
            return res
        except Exception as exc:
            return {
                "success": False,
                "error": f"Failed to fetch historical rainfall: {str(exc)}",
                "source": "Open-Meteo-ERA5-Land",
                "rainfall_source": "Open-Meteo ERA5-Land",
            }

    async def get_seasonal_rainfall(
        self,
        lat: float,
        lon: float,
        season: str,
        year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Calculates seasonal rainfall from ERA5 reanalysis data for crop recommendation models."""
        from datetime import date
        current_year = year or date.today().year
        season_lower = season.strip().lower()

        if season_lower == "kharif":
            start_date = f"{current_year}-06-01"
            end_date = f"{current_year}-10-31"
        elif season_lower == "rabi":
            start_date = f"{current_year - 1}-10-01"
            end_date = f"{current_year}-03-31"
        elif season_lower == "zaid":
            start_date = f"{current_year}-03-01"
            end_date = f"{current_year}-05-31"
        else:
            return {"success": False, "error": f"Unknown season '{season}'. Must be 'Kharif', 'Rabi', or 'Zaid'."}

        result = await self.get_historical_rainfall(lat, lon, start_date, end_date)
        if result.get("success"):
            result["season"] = season
            result["year"] = current_year
            result["rainfall_period"] = f"{season.capitalize()} {current_year}"
        return result

    async def get_annual_rainfall(
        self,
        lat: float,
        lon: float,
        year: Optional[int] = None,
    ) -> Dict[str, Any]:
        from datetime import date
        target_year = year or (date.today().year - 1)
        start_date = f"{target_year}-01-01"
        end_date = f"{target_year}-12-31"

        result = await self.get_historical_rainfall(lat, lon, start_date, end_date)
        if result.get("success"):
            result["year"] = target_year
            result["rainfall_period"] = str(target_year)
            result["annual_rainfall_mm"] = result.get("total_rainfall_mm")
            result["rainfall_source"] = "Open-Meteo ERA5-Land"
        return result


# Singleton
weather_agent = WeatherAgent()
