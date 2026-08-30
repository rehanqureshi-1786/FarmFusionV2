"""
Local Dialect Detection and Regional Normalization Engine.
Provides deterministic dialect identification (Marwari, Mewari, Bhojpuri, Haryanvi, etc.) with evidence verification.
"""
from typing import Dict, Any, List, Optional
from app.voice.local.dialect.base import LocalDialectModel, LocalDialectResult
from app.voice.languages import detect_dialect, normalize_agricultural_term, LANGUAGE_REGISTRY


class LocalDialectEngine(LocalDialectModel):
    def __init__(self, model_id: str = "farmfusion_dialect_rajasthani_v1"):
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
            "task": "dialect",
            "supported_dialects": ["rwr", "mew", "dhu", "bho", "bgc", "awa", "hne", "mup", "kat"],
            "is_available": True,
            "runtime": "rule_engine",
        }

    def detect_and_normalize(self, text: str, detected_language: str = "hi") -> LocalDialectResult:
        res = detect_dialect(text, detected_language=detected_language)
        
        # Word-level vocabulary normalization
        words = text.split()
        normalized_words = []
        for w in words:
            norm = normalize_agricultural_term(w)
            if norm:
                canon_name = norm.canonical_name if hasattr(norm, "canonical_name") else (norm.get("canonical_name", w) if isinstance(norm, dict) else w)
                normalized_words.append(canon_name)
            else:
                normalized_words.append(w)

        return LocalDialectResult(
            parent_language=res.language,
            detected_dialect=res.dialect,
            confidence=res.confidence,
            support_tier=res.support_tier,
            is_native=True,
            evidence=res.evidence,
            normalized_text=" ".join(normalized_words),
        )
