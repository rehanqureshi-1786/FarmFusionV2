"""
FarmFusion Central Voice Provider Router.
Orchestrates capability discovery, provider selection (Local vs Bhashini vs Fallback),
and prioritizes genuine LOCAL NEURAL TTS whenever an authentic model binary is installed,
falling back transparently to verified remote Bhashini TTS.
"""
from typing import Dict, Any, Optional, List
import structlog
from pydantic import BaseModel, Field

from app.voice.profiles import (
    get_voice_capability,
    get_language_profile,
    VoiceCapabilityProfile,
    CapabilityTier,
)
from app.voice.local.model_registry import local_model_registry
from app.voice.local.config import local_voice_config, RuntimeMode
from app.voice.local.tts.local_tts import local_tts_engine
from app.voice.bhashini import BhashiniClient

logger = structlog.get_logger(__name__)


class ProviderRoutingDecision(BaseModel):
    task: str
    requested_language: str
    requested_dialect: Optional[str] = None
    actual_tts_language: str
    actual_tts_dialect: Optional[str] = None
    selected_provider: str
    selected_model: Optional[str] = None
    capability_tier: CapabilityTier
    is_local: bool = True
    is_native: bool = False
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    offline_supported: bool = True

    @property
    def target_language(self) -> str:
        return self.actual_tts_language

    @property
    def model_id(self) -> Optional[str]:
        return self.selected_model


class UniversalVoiceProviderRouter:
    """
    Decides the best verified provider for ASR, LID, NLU, Response Localization, and TTS.
    Prioritizes genuine LOCAL NEURAL TTS when weights exist, otherwise cascades to Bhashini.
    """
    def __init__(self, bhashini_client: Optional[BhashiniClient] = None):
        self.bhashini_client = bhashini_client or BhashiniClient()

    def route_asr(
        self,
        language: str,
        dialect: Optional[str] = None,
        mode: RuntimeMode = RuntimeMode.HYBRID
    ) -> ProviderRoutingDecision:
        """Route ASR request based on verified provider capabilities."""
        cap = get_voice_capability(language if not dialect else dialect)
        if dialect and dialect in ["rwr", "mew", "bho", "bgc", "awa", "dhu", "hne"]:
            return ProviderRoutingDecision(
                task="asr",
                requested_language=language,
                requested_dialect=dialect,
                actual_tts_language=language,
                actual_tts_dialect=None,
                selected_provider="bhashini_parent_asr_with_dialect_normalization" if mode != RuntimeMode.OFFLINE else "local_parent_asr",
                selected_model="bhashini_hindi_asr" if mode != RuntimeMode.OFFLINE else "local_conformer_hindi_int8",
                capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
                is_local=(mode == RuntimeMode.OFFLINE),
                is_native=False,
                fallback_used=True,
                fallback_reason="DIALECT_ASR_USES_PARENT_LANGUAGE_WITH_NORMALIZATION",
                offline_supported=cap.offline_available,
            )

        if cap.asr_available and mode != RuntimeMode.OFFLINE:
            return ProviderRoutingDecision(
                task="asr",
                requested_language=language,
                requested_dialect=dialect,
                actual_tts_language=language,
                actual_tts_dialect=dialect,
                selected_provider=cap.asr_provider or "bhashini",
                selected_model=cap.asr_model or f"bhashini_asr_{language}",
                capability_tier=cap.capability_tier,
                is_local=False,
                is_native=True,
                fallback_used=False,
                offline_supported=cap.offline_available,
            )

        # Fallback to Hindi ASR
        return ProviderRoutingDecision(
            task="asr",
            requested_language=language,
            requested_dialect=dialect,
            actual_tts_language="hi",
            actual_tts_dialect=None,
            selected_provider="bhashini_fallback" if mode != RuntimeMode.OFFLINE else "local_rule_fallback",
            selected_model="bhashini_asr_hi" if mode != RuntimeMode.OFFLINE else "local_conformer_hi",
            capability_tier=CapabilityTier.TRANSLATION_FALLBACK,
            is_local=(mode == RuntimeMode.OFFLINE),
            is_native=False,
            fallback_used=True,
            fallback_reason=f"NO_NATIVE_ASR_FOR_{language.upper()}_FALLING_BACK_TO_HI",
            offline_supported=True,
        )

    def route_tts(
        self,
        language: str,
        dialect: Optional[str] = None,
        mode: RuntimeMode = RuntimeMode.HYBRID
    ) -> ProviderRoutingDecision:
        """
        Route TTS request prioritizing genuine LOCAL NEURAL TTS.
        Hierarchy:
        1. Genuine local neural TTS model (if weights loaded in LocalTTSEngine)
        2. Verified remote native TTS (Bhashini API)
        3. Verified remote parent-language TTS (for dialects)
        4. Offline failure / text-only if no neural weights exist
        """
        lookup_key = dialect if dialect else language
        cap = get_voice_capability(lookup_key)

        # -------------------------------------------------------------
        # Tier 1: Check Genuine Local Neural TTS
        # -------------------------------------------------------------
        if local_tts_engine.supports_language(language) and (not dialect):
            return ProviderRoutingDecision(
                task="tts",
                requested_language=language,
                requested_dialect=dialect,
                actual_tts_language=language,
                actual_tts_dialect=dialect,
                selected_provider="local_neural_tts",
                selected_model=f"farmfusion_tts_{language}_vits_v1",
                capability_tier=CapabilityTier.NATIVE_VOICE,
                is_local=True,
                is_native=True,
                fallback_used=False,
                offline_supported=True,
            )

        # -------------------------------------------------------------
        # Tier 2: Dialect with Parent Fallback (Marwari/Mewari/Bhojpuri etc.)
        # -------------------------------------------------------------
        if dialect:
            fallback_lang = cap.fallback_language or "hi"
            if mode != RuntimeMode.OFFLINE:
                return ProviderRoutingDecision(
                    task="tts",
                    requested_language=language,
                    requested_dialect=dialect,
                    actual_tts_language=fallback_lang,
                    actual_tts_dialect=None,
                    selected_provider="bhashini",
                    selected_model=f"bhashini_tts_{fallback_lang}",
                    capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
                    is_local=False,
                    is_native=False,
                    fallback_used=True,
                    fallback_reason=f"NO_NATIVE_TTS_FOR_{dialect.upper()}_USING_PARENT_{fallback_lang.upper()}_TTS",
                    offline_supported=False,
                )
            else:
                return ProviderRoutingDecision(
                    task="tts",
                    requested_language=language,
                    requested_dialect=dialect,
                    actual_tts_language=fallback_lang,
                    actual_tts_dialect=None,
                    selected_provider="local_tts_unavailable",
                    selected_model=None,
                    capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
                    is_local=True,
                    is_native=False,
                    fallback_used=True,
                    fallback_reason=f"OFFLINE_TTS_UNAVAILABLE_FOR_{dialect.upper()}",
                    offline_supported=False,
                )

        # -------------------------------------------------------------
        # Tier 3: Verified Remote Bhashini TTS (Online / Hybrid)
        # -------------------------------------------------------------
        if cap.native_tts and mode != RuntimeMode.OFFLINE:
            return ProviderRoutingDecision(
                task="tts",
                requested_language=language,
                requested_dialect=None,
                actual_tts_language=language,
                actual_tts_dialect=None,
                selected_provider="bhashini",
                selected_model=f"bhashini_tts_{language}",
                capability_tier=CapabilityTier.NATIVE_VOICE,
                is_local=False,
                is_native=True,
                fallback_used=False,
                offline_supported=False,
            )

        # -------------------------------------------------------------
        # Tier 4: Parent-Language Fallback
        # -------------------------------------------------------------
        fallback_lang = cap.fallback_language or "hi"
        if mode != RuntimeMode.OFFLINE:
            return ProviderRoutingDecision(
                task="tts",
                requested_language=language,
                requested_dialect=dialect,
                actual_tts_language=fallback_lang,
                actual_tts_dialect=None,
                selected_provider="bhashini",
                selected_model=f"bhashini_tts_{fallback_lang}",
                capability_tier=CapabilityTier.TRANSLATION_FALLBACK,
                is_local=False,
                is_native=False,
                fallback_used=True,
                fallback_reason=f"NO_NATIVE_TTS_FOR_{lookup_key.upper()}_FALLBACK_TO_{fallback_lang.upper()}",
                offline_supported=False,
            )

        return ProviderRoutingDecision(
            task="tts",
            requested_language=language,
            requested_dialect=dialect,
            actual_tts_language=fallback_lang,
            actual_tts_dialect=None,
            selected_provider="local_tts_unavailable",
            selected_model=None,
            capability_tier=CapabilityTier.UNSUPPORTED,
            is_local=True,
            is_native=False,
            fallback_used=True,
            fallback_reason="OFFLINE_TTS_UNAVAILABLE",
            offline_supported=False,
        )


universal_voice_router = UniversalVoiceProviderRouter()
