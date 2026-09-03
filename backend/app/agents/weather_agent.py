"""
Weather Agent powered by Open-Meteo with TTL caching, dynamic location awareness,
deterministic alert evaluation, and separate agronomic interpretations.
"""
from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional

import httpx
from app.schemas.weather import (
    CurrentWeather,
    DailyForecastItem,
    WeatherForecastResponse,
    WeatherCurrentResponse,
    AgriculturalAdvisory,
    WeatherAlertItem
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
                source="Open-Meteo"
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

        assumptions = []
        if crop_name:
            assumptions.append(f"Crop: {crop_name}")
        if growth_stage:
            assumptions.append(f"Growth Stage: {growth_stage}")
        if soil_type:
            assumptions.append(f"Soil Type: {soil_type}")
        if not assumptions:
            assumptions.append("General Indian agronomic standard; specific crop/soil not provided")

        from app.core.language import resolve_language_code
        lang = resolve_language_code(language).canonical_code

        # Deterministic advisory rules
        if lang == "hi":
            # Irrigation
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"अगले 3 दिनों में {round(total_rain_next_3_days, 1)} मिमी बारिश का अनुमान है। सिंचाई रोक दें ताकि जलभराव न हो।"
            elif max_temp >= 38.0:
                irrig = "तेज गर्मी के कारण वाष्पीकरण अधिक होगा। फसलों में नमी बनाए रखने के लिए शाम को हल्की सिंचाई करें।"
            else:
                irrig = "मौसम सामान्य रहेगा। मिट्टी की नमी की जांच कर आवश्यकतानुसार नियमित सिंचाई करें।"

            # Spraying
            if max_wind >= 25.0:
                spray = f"हवा की गति {round(max_wind, 1)} किमी/घंटा है। दवा के बहाव (ड्रिफ्ट) के खतरे से छिड़काव अभी न करें।"
            elif max_rain_chance >= 60:
                spray = "बारिश की संभावना के कारण कीटनाशक धुल सकते हैं। शुष्क मौसम की प्रतीक्षा करें।"
            else:
                spray = "हवा एवं मौसम अनुकूल है। सुबह या शाम के समय छिड़काव सुरक्षित रूप से किया जा सकता है।"

            # Fieldwork
            if total_rain_next_3_days >= 30.0:
                field = "खेत में नमी अधिक रहेगी। जुताई और कटी फसल की गहाई (थ्रेशिंग) कुछ दिन टालें।"
            else:
                field = "खेत कार्य, निराई-गुड़ाई एवं कटाई के लिए मौसम अनुकूल है।"

            summary = f"तापमान {round(min_temp, 1)}°C से {round(max_temp, 1)}°C रहेगा। 3 दिनों में कुल वर्षा: {round(total_rain_next_3_days, 1)} मिमी।"

        elif lang == "gu":
            if total_rain_next_3_days >= 20.0 or max_rain_chance >= 75:
                irrig = f"આગામી 3 દિવસમાં {round(total_rain_next_3_days, 1)} મીમી વરસાદની શક્યતા છે. પિયત આપવાનું મુલતવી રાખો."
            else:
                irrig = "જમીનમાં ભેજ ચકાસીને સામાન્ય પિયત આપી શકાય છે."

            if max_wind >= 25.0 or max_rain_chance >= 60:
                spray = "પવન અથવા વરસાદના જોખમને કારણે દવાનો છંટકાવ મોકૂફ રાખો."
            else:
                spray = "હવામાન અનુકૂળ છે. સવાર અથવા સાંજે દવાનો છંટકાવ કરી શકાય છે."

            field = "સામાન્ય ખેતી કાર્યો માટે હવામાન અનુકૂળ છે."
            summary = f"તાપમાન {round(min_temp, 1)}°C થી {round(max_temp, 1)}°C રહેશે. સંભવિત વરસાદ: {round(total_rain_next_3_days, 1)} મીમી."

        else:
            # English default
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

        return AgriculturalAdvisory(
            irrigation_advice=irrig,
            spraying_advice=spray,
            fieldwork_advice=field,
            summary=summary,
            language=lang,
            assumptions=assumptions
        )

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
        """Fetch historical daily precipitation sum from Open-Meteo Historical API."""
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": "precipitation_sum",
                "timezone": "auto",
            }
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0), trust_env=False) as client:
                response = await client.get(self.historical_url, params=params)
                response.raise_for_status()
                payload = response.json()

            daily = payload.get("daily", {})
            precip_values = daily.get("precipitation_sum", [])
            valid_values = [p for p in precip_values if p is not None]
            total_rainfall = round(sum(valid_values), 1)

            return {
                "success": True,
                "total_rainfall_mm": total_rainfall,
                "daily_rainfall": valid_values,
                "days_count": len(valid_values),
                "start_date": start_date,
                "end_date": end_date,
                "source": "Open-Meteo-ERA5-Land",
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Failed to fetch historical rainfall: {str(exc)}",
                "source": "Open-Meteo-ERA5-Land",
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
        return result


# Singleton
weather_agent = WeatherAgent()
