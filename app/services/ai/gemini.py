"""Gemini provider — Interactions API (2026) + legacy fallback."""
from typing import List, Optional
import httpx

from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


TEXT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
]

IMAGE_MODELS = [
    "gemini-3.1-flash-image",
    "gemini-3-pro-image",
    "gemini-3.1-flash-lite-image",
    "gemini-2.5-flash-image",
]

BASE_V1BETA = "https://generativelanguage.googleapis.com/v1beta"
INTERACTIONS_URL = f"{BASE_V1BETA}/interactions"


class GeminiProvider(BaseProvider):
    name = "gemini"
    default_model = "gemini-3.8-flash"

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.available:
            raise ProviderError("gemini: no API key")

        # حاول Interactions API أولاً
        try:
            text = await self._interactions_chat(
                messages, system, temperature, max_tokens, model)
            if text:
                return text
        except Exception as e:
            log.info("interactions failed, fallback: %s", e)

        # fallback: generateContent
        return await self._generate_content(
            messages, system, temperature, max_tokens, model)

    async def _interactions_chat(self, messages, system, temperature,
                                 max_tokens, model):
        parts = []
        for m in messages:
            parts.append(f"{m.role}: {m.content}")
        prompt = "\n".join(parts)

        payload = {
            "model": model or self.default_model,
            "input": prompt,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        candidates = [model] if model else TEXT_MODELS
        last_err = None

        for mdl in candidates:
            body = dict(payload)
            body["model"] = mdl
            try:
                async with httpx.AsyncClient(timeout=90.0) as c:
                    r = await c.post(
                        INTERACTIONS_URL, json=body,
                        headers={"x-goog-api-key": self.api_key,
                                 "Content-Type": "application/json"},
                    )
                if r.status_code == 404:
                    last_err = f"{mdl}: 404"
                    continue
                if r.status_code >= 400:
                    last_err = f"{mdl}: {r.status_code}"
                    continue
                data = r.json()
                text = self._extract_interaction_text(data)
                if text:
                    log.info("gemini interactions OK: %s", mdl)
                    return text
            except Exception as e:
                last_err = f"{mdl}: {e}"
                continue

        raise ProviderError(f"gemini interactions: {last_err}")

    @staticmethod
    def _extract_interaction_text(data: dict) -> str:
        if isinstance(data.get("output_text"), str):
            return data["output_text"]
        steps = data.get("steps") or []
        chunks = []
        for s in steps:
            if s.get("type") in ("text", "content"):
                txt = s.get("text") or (s.get("content") or {}).get("text")
                if txt:
                    chunks.append(txt)
        return "\n".join(chunks)

    async def _generate_content(self, messages, system, temperature,
                                max_tokens, model):
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

        candidates = [model] if model else TEXT_MODELS
        last_err = None

        for mdl in candidates:
            url = f"{BASE_V1BETA}/models/{mdl}:generateContent"
            try:
                async with httpx.AsyncClient(timeout=90.0) as c:
                    r = await c.post(
                        url, json=body,
                        headers={"x-goog-api-key": self.api_key,
                                 "Content-Type": "application/json"},
                    )
                if r.status_code == 404:
                    last_err = f"{mdl}: 404"
                    continue
                if r.status_code >= 400:
                    last_err = f"{mdl}: {r.status_code}"
                    continue
                data = r.json()
                log.info("gemini generateContent OK: %s", mdl)
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                last_err = f"{mdl}: {e}"
                continue

        raise ProviderError(f"gemini generateContent: {last_err}")
