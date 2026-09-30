"""Gemini provider with fallback models."""
from typing import List, Optional
import httpx
from app.core.exceptions import ProviderError
from app.services.ai.base import BaseProvider, ChatMessage


MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]


class GeminiProvider(BaseProvider):
    name = "gemini"
    default_model = "gemini-2.0-flash"
    base = "https://generativelanguage.googleapis.com/v1beta"

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.available:
            raise ProviderError("gemini: no API key")

        contents = []
        for m in messages:
            role = "user" if m.role in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        last_err = None
        for mdl in ([model] if model else MODELS):
            url = f"{self.base}/models/{mdl}:generateContent?key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=90.0) as c:
                    r = await c.post(url, json=body)
                if r.status_code >= 400:
                    last_err = f"{mdl}: {r.status_code}"
                    continue
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                last_err = f"{mdl}: {e}"
                continue
        raise ProviderError(f"gemini failed: {last_err}")
