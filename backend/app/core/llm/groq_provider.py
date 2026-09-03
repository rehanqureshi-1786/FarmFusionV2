"""
Groq LLM Provider implementation for ultra-fast agricultural reasoning.
"""
import json
import re
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
import structlog
from groq import AsyncGroq
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.core.llm.base import LLMMessage, LLMProvider, LLMResponse

logger = structlog.get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class GroqLLMProvider(LLMProvider):
    """
    Groq Cloud provider providing high-speed inference on open models like Llama 3.3 70B.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.groq_api_key
        self.default_model = model or settings.groq_model or "llama-3.3-70b-versatile"
        self._client: Optional[AsyncGroq] = None
        if self.api_key:
            self._client = AsyncGroq(api_key=self.api_key)

    def is_available(self) -> bool:
        return self._client is not None

    def _build_messages(
        self, messages: List[LLMMessage], system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        formatted: List[Dict[str, str]] = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            formatted.append({"role": msg.role, "content": msg.content})
        return formatted

    async def generate(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None,
    ) -> LLMResponse:
        if not self.is_available():
            raise RuntimeError("Groq API key is not configured.")

        payload_msgs = self._build_messages(messages, system_prompt)
        kwargs: Dict[str, Any] = {
            "model": self.default_model,
            "messages": payload_msgs,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        try:
            res = await self._client.chat.completions.create(**kwargs)
            choice = res.choices[0]
            tokens_used = res.usage.total_tokens if res.usage else 0
            return LLMResponse(
                content=choice.message.content or "",
                model=self.default_model,
                tokens_used=tokens_used,
                provider="groq",
                finish_reason=choice.finish_reason,
            )
        except Exception as e:
            logger.error("groq_generation_failed", error=str(e), model=self.default_model)
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
                    "groq_structured_output_parse_retry",
                    attempt=attempt,
                    error=str(e),
                )
                augmented_system += f"\nPrevious attempt failed with error: {str(e)}. Please correct your JSON."

        raise ValueError(f"Failed to produce valid structured output for {schema.__name__} after {max_retries} retries: {last_error}")

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        if not self.is_available():
            raise RuntimeError("Groq API key is not configured.")

        payload_msgs = self._build_messages(messages, system_prompt)
        try:
            stream = await self._client.chat.completions.create(
                model=self.default_model,
                messages=payload_msgs,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("groq_stream_failed", error=str(e), model=self.default_model)
            raise
