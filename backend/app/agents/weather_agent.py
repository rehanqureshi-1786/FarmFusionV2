"""
Weather agent powered by Open-Meteo.
Uses a free no-key weather API and returns normalized weather data for the app.
"""
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class WeatherAgent:
    def __init__(self) -> None:
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.historical_url = "https://archive-api.open-meteo.com/v1/archive"

    def is_available(self) -> bool:
        return True

    async def get_current_weather(self, lat: float, lon: float, language: Optional[str] = None) -> Dict[str, Any]:
        from app.core.language import resolve_language_code, get_current_language
        lang_code = resolve_language_code(language or get_current_language()).canonical_code
        try:
            payload = await self._fetch_weather_bundle(lat, lon, forecast_days=1, past_days=0)
            current = payload.get("current", {})
            daily = payload.get("daily", {})

            sunrise = daily.get("sunrise", [None])[0]
            sunset = daily.get("sunset", [None])[0]
            temperature = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind_speed = current.get("wind_speed_10m")
            weather_code = current.get("weather_code")

            return {
                "success": True,
                "location": "",
                "temperature_c": temperature,
                "feels_like_c": current.get("apparent_temperature", temperature),
                "humidity_percent": int(humidity or 0),
                "pressure_hpa": int(current.get("pressure_msl") or 0),
                "weather": self._weather_code_to_text(weather_code, language=lang_code),
                "wind_speed_ms": self._kmh_to_ms(current.get("wind_speed_10m")),
                "visibility_m": int(current.get("visibility") or 10000),
                "cloudiness_percent": int(current.get("cloud_cover") or 0),
                "sunrise": sunrise,
                "sunset": sunset,
                "language": lang_code,
                "farming_advice": self._generate_farming_advice(
                    temperature_c=temperature,
                    humidity_percent=humidity,
                    wind_speed_kmh=current.get("wind_speed_10m"),
                    weather_code=weather_code,
                    language=lang_code
                ),
                "source": "open-meteo"
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Open-Meteo weather request failed: {str(exc)}",
                "source": "open-meteo"
            }

    async def get_forecast(self, lat: float, lon: float, days: int = 5, language: Optional[str] = None) -> Dict[str, Any]:
        from app.core.language import resolve_language_code, get_current_language
        lang_code = resolve_language_code(language or get_current_language()).canonical_code
        try:
            payload = await self._fetch_weather_bundle(lat, lon, forecast_days=days, past_days=0)
            daily = payload.get("daily", {})
            forecasts = self._build_daily_rows(daily, days, language=lang_code)

            return {
                "success": True,
                "location": "",
                "forecast": forecasts,
                "language": lang_code,
                "farming_advice": self._generate_forecast_advice(forecasts, language=lang_code),
                "source": "open-meteo"
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Open-Meteo forecast request failed: {str(exc)}",
                "source": "open-meteo"
            }

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
        try:
            payload = await self._fetch_weather_bundle(
                lat,
                lon,
                forecast_days=forecast_days,
                past_days=past_days
            )
            daily = payload.get("daily", {})
            past_forecasts = self._build_daily_rows(daily, past_days, past=True, language=lang_code)
            future_forecasts = self._build_daily_rows(daily, forecast_days, language=lang_code)

            return {
                "success": True,
                "location": "",
                "past_days": past_forecasts,
                "forecast_days": future_forecasts,
                "language": lang_code,
                "farming_advice": self._generate_forecast_advice(future_forecasts, language=lang_code),
                "source": "open-meteo"
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Open-Meteo timeline request failed: {str(exc)}",
                "source": "open-meteo"
            }

    async def _fetch_weather_bundle(
        self,
        lat: float,
        lon: float,
        forecast_days: int,
        past_days: int
    ) -> Dict[str, Any]:
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
            return response.json()

    def _build_daily_rows(self, daily: Dict[str, Any], days: int, past: bool = False, language: str = "hi") -> List[Dict[str, Any]]:
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

        if wind_speed_kmh is not None and wind_speed_kmh > 20:
            advice_hi.append("तेज हवा - कीटनाशक छिड़काव स्थगित रखें")
            advice_gu.append("ઝડપી પવન - દવાનો છંટકાવ મોકૂફ રાખો")
            advice_mr.append("जोराचा वारा - कीटकनाशक फवारणी थांबवा")
            advice_pa.append("ਤੇਜ਼ ਹਵਾ - ਕੀਟਨਾਸ਼ਕ ਸਪਰੇਅ ਰੋਕੋ")
            advice_bn.append("দমকা হাওয়া - কীটনাশক স্প্রে করা স্থগিত রাখুন")
            advice_en.append("Windy conditions - delay foliar spraying")

        if weather_code is not None and weather_code in {61, 63, 65, 80, 81, 82, 95, 96, 99}:
            advice_hi.append("बारिश की संभावना - छिड़काव रोकें एवं जल निकासी रखें")
            advice_gu.append("વરસાદની શક્યતા - છંટકાવ અટકાવો અને પાણી નિકાલ રાખો")
            advice_mr.append("पावसाची शक्यता - फवारणी टाळा आणि पाण्याचा निचरा करा")
            advice_pa.append("ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ - ਸਪਰੇਅ ਰੋਕੋ ਅਤੇ ਨਿਕਾਸੀ ਯਕੀਨੀ ਬਣਾਓ")
            advice_bn.append("বৃষ্টির সম্ভাবনা - স্প্রে স্থগিত রাখুন ও নিকাশি বজায় রাখুন")
            advice_en.append("Rain likely - avoid spraying before showers and ensure drainage")

        lang_map = {
            "hi": " | ".join(advice_hi) if advice_hi else "मौसम खेती कार्यों के अनुकूल है",
            "gu": " | ".join(advice_gu) if advice_gu else "હવામાન ખેતી કામ માટે અનુકૂળ છે",
            "mr": " | ".join(advice_mr) if advice_mr else "हवामान शेतीकामासाठी अनुकूल आहे",
            "pa": " | ".join(advice_pa) if advice_pa else "ਮੌਸਮ ਖੇਤੀਬਾੜੀ ਕਾਰਜਾਂ ਲਈ ਅਨੁਕੂਲ ਹੈ",
            "bn": " | ".join(advice_bn) if advice_bn else "আবহাওয়া চাষের কাজের জন্য অনুকূল",
            "en": " | ".join(advice_en) if advice_en else "Good weather conditions for farm work"
        }
        return lang_map.get(language, lang_map["hi"] if language != "en" else lang_map["en"])

    def _generate_forecast_advice(self, forecasts: List[Dict[str, Any]], language: str = "hi") -> str:
        rainy_days = sum(1 for day in forecasts if day.get("rain_chance", 0) >= 40 or day.get("precipitation_mm", 0) > 1)
        hot_days = sum(1 for day in forecasts if day.get("temperature_max_c", 0) > 35)

        if language == "gu":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} દિવસ વરસાદની શક્યતા છે. સૂકા સમયમાં છંટકાવનું આયોજન કરો.")
            if hot_days: parts.append(f"{hot_days} દિવસ ગરમી વધુ રહેશે. પિયત તૈયાર રાખો.")
            return " ".join(parts) if parts else "આગામી દિવસોમાં હવામાન સ્થિર રહેશે. ખેતી કામ માટે સારું છે."
        elif language == "mr":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} दिवस पावसाची शक्यता आहे. कोरड्या वेळेत फवारणी करा.")
            if hot_days: parts.append(f"{hot_days} दिवस जास्त उष्णता राहील. पाणी देण्याची तयारी ठेवा.")
            return " ".join(parts) if parts else "हवामान साधारणपणे स्थिर राहील. शेतीच्या कामासाठी योग्य."
        elif language == "pa":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} ਦਿਨ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਹੈ। ਸੁੱਕੇ ਦਿਨਾਂ ਵਿੱਚ ਸਪਰੇਅ ਦੀ ਯੋਜਨਾ ਬਣਾਓ।")
            if hot_days: parts.append(f"{hot_days} ਦਿਨ ਗਰਮੀ ਵੱਧ ਰਹੇਗੀ। ਸਿੰਚਾਈ ਤਿਆਰ ਰੱਖੋ।")
            return " ".join(parts) if parts else "ਮੌਸਮ ਸਥਿਰ ਰਹਿਣ ਦੀ ਉਮੀਦ ਹੈ। ਖੇਤੀ ਲਈ ਚੰਗਾ।"
        elif language == "bn":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} দিন বৃষ্টির সম্ভাবনা রয়েছে। শুকনো দিনে স্প্রে করার পরিকল্পনা করুন।")
            if hot_days: parts.append(f"{hot_days} দিন তাপমাত্রা বেশি থাকবে। সেচের ব্যবস্থা প্রস্তুত রাখুন।")
            return " ".join(parts) if parts else "আবহাওয়া স্থিতিশীল থাকবে। মাঠের কাজের জন্য উপযুক্ত।"
        elif language == "en":
            parts = []
            if rainy_days: parts.append(f"{rainy_days} rainy day(s) expected. Plan spraying around dry windows.")
            if hot_days: parts.append(f"{hot_days} hot day(s) ahead. Keep irrigation ready.")
            return " ".join(parts) if parts else "Stable weather expected. Good for field operations."
        else:
            # Default Hindi
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
            # Default Hindi
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

    async def get_historical_rainfall(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """
        Fetch historical daily precipitation sum from Open-Meteo Historical API.
        
        Uses ERA5-Land reanalysis (0.1 degree, ~11km) for best India coverage.
        Data available from 1950 (ERA5) or 1981 (ERA5-Land) to present.
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict with success, daily precipitation values, and sum
        """
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
            dates = daily.get("time", [])
            
            # Filter out None values
            valid_precip = [float(p) for p in precip_values if p is not None]
            total = sum(valid_precip)
            
            return {
                "success": True,
                "daily_precipitation_mm": [
                    {"date": d, "precipitation_mm": float(p)}
                    for d, p in zip(dates, precip_values)
                    if p is not None
                ],
                "total_precipitation_mm": round(total, 2),
                "days_count": len(valid_precip),
                "source": "Open-Meteo ERA5-Land (historical)",
            }
        except httpx.TimeoutException:
            logger.warning("historical_rainfall_timeout lat=%s lon=%s", lat, lon)
            return {
                "success": False,
                "error": "Historical rainfall API timed out.",
                "source": "Open-Meteo",
            }
        except httpx.HTTPStatusError as exc:
            logger.warning("historical_rainfall_http_error status=%s", exc.response.status_code)
            return {
                "success": False,
                "error": f"Historical rainfall API returned HTTP {exc.response.status_code}.",
                "source": "Open-Meteo",
            }
        except httpx.HTTPError as exc:
            logger.warning("historical_rainfall_http_failure: %s", exc)
            return {
                "success": False,
                "error": f"Historical rainfall API request failed: {exc}.",
                "source": "Open-Meteo",
            }
        except (ValueError, TypeError, KeyError) as exc:
            logger.warning("historical_rainfall_parse_error: %s", exc)
            return {
                "success": False,
                "error": f"Historical rainfall API returned invalid response: {exc}.",
                "source": "Open-Meteo",
            }

    async def get_seasonal_rainfall(
        self,
        lat: float,
        lon: float,
        season: str,
        year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get seasonal rainfall for the given season and year.
        
        Seasons (Indian cropping calendar):
        - Kharif: June - October
        - Rabi: November - March (wraps year boundary)
        - Zaid: April - May
        
        Args:
            lat: Latitude
            lon: Longitude
            season: "Kharif", "Rabi", or "Zaid"
            year: Year (defaults to current year)
            
        Returns:
            Dict with seasonal rainfall total and daily breakdown
        """
        from datetime import datetime
        
        if year is None:
            year = datetime.now().year
        
        season_months = {
            "Kharif": (6, 10),   # June - October
            "Rabi": (11, 3),     # November - March (wraps)
            "Zaid": (4, 5),      # April - May
        }
        
        if season not in season_months:
            return {
                "success": False,
                "error": f"Unknown season: {season}",
                "source": "Open-Meteo",
            }
        
        start_month, end_month = season_months[season]
        
        if season == "Rabi":
            # Rabi wraps year boundary: Nov-Dec of previous year, Jan-Mar of current year
            start_date = f"{year - 1}-11-01"
            end_date = f"{year}-03-31"
        else:
            start_date = f"{year}-{start_month:02d}-01"
            # Get last day of end month
            if end_month == 10:
                end_day = 31
            elif end_month in (4, 6, 9, 11):
                end_day = 30
            elif end_month == 2:
                # Handle leap year
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                end_day = 29 if is_leap else 28
            else:
                end_day = 31
            end_date = f"{year}-{end_month:02d}-{end_day:02d}"
        
        return await self.get_historical_rainfall(lat, lon, start_date, end_date)

    async def get_annual_rainfall(
        self,
        lat: float,
        lon: float,
        year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get annual rainfall for the given year (previous complete calendar year).
        
        Args:
            lat: Latitude
            lon: Longitude
            year: Year (defaults to previous complete calendar year)
            
        Returns:
            Dict with annual rainfall total, daily breakdown, and provenance metadata
        """
        if year is None:
            # Use previous complete calendar year to ensure full year data
            year = datetime.now().year - 1
        
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        result = await self.get_historical_rainfall(lat, lon, start_date, end_date)
        if result.get("success"):
            result["annual_rainfall_mm"] = result.get("total_precipitation_mm", 0.0)
            result["rainfall_source"] = "Open-Meteo ERA5-Land"
            result["rainfall_period"] = str(year)
            result["source"] = "Open-Meteo ERA5-Land"
        return result


weather_agent = WeatherAgent()
