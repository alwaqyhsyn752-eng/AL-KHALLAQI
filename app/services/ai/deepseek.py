"""DeepSeek V4.1 — يتخطى بسرعة عند عدم الرصيد."""
from typing import List, Optional, Dict, Any
import httpx
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


BASE_URL = "https://api.deepseek.com"

MODELS = [
    "deepseek-flash",
    "deepseek-v4-pro",
]


class DeepSeekProvider(BaseProvider):
    name = "deepseek"
    default_model = "deepseek-flash"

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
            raise ProviderError("deepseek: no key")

        payload_messages = []
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # جرّب النموذج الأول فقط (لا حاجة للتكرار عند 402)
        mdl = body["model"]
        try:
            async with httpx.AsyncClient(timeout=60.0) as c:
                r = await c.post(f"{BASE_URL}/chat/completions",
                                 json=body, headers=headers)
            if r.status_code == 402:
                raise ProviderError("deepseek: 402 (no credit)")
            if r.status_code >= 400:
                raise ProviderError(f"deepseek: {r.status_code}")
            data = r.json()
            return data["choices"][0]["message"].get("content", "")
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"deepseek: {e}")
