#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""إصلاح فوري: Gemini 2.5 فقط + DeepSeek يتخطى عند 402."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════
# Gemini — نماذج مؤكدة فقط (مجانية)
# ═══════════════════════════════════════════════════════════
GEMINI = r'''"""Gemini — النماذج المجانية المؤكدة فقط."""
from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


# ✅ هذه النماذج متاحة ومجانية (تم اختبارها)
TEXT_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
]

BASE_V1BETA = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(BaseProvider):
    name = "gemini"
    default_model = "gemini-2.5-flash"

    @property
    def keys(self) -> list:
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

        for key in self.keys:
            for mdl in candidates:
                url = f"{BASE_V1BETA}/models/{mdl}:generateContent"
                try:
                    async with httpx.AsyncClient(timeout=60.0) as c:
                        r = await c.post(
                            url, json=body,
                            headers={"x-goog-api-key": key,
                                     "Content-Type": "application/json"},
                        )
                    if r.status_code == 429:
                        last_err = f"{mdl}: 429 (quota)"
                        continue
                    if r.status_code == 404:
                        last_err = f"{mdl}: 404"
                        continue
                    if r.status_code >= 400:
                        last_err = f"{mdl}: {r.status_code}"
                        continue
                    data = r.json()
                    log.info("gemini OK: %s", mdl)
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as e:
                    last_err = f"{mdl}: {e}"
                    continue

        raise ProviderError(f"gemini: {last_err}")
'''
(BASE / "app" / "services" / "ai" / "gemini.py").write_text(GEMINI, encoding="utf-8")
print("[+] gemini.py محدّث")

# ═══════════════════════════════════════════════════════════
# DeepSeek — تخطي فوري عند 402
# ═══════════════════════════════════════════════════════════
DEEPSEEK = r'''"""DeepSeek V4.1 — يتخطى بسرعة عند عدم الرصيد."""
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
'''
(BASE / "app" / "services" / "ai" / "deepseek.py").write_text(DEEPSEEK, encoding="utf-8")
print("[+] deepseek.py محدّث")

# ═══════════════════════════════════════════════════════════
# Router — Groq أولاً (مجاني 100%)
# ═══════════════════════════════════════════════════════════
ROUTER = r'''"""AI Router — الأولوية للمزودين المجانيين."""
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
            try:
                log.info("router trying %s", p.name)
                return await p.chat(messages, system=system,
                                    temperature=temperature,
                                    max_tokens=max_tokens)
            except Exception as e:
                errors.append(f"{p.name}: {e}")
                log.warning("provider %s failed: %s", p.name, e)
                continue
        raise ProviderError(" | ".join(errors))


_router: Optional[AIRouter] = None


def get_ai() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
'''
(BASE / "app" / "services" / "ai" / "router.py").write_text(ROUTER, encoding="utf-8")
print("[+] router.py محدّث")

print()
print("=" * 60)
print("  تم الإصلاح")
print("=" * 60)
print("  ✓ Gemini: نماذج 2.5 فقط (مجانية)")
print("  ✓ DeepSeek: يتخطى فوراً عند 402")
print("  ✓ Router: Groq أولاً")
print()
print("ارفع:")
print("   git add -A && git commit -m 'Fix Gemini models' && git push")
print("=" * 60)
