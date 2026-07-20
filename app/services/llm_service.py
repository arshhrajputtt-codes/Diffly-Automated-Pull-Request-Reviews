import json

import httpx

from app.core.config import settings
from app.core.exceptions import ProviderError

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class LLMService:
    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.LLM_PROVIDER

    def complete(self, system_prompt: str, user_prompt: str) -> dict:
        """Returns {"content": str, "input_tokens": int, "output_tokens": int, "model": str}."""
        if self.provider == "ollama":
            return self._complete_ollama(system_prompt, user_prompt)
        return self._complete_anthropic(system_prompt, user_prompt)

    def _complete_ollama(self, system_prompt: str, user_prompt: str) -> dict:
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        try:
            response = httpx.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload, timeout=180.0
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderError("ollama", exc.response.text) from exc
        except httpx.RequestError as exc:
            raise ProviderError("ollama", f"{exc} (is Ollama running?)") from exc

        data = response.json()
        return {
            "content": data.get("message", {}).get("content", ""),
            "input_tokens": data.get("prompt_eval_count", 0),
            "output_tokens": data.get("eval_count", 0),
            "model": settings.OLLAMA_MODEL,
        }

    def _complete_anthropic(self, system_prompt: str, user_prompt: str) -> dict:
        if not settings.ANTHROPIC_API_KEY:
            raise ProviderError("anthropic", "ANTHROPIC_API_KEY is not configured")

        payload = {
            "model": settings.ANTHROPIC_MODEL,
            "max_tokens": 1500,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        try:
            response = httpx.post(ANTHROPIC_MESSAGES_URL, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderError("anthropic", exc.response.text) from exc
        except httpx.RequestError as exc:
            raise ProviderError("anthropic", str(exc)) from exc

        data = response.json()
        content = "".join(block.get("text", "") for block in data.get("content", []))
        usage = data.get("usage", {})
        return {
            "content": content,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "model": settings.ANTHROPIC_MODEL,
        }
