import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class OpenAIService:
    """Async OpenAI service with real API calls and safe fallback behavior."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.max_tokens = int(os.environ.get("OPENAI_MAX_TOKENS", "2048"))
        self.temperature = float(os.environ.get("OPENAI_TEMPERATURE", "0.7"))

    @staticmethod
    def _safe_json_loads(raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON returned by OpenAI: {exc}") from exc

    @staticmethod
    def _format_context(context: Dict[str, Any]) -> str:
        if not context:
            return "No additional context supplied."
        return json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True)

    @retry(
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _create_completion(self, **kwargs: Any) -> Any:
        if self.client is None:
            raise RuntimeError("OpenAI client is not configured.")
        return await self.client.chat.completions.create(**kwargs)

    def _fallback_response(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "data": {
                "analysis": (
                    "OpenAI API is not configured or unavailable. The builder entered a local fallback "
                    "execution mode and preserved the real request state for later verification."
                ),
                "recommendations": [
                    "Configure OPENAI_API_KEY for full model-backed execution.",
                    "Provide task context to improve generated analysis quality.",
                    "Verify downstream tool execution through evidence-based logging.",
                ],
                "next_steps": [
                    "Set OPENAI_API_KEY in the environment.",
                    "Retry the builder request with repository context and human approval.",
                    "Inspect memory/events.jsonl for execution evidence.",
                ],
                "confidence": 0.0,
                "prompt": prompt,
                "context": context,
            },
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": self.model,
            "fallback": True,
        }

    async def generate_builder_response(
        self,
        prompt: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary.")

        if not self.api_key or self.client is None:
            logger.warning("OPENAI_API_KEY missing; using safe fallback response.")
            return self._fallback_response(prompt, context)

        system_prompt = (
            "You are AP1 Auto AI Builder. Return valid JSON only. "
            "Use real state, evidence, and human-intent-first reasoning. "
            "Do not claim actions you cannot verify. "
            "Respond with keys: analysis, recommendations, next_steps, confidence."
        )

        user_content = f"""
Task:
{prompt}

Context:
{self._format_context(context)}
"""

        try:
            response = await self._create_completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                return self._fallback_response(prompt, context)

            payload = self._safe_json_loads(content)
            normalized_payload = {
                "analysis": payload.get("analysis", ""),
                "recommendations": payload.get("recommendations", []),
                "next_steps": payload.get("next_steps", []),
                "confidence": payload.get("confidence", 0.0),
            }

            return {
                "success": True,
                "data": normalized_payload,
                "usage": {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": self.model,
                "fallback": False,
            }

        except (RateLimitError, APIConnectionError) as exc:
            logger.warning("Transient OpenAI error after retries: %s", exc)
            return self._fallback_response(prompt, context)

        except APIStatusError as exc:
            logger.warning("OpenAI API status error: %s", exc)
            return self._fallback_response(prompt, context)

        except Exception:
            logger.exception("Unexpected error generating builder response")
            return self._fallback_response(prompt, context)

    async def stream_builder_execution(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")

        context = context or {}

        if not self.api_key or self.client is None:
            fallback_lines = [
                "[builder] OpenAI API unavailable. Switching to safe fallback mode.",
                "[builder] Capturing real request state for evidence-based follow-up.",
                f"[builder] Task: {prompt}",
                "[builder] Completion: fallback response generated locally.",
            ]
            for line in fallback_lines:
                yield line + "\n"
                await asyncio.sleep(0.01)
            return

        system_prompt = (
            "You are AP1 Auto AI Builder. Stream execution logs in real time with "
            "clear evidence-based status updates. Do not simulate state. "
            "Provide concise, structured output suitable for terminal streaming."
        )

        user_content = f"""
Task:
{prompt}

Context:
{self._format_context(context)}
"""

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta
                    await asyncio.sleep(0.01)

        except (RateLimitError, APIConnectionError) as exc:
            logger.warning("Transient OpenAI streaming error: %s", exc)
            yield f"[builder] OpenAI streaming error: {exc}\n"
        except APIStatusError as exc:
            logger.warning("OpenAI streaming status error: %s", exc)
            yield f"[builder] OpenAI status error: {exc}\n"
        except Exception as exc:
            logger.exception("Unexpected streaming error")
            yield f"[builder] Streaming failed: {exc}\n"


openai_service = OpenAIService()
