"""Gemini — مجاني مع مفتاح احتياطي + نماذج متعددة."""
from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


# أحدث النماذج المجانية (من Google AI Studio)
TEXT_MODELS = [
    "gemini-2.5-flash",              # مجاني، سريع
    "gemini-2.5-pro",                # مجاني بحصة أعلى
    "gemini-2.0-flash",              # مجاني مستقر
    "gemini-2.0-flash-exp",          # تجريبي
    "gemini-1.5-flash-latest",       # احتياطي
    "gemini-1.5-pro-latest",         # احتياطي
]

BASE_V1BETA = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(BaseProvider):
    name = "gemini"
    default_model = "gemini-2.5-flash"

    @property
    def keys(self) -> list:
        """قائمة المفاتيح — يدعم مفتاحين للتبديل عند نفاد الحصة."""
        keys = []
        k1 = getattr(settings, "GEMINI_API_KEY", "")
        k2 = getattr(settings, "GEMINI_API_KEY_FALLBACK", "")
        if k1: keys.append(k1)
        if k2: keys.append(k2)
        return keys

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.keys:
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

        candidates = [model] if model else TEXT_MODELS
        last_err = None

        # جرّب كل مفتاح × كل نموذج
        for key in self.keys:
            for mdl in candidates:
                url = f"{BASE_V1BETA}/models/{mdl}:generateContent"
                try:
                    async with httpx.AsyncClient(timeout=90.0) as c:
                        r = await c.post(
                            url, json=body,
                            headers={"x-goog-api-key": key,
                                     "Content-Type": "application/json"},
                        )
                    if r.status_code == 429:
                        last_err = f"{mdl}: 429 (quota)"
                        continue  # جرّب المفتاح/النموذج التالي
                    if r.status_code == 404:
                        last_err = f"{mdl}: 404"
                        continue
                    if r.status_code >= 400:
                        last_err = f"{mdl}: {r.status_code}"
                        continue
                    data = r.json()
                    log.info("gemini OK: %s (key %s...)", mdl, key[:6])
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as e:
                    last_err = f"{mdl}: {e}"
                    continue

        raise ProviderError(f"gemini: {last_err}")
