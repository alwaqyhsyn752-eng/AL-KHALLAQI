#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تحديث قائمة نماذج Gemini — يشمل الأسماء المطلوبة + الأسماء المؤكدة."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

NEW_GEMINI = r'''"""Gemini provider with extended model fallback list.

ملاحظة: بعض الأسماء التالية قد لا تكون متاحة في API العام،
لذا يحاول الكود كل واحد بالترتيب حتى يجد ما يعمل.
"""
from typing import List, Optional
import httpx
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


# ─── قائمة النماذج بالترتيب: الأحدث → الأقدم ───────────────
# الكود يحاول كل اسم حتى ينجح أحدها.
MODELS = [
    # الأسماء المطلوبة (قد تعمل مستقبلاً)
    "gemini-4-argon",
    "gemini-3.8-flash",
    "gemini-3.8-live",
    "gemini-3.8-flash-extended-thinking",

    # الأسماء المؤكدة (2025)
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-preview-09-2025",
    "gemini-2.5-flash-thinking",

    # نماذج 2.0
    "gemini-2.0-flash",
    "gemini-2.0-flash-thinking-exp",
    "gemini-2.0-flash-exp",

    # نماذج 1.5 (احتياطي)
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
]


class GeminiProvider(BaseProvider):
    name = "gemini"
    default_model = "gemini-2.5-flash"
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

        candidates = [model] if model else MODELS
        last_err = None

        for mdl in candidates:
            url = f"{self.base}/models/{mdl}:generateContent?key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=90.0) as c:
                    r = await c.post(url, json=body)
                if r.status_code == 404:
                    log.info("gemini model not found: %s", mdl)
                    last_err = f"{mdl}: 404"
                    continue
                if r.status_code == 429:
                    log.warning("gemini quota exceeded: %s", mdl)
                    last_err = f"{mdl}: 429 (quota)"
                    continue
                if r.status_code >= 400:
                    last_err = f"{mdl}: {r.status_code}"
                    continue
                data = r.json()
                log.info("gemini success with model: %s", mdl)
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                last_err = f"{mdl}: {e}"
                continue

        raise ProviderError(f"gemini: all models failed ({last_err})")
'''

path = BASE / "app" / "services" / "ai" / "gemini.py"
path.write_text(NEW_GEMINI, encoding="utf-8")
print("[+] تم تحديث app/services/ai/gemini.py")
print()
print("النماذج المضافة (بالترتيب):")
for m in ["gemini-4-argon", "gemini-3.8-flash", "gemini-3.8-live",
          "gemini-3.8-flash-extended-thinking", "gemini-2.5-flash",
          "gemini-2.5-pro", "gemini-2.5-flash-thinking", "gemini-2.0-flash",
          "gemini-2.0-flash-thinking-exp", "gemini-1.5-flash-latest"]:
    print(f"   - {m}")
print()
print("=" * 60)
print("✅ جاهز. ارفع الآن:")
print("   git add -A")
print('   git commit -m "Update Gemini models list"')
print("   git push origin main")
print("=" * 60)
