#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AL-KHALLAQI — ترقية شاملة: Gemini 3.x + DeepSeek V4.1 + Router + Config."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

def w(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"[+] {rel}")

# ═════════════════════════════════════════════════════════════
# 1) Gemini 3.x — Interactions API + legacy fallback
# ═════════════════════════════════════════════════════════════
w("app/services/ai/gemini.py", r'''"""Gemini provider — Interactions API (2026) + legacy fallback."""
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
''')

# ═════════════════════════════════════════════════════════════
# 2) DeepSeek V4.1 + thinking mode
# ═════════════════════════════════════════════════════════════
w("app/services/ai/deepseek.py", r'''"""DeepSeek provider — V4.1-Flash (2026) + thinking mode + reasoning_content."""
from typing import List, Optional, Dict, Any
import httpx

from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


BASE_URL = "https://api.deepseek.com"

MODELS = [
    "deepseek-flash",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "deepseek-v4-flash-vision-exp",
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
''')

# ═════════════════════════════════════════════════════════════
# 3) Config — إضافة متغيرات جديدة
# ═════════════════════════════════════════════════════════════
cfg_path = BASE / "app" / "core" / "config.py"
src = cfg_path.read_text(encoding="utf-8")

if "GEMINI_MODEL" not in src:
    src = src.replace(
        'GEMINI_API_KEY: str = ""',
        'GEMINI_API_KEY: str = ""\n'
        '    GEMINI_MODEL: str = "gemini-3.8-flash"'
    )

if "DEEPSEEK_MODEL" not in src:
    src = src.replace(
        'DEEPSEEK_API_KEY: str = ""',
        'DEEPSEEK_API_KEY: str = ""\n'
        '    DEEPSEEK_MODEL: str = "deepseek-flash"\n'
        '    DEEPSEEK_THINKING: str = "enabled"\n'
        '    DEEPSEEK_REASONING_EFFORT: str = "high"'
    )

cfg_path.write_text(src, encoding="utf-8")
print("[+] app/core/config.py")

# ═════════════════════════════════════════════════════════════
# 4) Router — يمرّر الخيارات الجديدة + إعادة الترتيب
# ═════════════════════════════════════════════════════════════
w("app/services/ai/router.py", r'''"""AI Router — ترتيب حسب الأولوية المجانية."""
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
''')

print()
print("=" * 60)
print("  ✦ اكتمل التحديث الشامل")
print("=" * 60)
print()
print("ما تم تحديثه:")
print("  1. Gemini  → 3.8-flash + Interactions API")
print("  2. DeepSeek → V4.1-Flash + thinking mode")
print("  3. Config  → متغيرات جديدة")
print("  4. Router  → ترتيب مجاني أولاً")
print()
print("ارفع الآن:")
print("   git add -A")
print('   git commit -m "Upgrade: Gemini 3.x + DeepSeek V4.1"')
print("   git push origin main")
print("=" * 60)
