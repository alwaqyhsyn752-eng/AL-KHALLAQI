"""DeepSeek provider — V4.1-Flash (2026) + thinking mode."""
from typing import List, Optional, Dict, Any
import httpx

from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


BASE_URL = "https://api.deepseek.com"

# ⚠️ deepseek-flash (V4.1) أولاً — لا تحذفه
MODELS = [
    "deepseek-flash",                 # V4.1-Flash (الأحدث)
    "deepseek-v4-pro",                # Pro
    "deepseek-v4-flash",              # اسم قديم → يوجَّه تلقائياً
    "deepseek-v4-flash-vision-exp",   # Vision
]


class DeepSeekProvider(BaseProvider):
    name = "deepseek"
    default_model = "deepseek-flash"
    base_url = BASE_URL

    def __init__(self, api_key: str = "",
                 thinking: str = "enabled",
                 reasoning_effort: str = "high") -> None:
        super().__init__(api_key)
        self.thinking = thinking
        self.reasoning_effort = reasoning_effort

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.available:
            raise ProviderError("deepseek: no API key")

        payload_messages: List[Dict[str, Any]] = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        for m in messages:
            payload_messages.append({"role": m.role, "content": m.content})

        body: Dict[str, Any] = {
            "model": model or self.default_model,
            "messages": payload_messages,
            "max_tokens": max_tokens,
            "stream": False,
        }

        if self.thinking == "enabled":
            body["thinking"] = {"type": "enabled"}
            body["reasoning_effort"] = self.reasoning_effort
        else:
            body["thinking"] = {"type": "disabled"}
            body["temperature"] = temperature
            body["top_p"] = 0.95

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_err = None
        candidates = [model] if model else MODELS

        for mdl in candidates:
            body["model"] = mdl
            try:
                async with httpx.AsyncClient(timeout=120.0) as c:
                    r = await c.post(f"{BASE_URL}/chat/completions",
                                     json=body, headers=headers)
                if r.status_code == 402:
                    last_err = f"{mdl}: 402 (رصيد غير كافٍ)"
                    continue
                if r.status_code == 404:
                    last_err = f"{mdl}: 404"
                    continue
                if r.status_code >= 400:
                    last_err = f"{mdl}: {r.status_code}"
                    continue
                data = r.json()
                choice = data["choices"][0]["message"]
                content = choice.get("content") or ""
                reasoning = choice.get("reasoning_content") or ""
                if reasoning:
                    log.info("deepseek thinking: %s...",
                             reasoning[:80].replace("\n", " "))
                log.info("deepseek OK: %s", mdl)
                return content
            except Exception as e:
                last_err = f"{mdl}: {e}"
                continue

        raise ProviderError(f"deepseek: {last_err}")
