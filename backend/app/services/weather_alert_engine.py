"""
Deterministic Weather Alert Engine for FarmFusion.
Evaluates physical weather parameters against agronomic thresholds and produces
deduplicated, actionable agricultural weather warnings in the farmer's preferred language.
"""

import hashlib
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas.weather import WeatherAlertItem, DailyForecastItem, CurrentWeather
from app.core.language import resolve_language_code

# Configurable agronomic thresholds (Metric units)
THRESHOLDS = {
    "HEAVY_RAIN_MM": 40.0,            # Daily precipitation sum >= 40mm
    "MODERATE_RAIN_MM": 25.0,         # Daily precipitation sum >= 25mm with high probability
    "HEATWAVE_MAX_C": 40.0,           # Daily max temperature >= 40°C
    "EXTREME_HEATWAVE_MAX_C": 44.0,   # Daily max temperature >= 44°C
    "FROST_MIN_C": 4.0,               # Daily min temperature <= 4°C (ground frost risk)
    "HIGH_WIND_KMH": 35.0,            # Max wind speed >= 35 km/h (risk of crop lodging & spray drift)
    "GALE_WIND_KMH": 50.0,            # Severe windstorm >= 50 km/h
}

ALERT_LOCALIZATIONS = {
    "HEAVY_RAIN": {
        "hi": {
            "title": "भारी बारिश की चेतावनी",
            "message": "आगामी 24-48 घंटों में {val} मिमी भारी बारिश का अनुमान है।",
            "recommendation": "खेत में जल निकासी (ड्रेनेज) की व्यवस्था करें। कीटनाशक छिड़काव एवं सिंचाई तुरंत रोक दें।"
        },
        "gu": {
            "title": "ભારે વરસાદની ચેતવણી",
            "message": "આગામી સમયમાં {val} મીમી ભારે વરસાદ થવાની શક્યતા છે.",
            "recommendation": "ખેતરમાંથી વધારાના પાણીના નિકાલની વ્યવસ્થા કરો. પિયત અને દવાનો છંટકાવ મોકૂફ રાખો."
        },
        "mr": {
            "title": "मुसळधार पावसाचा इशारा",
            "message": "पुढील २४ ते ४८ तासांत {val} मिमी मुसळधार पावसाचा अंदाज आहे.",
            "recommendation": "शेतातून पाणी निचरा होण्याची सोय करा. खत व कीटकनाशक फवारणी पुढे ढकला."
        },
        "pa": {
            "title": "ਭਾਰੀ ਬਾਰਿਸ਼ ਦੀ ਚੇਤਾਵਨੀ",
            "message": "ਅਗਲੇ ਸਮੇਂ ਵਿੱਚ {val} ਮਿਮੀ ਭਾਰੀ ਬਾਰਿਸ਼ ਦੀ ਸੰਭਾਵਨਾ ਹੈ।",
            "recommendation": "ਖੇਤ ਵਿੱਚ ਪਾਣੀ ਦੀ ਨਿਕਾਸੀ ਦਾ ਪ੍ਰਬੰਧ ਕਰੋ। ਸਪਰੇਅ ਅਤੇ ਸਿੰਚਾਈ ਰੋਕੋ।"
        },
        "bn": {
            "title": "ভারী বৃষ্টির সতর্কতা",
            "message": "আগামী ২৪-৪৮ ঘণ্টায় {val} মিমি ভারী বৃষ্টির সম্ভাবনা রয়েছে।",
            "recommendation": "জমি থেকে অতিরিক্ত জল নিষ্কাশনের ব্যবস্থা করুন। সার ও কীটনাশক স্প্রে স্থগিত রাখুন।"
        },
        "en": {
            "title": "Heavy Rainfall Warning",
            "message": "Forecast indicates heavy precipitation of {val} mm.",
            "recommendation": "Ensure field drainage. Pause all chemical spraying and scheduled irrigation."
        }
    },
    "THUNDERSTORM": {
        "hi": {
            "title": "आंधी-तूफान एवं गरज-चमक की चेतावनी",
            "message": "तेज हवाओं और गरज-चमक के साथ आंधी-तूफान की आशंका है।",
            "recommendation": "कटी हुई फसल को तुरंत सुरक्षित स्थान पर ढकें। कृषि उपकरणों को सुरक्षित रखें।"
        },
        "gu": {
            "title": "વાવાઝોડું અને વીજળીની ચેતવણી",
            "message": "તેજ પવન અને ગાજવીજ સાથે વાવાઝોડું આવવાની શક્યતા છે.",
            "recommendation": "લણેલા પાકને સુરક્ષિત ઢાંકી દો અને ખેતીના સાધનો સુરક્ષિત જગ્યાએ મૂકો."
        },
        "mr": {
            "title": "वादळी पावसाचा इशारा",
            "message": "विजांच्या कडकडाटासह वादळी पावसाची शक्यता आहे.",
            "recommendation": "कापणी केलेले पीक तातडीने सुरक्षित ठिकाणी ठेवा. शेती अवजारे सुरक्षित करा."
        },
        "pa": {
            "title": "ਗਰਜ ਅਤੇ ਤੂਫਾਨ ਦੀ ਚੇਤਾਵਨੀ",
            "message": "ਤੇਜ਼ ਹਵਾਵਾਂ ਅਤੇ ਗਰਜ-ਚਮਕ ਨਾਲ ਤੂਫਾਨ ਆਉਣ ਦਾ ਖਦਸ਼ਾ ਹੈ।",
            "recommendation": "ਵੱਢੀ ਹੋਈ ਫਸਲ ਨੂੰ ਤੁਰੰਤ ਢੱਕ ਕੇ ਸੁਰੱਖਿਅਤ ਕਰੋ।"
        },
        "bn": {
            "title": "বজ্রবিদ্যুৎসহ ঝড়ের সতর্কতা",
            "message": "ঝড়ো হাওয়া এবং বজ্রপাতসহ তীব্র ঝড়ের আশঙ্কা রয়েছে।",
            "recommendation": "কাটা ফসল নিরাপদে ঢেকে রাখুন এবং খোলা মাঠে কাজ করা থেকে বিরত থাকুন।"
        },
        "en": {
            "title": "Severe Thunderstorm Warning",
            "message": "High risk of thunderstorms with strong wind gusts.",
            "recommendation": "Protect harvested produce and secure lightweight farm structures immediately."
        }
    },
    "HEATWAVE": {
        "hi": {
            "title": "भीषण गर्मी एवं लू (हीटवेव) की चेतावनी",
            "message": "अधिकतम तापमान {val}°C तक पहुंचने का अनुमान है।",
            "recommendation": "फसलों में नमी बनाए रखने के लिए शाम के समय हल्की सिंचाई करें। दोपहर में खेत कार्य से बचें।"
        },
        "gu": {
            "title": "તીવ્ર ગરમી / હીટવેવની ચેતવણી",
            "message": "મહત્તમ તાપમાન {val}°C સુધી પહોંચવાની શક્યતા છે.",
            "recommendation": "સાંજના સમયે હળવું પિયત આપો જેથી જમીનમાં ભેજ જળવાઈ રહે."
        },
        "mr": {
            "title": "उष्णतेच्या लाटेचा इशारा",
            "message": "कमाल तापमान {val}°C पर्यंत जाण्याची शक्यता आहे.",
            "recommendation": "पिकांना संध्याकाळी हलके पाणी द्या जेणेकरून जमिनीत ओलावा राहील."
        },
        "pa": {
            "title": "ਗਰਮੀ ਦੀ ਲਹਿਰ (ਹੀਟਵੇਵ) ਚੇਤਾਵਨੀ",
            "message": "ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ {val}°C ਤੱਕ ਪਹੁੰਚਣ ਦੀ ਸੰਭਾਵਨਾ ਹੈ।",
            "recommendation": "ਸ਼ਾਮ ਨੂੰ ਹਲਕੀ ਸਿੰਚਾਈ ਕਰੋ ਤਾਂ ਜੋ ਫਸਲਾਂ ਸੁੱਕਣ ਤੋਂ ਬਚ ਸਕਣ।"
        },
        "bn": {
            "title": "তীব্র তাপদাহের সতর্কতা",
            "message": "সর্বোচ্চ তাপমাত্রা {val}°C পর্যন্ত পৌঁছাতে পারে।",
            "recommendation": "মাটির আর্দ্রতা ধরে রাখতে সন্ধ্যার সময় হালকা সেচ প্রদান করুন।"
        },
        "en": {
            "title": "Heatwave Advisory",
            "message": "Maximum temperature expected to reach {val}°C.",
            "recommendation": "Provide light evening irrigation to mitigate heat stress. Avoid midday field labor."
        }
    },
    "FROST": {
        "hi": {
            "title": "पाला (तुषार) पड़ने का जोखिम",
            "message": "रात का न्यूनतम तापमान {val}°C तक गिरने का अनुमान है, जिससे पाला पड़ सकता है।",
            "recommendation": "खेत की मेड़ों पर शाम को धुआं करें अथवा हल्की सिंचाई करें ताकि फसलें पाले से सुरक्षित रहें।"
        },
        "gu": {
            "title": "હિમ અને ઠંડીનું જોખમ",
            "message": "રાત્રિનું લઘુત્તમ તાપમાન {val}°C સુધી ઘટી શકે છે, જેથી હિમ લાગવાની શક્યતા છે.",
            "recommendation": "પાકને બચાવવા માટે સાંજે હળવું પિયત આપો અથવા ખેતરના શેઢે ધુમાડો કરો."
        },
        "mr": {
            "title": "धुके व थंडीची लाट (दव पडण्याचा धोका)",
            "message": "किमान तापमान {val}°C पर्यंत खाली येण्याची शक्यता आहे.",
            "recommendation": "पिकांचे थंडीपासून संरक्षण करण्यासाठी हलके पाणी द्या किंवा धूर करा."
        },
        "pa": {
            "title": "ਕੋਰਾ (ਪਾਲਾ) ਪੈਣ ਦਾ ਖਦਸ਼ਾ",
            "message": "ਰਾਤ ਦਾ ਘੱਟੋ-ਘੱਟ ਤਾਪਮਾਨ {val}°C ਤੱਕ ਡਿੱਗਣ ਦਾ ਅਨੁਮਾਨ ਹੈ।",
            "recommendation": "ਫਸਲ ਨੂੰ ਪਾਲੇ ਤੋਂ ਬਚਾਉਣ ਲਈ ਹਲਕੀ ਸਿੰਚਾਈ ਕਰੋ।"
        },
        "bn": {
            "title": "তীব্র শৈত্যপ্রবাহ ও কুয়াশার সতর্কতা",
            "message": "রাতের সর্বনিম্ন তাপমাত্রা {val}°C-এ নেমে যেতে পারে।",
            "recommendation": "ফসল রক্ষায় হালকা সেচ দিন অথবা খড়ের ছাউনি দিয়ে চারা গাছ ঢেকে দিন।"
        },
        "en": {
            "title": "Frost / Cold Wave Warning",
            "message": "Night temperature dropping to {val}°C with severe frost risk.",
            "recommendation": "Apply light surface irrigation or create smoke barriers on windward edges to insulate crops."
        }
    },
    "HIGH_WIND": {
        "hi": {
            "title": "तेज हवाओं की चेतावनी",
            "message": "हवा की गति {val} किमी/घंटा तक पहुंचने का अनुमान है।",
            "recommendation": "लंबी फसलों को सहारा दें। तेज हवा में कीटनाशक का छिड़काव बिल्कुल न करें।"
        },
        "gu": {
            "title": "તેજ પવનની ચેતવણી",
            "message": "પવનની ગતિ {val} કિમી/કલાક સુધી પહોંચવાની શક્યતા છે.",
            "recommendation": "ઊંચા પાકને ટેકો આપો. પવન દરમિયાન દવાનો છંટકાવ ટાળો."
        },
        "mr": {
            "title": "वेगवान वाऱ्याचा इशारा",
            "message": "वाऱ्याचा वेग {val} किमी/तास राहण्याचा अंदाज आहे.",
            "recommendation": "उंच पिकांना आधार द्या. जोरदार वाऱ्यात फवारणी करू नका."
        },
        "pa": {
            "title": "ਤੇਜ਼ ਹਵਾਵਾਂ ਦੀ ਚੇਤਾਵਨੀ",
            "message": "ਹਵਾ ਦੀ ਰਫ਼ਤਾਰ {val} ਕਿਮੀ/ਘੰਟਾ ਤੱਕ ਜਾ ਸਕਦੀ ਹੈ।",
            "recommendation": "ਲੰਬੀਆਂ ਫਸਲਾਂ ਨੂੰ ਸਹਾਰਾ ਦਿਓ ਅਤੇ ਸਪਰੇਅ ਕਰਨ ਤੋਂ ਬਚੋ।"
        },
        "bn": {
            "title": "প্রবল বাতাসের সতর্কতা",
            "message": "বাতাসের গতিবেগ ঘণ্টায় {val} কিমি পর্যন্ত হতে পারে।",
            "recommendation": "লম্বা গাছে ঠেস দিন এবং স্প্রে করার কাজ স্থগিত রাখুন।"
        },
        "en": {
            "title": "High Wind Advisory",
            "message": "Wind gusts up to {val} km/h expected.",
            "recommendation": "Stake tall crops to prevent lodging. Postpone pesticide/fertilizer foliar spraying."
        }
    }
}


class WeatherAlertEngine:
    """Central deterministic rule-based engine evaluating weather alerts."""

    def __init__(self):
        # Cache of recently generated alert IDs to enforce deduplication (alert_id -> timestamp)
        self._dedup_cache: Dict[str, float] = {}
        self.dedup_window_seconds = 21600  # 6 hours deduplication window

    def generate_deterministic_id(
        self,
        alert_type: str,
        lat: float,
        lon: float,
        date_str: str,
        trigger_val: float
    ) -> str:
        """Computes a deterministic hash ID to identify unique weather alert events."""
        raw_key = f"{alert_type}:{round(lat, 2)}:{round(lon, 2)}:{date_str}:{round(trigger_val, 1)}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def _get_localized_text(self, alert_type: str, lang: str, val: Any) -> Dict[str, str]:
        resolved_lang = resolve_language_code(lang).canonical_code
        type_dict = ALERT_LOCALIZATIONS.get(alert_type, {})
        lang_dict = type_dict.get(resolved_lang, type_dict.get("hi", type_dict.get("en", {})))

        val_str = str(round(float(val), 1) if isinstance(val, (int, float)) else val)
        return {
            "title": lang_dict.get("title", f"{alert_type} Alert"),
            "message": lang_dict.get("message", "").format(val=val_str),
            "recommendation": lang_dict.get("recommendation", "")
        }

    def evaluate_forecast(
        self,
        lat: float,
        lon: float,
        forecasts: List[DailyForecastItem],
        location_name: Optional[str] = None,
        language: str = "hi"
    ) -> List[WeatherAlertItem]:
        """
        Evaluates a multi-day forecast against deterministic thresholds.
        Returns deduplicated alerts sorted by severity and chronological start time.
        """
        alerts: List[WeatherAlertItem] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for day in forecasts:
            d_str = day.date

            # 1. HEAVY RAIN CHECK
            if day.precipitation_mm >= THRESHOLDS["HEAVY_RAIN_MM"] or (
                day.precipitation_mm >= THRESHOLDS["MODERATE_RAIN_MM"] and day.precipitation_probability_percent >= 80
            ):
                aid = self.generate_deterministic_id("HEAVY_RAIN", lat, lon, d_str, day.precipitation_mm)
                loc_txt = self._get_localized_text("HEAVY_RAIN", language, day.precipitation_mm)
                severity = "EMERGENCY" if day.precipitation_mm >= 65.0 else "WARNING"
                alerts.append(WeatherAlertItem(
                    alert_id=aid,
                    alert_type="HEAVY_RAIN",
                    severity=severity,
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    start_time=f"{d_str}T00:00:00Z",
                    end_time=f"{d_str}T23:59:59Z",
                    trigger_value=day.precipitation_mm,
                    threshold_value=THRESHOLDS["HEAVY_RAIN_MM"],
                    unit="mm",
                    title=loc_txt["title"],
                    message=loc_txt["message"],
                    farming_recommendation=loc_txt["recommendation"],
                    source="Open-Meteo-NWP",
                    created_at=now_iso
                ))

            # 2. THUNDERSTORM / HAIL CHECK (WMO codes 95, 96, 99)
            if day.weather_code in (95, 96, 99):
                aid = self.generate_deterministic_id("THUNDERSTORM", lat, lon, d_str, day.weather_code)
                loc_txt = self._get_localized_text("THUNDERSTORM", language, day.condition)
                alerts.append(WeatherAlertItem(
                    alert_id=aid,
                    alert_type="THUNDERSTORM",
                    severity="EMERGENCY",
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    start_time=f"{d_str}T00:00:00Z",
                    end_time=f"{d_str}T23:59:59Z",
                    trigger_value=float(day.weather_code),
                    threshold_value=95.0,
                    unit="WMO Code",
                    title=loc_txt["title"],
                    message=loc_txt["message"],
                    farming_recommendation=loc_txt["recommendation"],
                    source="Open-Meteo-NWP",
                    created_at=now_iso
                ))

            # 3. HEATWAVE CHECK
            if day.temperature_max_c >= THRESHOLDS["HEATWAVE_MAX_C"]:
                aid = self.generate_deterministic_id("HEATWAVE", lat, lon, d_str, day.temperature_max_c)
                loc_txt = self._get_localized_text("HEATWAVE", language, day.temperature_max_c)
                severity = "EMERGENCY" if day.temperature_max_c >= THRESHOLDS["EXTREME_HEATWAVE_MAX_C"] else "WARNING"
                alerts.append(WeatherAlertItem(
                    alert_id=aid,
                    alert_type="HEATWAVE",
                    severity=severity,
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    start_time=f"{d_str}T11:00:00Z",
                    end_time=f"{d_str}T17:00:00Z",
                    trigger_value=day.temperature_max_c,
                    threshold_value=THRESHOLDS["HEATWAVE_MAX_C"],
                    unit="°C",
                    title=loc_txt["title"],
                    message=loc_txt["message"],
                    farming_recommendation=loc_txt["recommendation"],
                    source="Open-Meteo-NWP",
                    created_at=now_iso
                ))

            # 4. FROST CHECK
            if day.temperature_min_c <= THRESHOLDS["FROST_MIN_C"]:
                aid = self.generate_deterministic_id("FROST", lat, lon, d_str, day.temperature_min_c)
                loc_txt = self._get_localized_text("FROST", language, day.temperature_min_c)
                severity = "EMERGENCY" if day.temperature_min_c <= 1.0 else "WARNING"
                alerts.append(WeatherAlertItem(
                    alert_id=aid,
                    alert_type="FROST",
                    severity=severity,
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    start_time=f"{d_str}T02:00:00Z",
                    end_time=f"{d_str}T07:00:00Z",
                    trigger_value=day.temperature_min_c,
                    threshold_value=THRESHOLDS["FROST_MIN_C"],
                    unit="°C",
                    title=loc_txt["title"],
                    message=loc_txt["message"],
                    farming_recommendation=loc_txt["recommendation"],
                    source="Open-Meteo-NWP",
                    created_at=now_iso
                ))

            # 5. HIGH WIND CHECK
            wind_kmh = day.wind_speed_max_kmh or (day.wind_speed_max_ms * 3.6)
            if wind_kmh >= THRESHOLDS["HIGH_WIND_KMH"]:
                aid = self.generate_deterministic_id("HIGH_WIND", lat, lon, d_str, wind_kmh)
                loc_txt = self._get_localized_text("HIGH_WIND", language, wind_kmh)
                severity = "EMERGENCY" if wind_kmh >= THRESHOLDS["GALE_WIND_KMH"] else "WARNING"
                alerts.append(WeatherAlertItem(
                    alert_id=aid,
                    alert_type="HIGH_WIND",
                    severity=severity,
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    start_time=f"{d_str}T06:00:00Z",
                    end_time=f"{d_str}T20:00:00Z",
                    trigger_value=wind_kmh,
                    threshold_value=THRESHOLDS["HIGH_WIND_KMH"],
                    unit="km/h",
                    title=loc_txt["title"],
                    message=loc_txt["message"],
                    farming_recommendation=loc_txt["recommendation"],
                    source="Open-Meteo-NWP",
                    created_at=now_iso
                ))

        # Deduplicate against recent emission history
        current_ts = time.time()
        deduplicated: List[WeatherAlertItem] = []
        for alert in alerts:
            last_seen = self._dedup_cache.get(alert.alert_id)
            if last_seen is None or (current_ts - last_seen) >= self.dedup_window_seconds:
                self._dedup_cache[alert.alert_id] = current_ts
                deduplicated.append(alert)

        return deduplicated

# Module singleton
weather_alert_engine = WeatherAlertEngine()
