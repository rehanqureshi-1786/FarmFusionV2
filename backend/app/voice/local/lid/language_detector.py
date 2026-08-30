"""
Local Language Detector for Indic Languages.
Identifies Indic languages via Unicode script block analysis, character frequency, and agricultural lexicons.
"""
from typing import Dict, Any, List, Optional
import re
from app.voice.local.lid.base import LocalLanguageDetector, LocalLIDResult
from app.voice.languages import get_language_profile, LANGUAGE_REGISTRY


SCRIPT_RANGES = {
    "gu": (0x0A80, 0x0AFF), # Gujarati
    "pa": (0x0A00, 0x0A7F), # Gurmukhi (Punjabi)
    "bn": (0x0980, 0x09FF), # Bengali / Assamese
    "ta": (0x0B80, 0x0BFF), # Tamil
    "te": (0x0C00, 0x0C7F), # Telugu
    "kn": (0x0C80, 0x0CFF), # Kannada
    "ml": (0x0D00, 0x0D7F), # Malayalam
    "or": (0x0B00, 0x0B7F), # Odia
    "ur": (0x0600, 0x06FF), # Arabic / Urdu
    "hi": (0x0900, 0x097F), # Devanagari (Hindi, Marathi, Maithili, Rajasthani)
}


class LocalLanguageDetectorEngine(LocalLanguageDetector):
    def __init__(self, model_id: str = "farmfusion_lid_indic_v1"):
        self.model_id = model_id
        self._loaded = True

    def load(self) -> bool:
        self._loaded = True
        return True

    def is_available(self) -> bool:
        return self._loaded

    def capabilities(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "task": "lid",
            "supported_languages": list(LANGUAGE_REGISTRY.keys()),
            "is_available": True,
            "runtime": "rule_engine",
        }

    def detect_language(self, text: str) -> LocalLIDResult:
        if not text or not text.strip():
            return LocalLIDResult(detected_language="hi", confidence=1.0, script="Devanagari")

        cleaned = text.strip()
        
        # 1. Unicode script character distribution
        counts: Dict[str, int] = {lang: 0 for lang in SCRIPT_RANGES}
        latin_count = 0
        total_indic = 0

        for char in cleaned:
            code = ord(char)
            if (65 <= code <= 90) or (97 <= code <= 122):
                latin_count += 1
            for lang, (start, end) in SCRIPT_RANGES.items():
                if start <= code <= end:
                    counts[lang] += 1
                    total_indic += 1
                    break

        # Check code-switching (Latin + Indic characters)
        is_code_switched = (latin_count > 2 and total_indic > 2)

        # Disambiguate Bengali vs Assamese in Eastern Nagari script
        if counts["bn"] > 0:
            # Assamese specific characters: ৰ (\u09f0), ৱ (\u09f1)
            if "ৰ" in cleaned or "ৱ" in cleaned or "বতৰ" in cleaned:
                return LocalLIDResult(
                    detected_language="as",
                    confidence=0.95,
                    script="Bengali-Assamese",
                    is_code_switched=is_code_switched,
                    evidence=["assamese_specific_graphemes"],
                )
            return LocalLIDResult(
                detected_language="bn",
                confidence=0.95,
                script="Bengali",
                is_code_switched=is_code_switched,
            )

        # Devanagari script: Disambiguate Marathi vs Hindi vs Maithili
        if counts["hi"] > 0:
            # Marathi markers: "आहे", "मध्ये", "शेतात", "पीक", "भाव", "कसा"
            marathi_markers = ["आहे", "मध्ये", "शेतात", "पीक", "कसा", "करावे", "करावी", "नाही", "पाऊस"]
            if any(w in cleaned for w in marathi_markers):
                return LocalLIDResult(
                    detected_language="mr",
                    confidence=0.95,
                    script="Devanagari",
                    is_code_switched=is_code_switched,
                    evidence=["marathi_lexical_markers"],
                )
            # Maithili markers
            maithili_markers = ["अछि", "हमर", "तोहर", "कोना", "कहल", "भेल"]
            if any(w in cleaned for w in maithili_markers):
                return LocalLIDResult(
                    detected_language="mai",
                    confidence=0.92,
                    script="Devanagari",
                    is_code_switched=is_code_switched,
                    evidence=["maithili_lexical_markers"],
                )
            return LocalLIDResult(
                detected_language="hi",
                confidence=0.95,
                script="Devanagari",
                is_code_switched=is_code_switched,
            )

        # Distinct script matching
        for lang, count in counts.items():
            if count > 0 and lang not in ["hi", "bn"]:
                profile = get_language_profile(lang)
                return LocalLIDResult(
                    detected_language=lang,
                    confidence=0.96,
                    script=profile.script,
                    is_code_switched=is_code_switched,
                )

        # Latin script fallback (English or Romanized Hinglish)
        if latin_count > 0:
            hinglish_words = ["mausam", "kaisa", "khet", "fasal", "bhai", "aaj", "bhav", "rate", "gehu", "pani"]
            if any(w in cleaned.lower() for w in hinglish_words):
                return LocalLIDResult(
                    detected_language="hi",
                    confidence=0.90,
                    is_code_switched=True,
                    secondary_language="en",
                    script="Latin",
                    evidence=["romanized_hinglish_lexicon"],
                )
            return LocalLIDResult(
                detected_language="en",
                confidence=0.95,
                script="Latin",
                is_code_switched=False,
            )

        return LocalLIDResult(detected_language="hi", confidence=0.80, script="Devanagari")
