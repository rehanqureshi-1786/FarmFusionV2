"""
OpenRouter LLM Provider implementation for FarmFusion general reasoning layer.
Utilizes OpenRouter's OpenAI-compatible API with openrouter/free model routing.
"""
import json
import re
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
import httpx
import structlog
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.core.llm.base import LLMMessage, LLMProvider, LLMResponse

logger = structlog.get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenRouterLLMProvider(LLMProvider):
    """
    OpenRouter Cloud provider routing to open models (default: openrouter/free).
    Enforces strict structured schema output and resilience.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 12.0,
    ):
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.openrouter_api_key
        self.default_model = model or settings.openrouter_model or "openrouter/free"
        self.base_url = (base_url or settings.openrouter_base_url or "https://openrouter.ai/api/v1").rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("placeholder"))

    def _build_messages(
        self, messages: List[LLMMessage], system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        formatted: List[Dict[str, str]] = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            formatted.append({"role": msg.role, "content": msg.content})
        return formatted

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError("OpenRouter API key is not configured.")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://farmfusion.app",
            "X-Title": "FarmFusion",
        }

    async def generate(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None,
    ) -> LLMResponse:
        if not self.is_available():
            raise RuntimeError("OpenRouter API key is not configured or is a placeholder.")

        payload_msgs = self._build_messages(messages, system_prompt)
        kwargs: Dict[str, Any] = {
            "model": self.default_model,
            "messages": payload_msgs,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        endpoint = f"{self.base_url}/chat/completions"
        headers = self._get_headers()

        import asyncio

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(endpoint, headers=headers, json=kwargs)
                    
                    if res.status_code == 200:
                        data = res.json()
                        choice = data["choices"][0]
                        content = choice["message"]["content"] or ""
                        model_used = data.get("model", self.default_model)
                        usage = data.get("usage", {})
                        tokens_used = usage.get("total_tokens", 0)
                        finish_reason = choice.get("finish_reason")
                        return LLMResponse(
                            content=content,
                            model=model_used,
                            tokens_used=tokens_used,
                            provider="openrouter",
                            finish_reason=finish_reason,
                        )
                    elif res.status_code in (401, 403):
                        logger.error("openrouter_auth_failed", status=res.status_code)
                        raise RuntimeError(f"OpenRouter authentication failed with status {res.status_code}")
                    elif res.status_code == 429:
                        if attempt == 0:
                            logger.warning("openrouter_rate_limited_retrying", attempt=attempt)
                            await asyncio.sleep(2.5)
                            continue
                        logger.warning("openrouter_rate_limited", status=429)
                        raise RuntimeError("OpenRouter rate limit reached (HTTP 429)")
                    else:
                        logger.error("openrouter_http_error", status=res.status_code, body=res.text[:200])
                        raise RuntimeError(f"OpenRouter HTTP error {res.status_code}: {res.text[:200]}")
            except httpx.TimeoutException as e:
                logger.warning("openrouter_timeout", timeout_seconds=self.timeout)
                raise TimeoutError(f"OpenRouter request timed out after {self.timeout}s") from e
            except Exception as e:
                if not isinstance(e, (RuntimeError, TimeoutError)):
                    logger.error("openrouter_generation_failed", error=str(e), model=self.default_model)
                raise

    async def generate_structured(
        self,
        schema: Type[T],
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 2,
    ) -> T:
        """
        Generates structured JSON and parses it strictly into the target Pydantic model.
        Retries on JSON or validation errors.
        """
        json_instruction = (
            f"\n\nYou MUST respond ONLY with a single valid JSON object strictly matching this schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}\n"
            f"Do NOT include any markdown code blocks, backticks, or text outside the JSON object."
        )
        augmented_system = (system_prompt or "") + json_instruction

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = await self.generate(
                    messages=messages,
                    system_prompt=augmented_system,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                raw_text = response.content.strip()
                # Clean any lingering markdown fences if model included them
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                parsed_dict = json.loads(raw_text)
                return schema.model_validate(parsed_dict)
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                logger.warning(
                    "openrouter_structured_output_parse_retry",
                    attempt=attempt,
                    error=str(e),
                )
                augmented_system += f"\nPrevious attempt failed with error: {str(e)}. Please return ONLY valid JSON matching the schema."

        raise ValueError(
            f"Failed to produce valid structured output for {schema.__name__} after {max_retries} retries: {last_error}"
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        if not self.is_available():
            raise RuntimeError("OpenRouter API key is not configured.")

        payload_msgs = self._build_messages(messages, system_prompt)
        payload = {
            "model": self.default_model,
            "messages": payload_msgs,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        endpoint = f"{self.base_url}/chat/completions"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        raise RuntimeError(f"OpenRouter streaming HTTP error: {response.status_code}")
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or line.startswith(":"):
                            continue
                        if line == "data: [DONE]":
                            break
                        if line.startswith("data: "):
                            data_str = line[6:]
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error("openrouter_stream_failed", error=str(e), model=self.default_model)
            raise
