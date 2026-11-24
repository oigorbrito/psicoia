"""Unauthenticated OpenAI-compatible chat for an Ollama server on loopback only."""
from urllib.parse import urlparse

import httpx

from .base import BackendSettings


def is_loopback_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"} and not parsed.username and not parsed.password


class OllamaLocalBackend:
    def __init__(self, settings: BackendSettings):
        if not is_loopback_url(settings.base_url):
            raise ValueError("Unauthenticated Ollama is permitted on HTTP loopback only")
        self.settings = settings

    async def chat_text(self, messages, **kwargs):
        payload = {
            "model": kwargs.get("model", self.settings.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "stream": False,
        }
        async with httpx.AsyncClient(trust_env=False, timeout=float(kwargs.get("timeout_sec", self.settings.timeout_sec))) as client:
            response = await client.post(self.settings.base_url.rstrip("/") + "/chat/completions", json=payload)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("empty model output")
        return text.strip()
