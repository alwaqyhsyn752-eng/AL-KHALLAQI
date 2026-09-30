#!/usr/bin/env python3
from pathlib import Path
BASE = Path(__file__).resolve().parent

ROUTER = r'''"""AI Router — يتخطى المزودين الفاشلين بسرعة + caching للأخطاء."""
import time
from typing import List, Optional, Dict
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import ChatMessage
from app.services.ai.gemini import GeminiProvider
from app.services.ai.groq import GroqProvider
from app.services.ai.openrouter import OpenRouterProvider
from app.services.ai.deepseek import DeepSeekProvider


# cache: يخزّن وقت آخر فشل لكل مزود (لتخطيه لمدة 60 ثانية)
_FAILED: Dict[str, float] = {}
_SKIP_SECONDS = 60


def _is_skipped(name: str) -> bool:
    ts = _FAILED.get(name)
    if not ts:
        return False
    if time.time() - ts > _SKIP_SECONDS:
        _FAILED.pop(name, None)
        return False
    return True


def _mark_failed(name: str) -> None:
    _FAILED[name] = time.time()


class AIRouter:
    def __init__(self) -> None:
        self.providers = [
            GroqProvider(settings.GROQ_API_KEY),
            GeminiProvider(settings.GEMINI_API_KEY),
            OpenRouterProvider(settings.OPENROUTER_API_KEY),
            DeepSeekProvider(
                settings.DEEPSEEK_API_KEY,
                thinking=getattr(settings, "DEEPSEEK_THINKING", "enabled"),
                reasoning_effort=getattr(settings, "DEEPSEEK_REASONING_EFFORT", "high"),
            ),
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
            if _is_skipped(p.name):
                log.info("router skip %s (recent failure)", p.name)
                errors.append(f"{p.name}: skipped")
                continue
            try:
                log.info("router trying %s", p.name)
                result = await p.chat(messages, system=system,
                                      temperature=temperature,
                                      max_tokens=max_tokens)
                # نجح — احذف من قائمة الفشل
                _FAILED.pop(p.name, None)
                return result
            except Exception as e:
                errors.append(f"{p.name}: {e}")
                log.warning("provider %s failed: %s", p.name, e)
                _mark_failed(p.name)
                continue

        raise ProviderError("كل المزودين فشلوا: " + " | ".join(errors))


_router: Optional[AIRouter] = None


def get_ai() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
'''
(BASE / "app" / "services" / "ai" / "router.py").write_text(ROUTER, encoding="utf-8")
print("[+] router.py محدّث — يتخطى الفاشلين بسرعة")
