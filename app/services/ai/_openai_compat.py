"""OpenAI-compatible provider base."""
from typing import List, Optional
import httpx
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


class OpenAICompatProvider(BaseProvider):
    base_url: str = ""
    default_model: str = ""

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.available:
            raise ProviderError(f"{self.name}: no API key")

        payload = {
            "model": model or self.default_model,
            "messages": ([{"role": "system", "content": system}] if system else [])
                        + [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=90.0) as c:
            r = await c.post(f"{self.base_url}/chat/completions",
                             json=payload, headers=headers)
        if r.status_code >= 400:
            log.warning("%s error %s: %s", self.name, r.status_code, r.text[:200])
            raise ProviderError(f"{self.name}: {r.status_code}")
        data = r.json()
        return data["choices"][0]["message"]["content"]
