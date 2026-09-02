"""
Centralized Language Context & Resolution for FarmFusion Backend.
Maintains request-scoped language state, resolves dialects to parent languages,
and validates against the canonical 38-language LANGUAGE_REGISTRY.
"""

from contextvars import ContextVar
from typing import Optional, Dict, Any
from fastapi import Request
from pydantic import BaseModel
import structlog
from app.voice.languages import LANGUAGE_REGISTRY, LanguageProfile, get_language_profile

logger = structlog.get_logger(__name__)

# Request-scoped language context variable
_request_language_context: ContextVar[str] = ContextVar("request_language_context", default="hi")
_request_dialect_context: ContextVar[Optional[str]] = ContextVar("request_dialect_context", default=None)

class LanguageContext(BaseModel):
    requested_code: str
    canonical_code: str
    language_name: str
    native_name: str
    is_dialect: bool = False
    dialect_name: Optional[str] = None
    parent_language: Optional[str] = None
    support_tier: int = 1
    native_tts: bool = True
    fallback_language: str = "hi"

def resolve_language_code(code: Optional[str]) -> LanguageContext:
    """
    Resolves any input language or dialect code to a validated LanguageContext.
    Falls back deterministically to Hindi ('hi') or English ('en') if unknown.
    """
    if not code or not code.strip():
        profile = LANGUAGE_REGISTRY.get("hi", LANGUAGE_REGISTRY["hi"])
        return LanguageContext(
            requested_code="hi",
            canonical_code="hi",
            language_name=profile.name,
            native_name=profile.native_name,
            is_dialect=False,
            support_tier=profile.support_tier,
            native_tts=profile.tts.native_supported,
            fallback_language=profile.fallback_language
        )

    clean_code = code.strip().lower().split(",")[0].split(";")[0].strip()
    
    # Check if standard locale string like 'hi-IN' or 'gu_IN'
    if "-" in clean_code:
        clean_code = clean_code.split("-")[0]
    elif "_" in clean_code:
        clean_code = clean_code.split("_")[0]

    # Direct match in 38-language registry
    if clean_code in LANGUAGE_REGISTRY:
        profile = LANGUAGE_REGISTRY[clean_code]
        if profile.is_dialect:
            parent_code = profile.fallback_language or "hi"
            return LanguageContext(
                requested_code=clean_code,
                canonical_code=parent_code,
                language_name=profile.name,
                native_name=profile.native_name,
                is_dialect=True,
                dialect_name=profile.name,
                parent_language=parent_code,
                support_tier=profile.support_tier,
                native_tts=profile.tts.native_supported,
                fallback_language=profile.fallback_language
            )
        else:
            return LanguageContext(
                requested_code=clean_code,
                canonical_code=profile.canonical_code,
                language_name=profile.name,
                native_name=profile.native_name,
                is_dialect=False,
                support_tier=profile.support_tier,
                native_tts=profile.tts.native_supported,
                fallback_language=profile.fallback_language
            )

    # Fallback to Hindi
    hi_prof = LANGUAGE_REGISTRY.get("hi")
    return LanguageContext(
        requested_code=clean_code,
        canonical_code="hi",
        language_name=hi_prof.name if hi_prof else "Hindi",
        native_name=hi_prof.native_name if hi_prof else "हिन्दी",
        is_dialect=False,
        support_tier=1,
        native_tts=True,
        fallback_language="hi"
    )

def set_current_language(code: str, dialect: Optional[str] = None):
    """Sets contextvar for the current async task/request."""
    _request_language_context.set(code)
    _request_dialect_context.set(dialect)

def get_current_language() -> str:
    """Returns the canonical language code for the current request (defaults to 'hi')."""
    return _request_language_context.get()

def get_current_dialect() -> Optional[str]:
    """Returns the dialect name if the current request is for a regional dialect."""
    return _request_dialect_context.get()

async def get_language_context(request: Request) -> LanguageContext:
    """
    FastAPI dependency to extract and resolve language context from request headers, query params, or defaults.
    """
    # 1. Check custom header X-User-Language
    user_lang = request.headers.get("x-user-language") or request.headers.get("X-User-Language")
    
    # 2. Check standard Accept-Language header
    if not user_lang:
        user_lang = request.headers.get("accept-language") or request.headers.get("Accept-Language")

    # 3. Check query param 'language' or 'preferred_language'
    if not user_lang:
        user_lang = request.query_params.get("language") or request.query_params.get("preferred_language")

    ctx = resolve_language_code(user_lang)
    set_current_language(ctx.canonical_code, ctx.dialect_name if ctx.is_dialect else None)
    return ctx
