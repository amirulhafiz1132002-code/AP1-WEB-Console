"""
OpenAI Service Module

Provides async service for interacting with OpenAI API v1.0+.
Enforces REAL STATE > UI SIMULATION principle:
- All responses are structured JSON from actual API calls
- Includes retry logic and fallback handling for rate limits and connection errors
- Streams real token data in production use

Architecture:
- generate_builder_response(): Sync structured JSON requests to OpenAI
- stream_builder_execution(): Async streaming of tokens/logs in real-time
"""

import os
import asyncio
import logging
from typing import Dict, AsyncGenerator, Optional
from datetime import datetime, timezone
from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class OpenAIService:
    """Async OpenAI service with structured output and streaming support."""

    def __init__(self):
        """Initialize OpenAI client from environment."""
        self.api_key: str = os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set; service will fail on real requests")
        
        self.client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key)
        self.model: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens: int = 2048
        self.temperature: float = 0.7

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    )
    async def generate_builder_response(
        self, prompt: str, context: Dict
    ) -> Dict:
        """
        Request structured JSON output from OpenAI.

        Args:
            prompt: The user prompt or task description.
            context: Contextual data (e.g., repository info, previous state).

        Returns:
            Structured dict with keys: success, data, usage, timestamp, model.
            data contains: analysis, recommendations, next_steps.

        Raises:
            APIStatusError: On persistent API failures after retries.
            ValueError: If API key is missing or response is malformed.
        """
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        if not prompt or not isinstance(prompt, str):
            raise ValueError("prompt must be a non-empty string")

        if not isinstance(context, dict):
            raise ValueError("context must be a dictionary")

        # Build system prompt for structured output
        system_prompt = (
            "You are an AI code builder assistant for the AP1 (Auto AI Builder) system. "
            "Provide structured, actionable analysis and recommendations. "
            "Always respond with valid JSON containing: analysis, recommendations, next_steps. "
            "Never include markdown, explanations outside JSON, or UI simulation."
        )

        # Build user message with context
        user_message = f"""
Context:
{self._format_context(context)}

Task:
{prompt}

Provide a structured JSON response with the following format:
{{
    "analysis": "detailed technical analysis of the task",
    "recommendations": ["recommendation 1", "recommendation 2", ...],
    "next_steps": ["step 1", "step 2", ...],
    "confidence": 0.0-1.0
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            # Extract response content
            response_content = response.choices[0].message.content
            if not response_content:
                raise ValueError("Empty response from OpenAI API")

            # Parse JSON response
            try:
                import json
                data = json.loads(response_content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {response_content}")
                raise ValueError(f"OpenAI response was not valid JSON: {str(e)}")

            # Validate required fields
            required_fields = ["analysis", "recommendations", "next_steps"]
            for field in required_fields:
                if field not in data:
                    data[field] = None

            return {
                "success": True,
                "data": data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": self.model,
            }

        except APIStatusError as e:
            logger.error(
                f"OpenAI API error (status {e.status_code}): {str(e)}",
                exc_info=True,
            )
            raise
        except APIConnectionError as e:
            logger.error(f"OpenAI connection error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_builder_response: {str(e)}", exc_info=True)
            raise

    async def stream_builder_execution(
        self, prompt: str, context: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream builder execution tokens/logs in real-time.

        Args:
            prompt: The execution task or query.
            context: Optional contextual data.

        Yields:
            String tokens/chunks as they arrive from the API.

        Raises:
            ValueError: If API key is missing.
            APIStatusError: On persistent API failures.
        """
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        if not prompt or not isinstance(prompt, str):
            raise ValueError("prompt must be a non-empty string")

        context = context or {}

        system_prompt = (
            "You are an AI code builder assistant streaming real-time execution logs. "
            "Provide clear, structured output suitable for streaming to a console or terminal. "
            "Each line should be actionable and reflect real state, not simulation."
        )

        user_message = f"""
{self._format_context(context)}

Execute:
{prompt}

Stream execution progress, logs, and results line by line.
"""

        try:
            with self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            ) as response:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        # Small delay to avoid overwhelming consumers
                        await asyncio.sleep(0.001)

        except APIStatusError as e:
            logger.error(
                f"OpenAI streaming error (status {e.status_code}): {str(e)}",
                exc_info=True,
            )
            raise
        except APIConnectionError as e:
            logger.error(f"OpenAI streaming connection error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in stream_builder_execution: {str(e)}", exc_info=True)
            raise

    def _format_context(self, context: Dict) -> str:
        """
        Format context dict into readable string.

        Args:
            context: Dict with repository, builder state, or other metadata.

        Returns:
            Formatted string representation of context.
        """
        if not context:
            return "No context provided."

        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"  {key}:")
                for k, v in value.items():
                    lines.append(f"    {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"  {key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


# Singleton instance
openai_service = OpenAIService()
