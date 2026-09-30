"""AI Router: tries providers in order."""
from typing import List, Optional
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import ChatMessage
from app.services.ai.gemini import GeminiProvider
from app.services.ai.groq import GroqProvider
from app.services.ai.openrouter import OpenRouterProvider
from app.services.ai.deepseek import DeepSeekProvider


class AIRouter:
    def __init__(self) -> None:
        self.providers = [
            GeminiProvider(settings.GEMINI_API_KEY),
            GroqProvider(settings.GROQ_API_KEY),
            OpenRouterProvider(settings.OPENROUTER_API_KEY),
            DeepSeekProvider(settings.DEEPSEEK_API_KEY),
        ]

    def status(self) -> dict:
        return {p.name: p.available for p in self.providers}

    async def chat(self, prompt: str,
                   system: Optional[str] = None,
                   history: Optional[List[ChatMessage]] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048) -> str:
        messages = list(history or []) + [ChatMessage(role="user", content=prompt)]
        errors = []
        for p in self.providers:
            if not p.available:
                continue
            try:
                log.info("AI router trying %s", p.name)
                return await p.chat(messages, system=system,
                                    temperature=temperature,
                                    max_tokens=max_tokens)
            except Exception as e:
                errors.append(f"{p.name}: {e}")
                continue
        raise ProviderError("All providers failed: " + " | ".join(errors))


_router: Optional[AIRouter] = None


def get_ai() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
