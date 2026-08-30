"""
Text Normalization Pipeline for Multilingual Indian Languages and Regional Dialects.
Handles:
- Unicode NFKC standardization
- Devanagari / Indic Nukta & Danda normalization
- Agricultural entity canonicalization
- Punctuation removal for acoustic ASR targets
"""
import unicodedata
import re
from typing import Dict, Any, Optional
from app.voice.languages import normalize_agricultural_term


class VoiceTextNormalizer:
    """
    Standardizes multilingual text across Indic scripts, Romanized Hinglish, and regional dialects.
    """
    @staticmethod
    def normalize_text(text: str, script: str = "Devanagari") -> str:
        if not text:
            return ""

        # 1. Unicode NFKC normalization
        norm = unicodedata.normalize("NFKC", text.strip())

        # 2. Standardize whitespace
        norm = re.sub(r"\s+", " ", norm)

        # 3. Standardize Devanagari Danda
        norm = norm.replace("।", " ").replace("॥", " ")

        # 4. Strip non-informative punctuation
        norm = re.sub(r"[?!,;:\"'()\[\]{}—_`~]", " ", norm)

        return norm.strip()

    @staticmethod
    def prepare_asr_target(text: str) -> str:
        """Strip all punctuation and lowercase for acoustic model training targets."""
        norm = VoiceTextNormalizer.normalize_text(text)
        return re.sub(r"[^\w\s\u0900-\u0D7F]", "", norm).lower().strip()

    @staticmethod
    def canonicalize_agri_entities(text: str) -> str:
        """Map dialect words to canonical names."""
        words = text.split()
        canonical_words = []
        for w in words:
            term = normalize_agricultural_term(w)
            if term:
                name = term.canonical_name if hasattr(term, "canonical_name") else term.get("canonical_name", w)
                canonical_words.append(name)
            else:
                canonical_words.append(w)
        return " ".join(canonical_words)
