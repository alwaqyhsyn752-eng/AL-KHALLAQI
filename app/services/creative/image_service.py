"""Image generation & editing via Pollinations with Arabic support."""
import re
from typing import Dict, Optional
from urllib.parse import quote
import httpx
from app.core.logging import log
from app.prompts.creative_prompts import image_prompt


POLL_BASE = "https://image.pollinations.ai/prompt"


# ترجمة عربي → إنجليزي (قاموس أساسي + fallback للـ AI)
_AR_TO_EN = {
    "قطة": "cat", "قط": "cat", "كلب": "dog", "بيت": "house",
    "شجرة": "tree", "بحر": "sea", "جبل": "mountain", "سماء": "sky",
    "شمس": "sun", "قمر": "moon", "نجمة": "star", "زهرة": "flower",
    "سيارة": "car", "طائرة": "airplane", "مدينة": "city", "قرية": "village",
    "طفل": "child", "رجل": "man", "امرأة": "woman", "بنت": "girl", "ولد": "boy",
    "طائر": "bird", "سمك": "fish", "أسد": "lion", "فيل": "elephant",
    "غروب": "sunset", "شروق": "sunrise", "مطر": "rain", "ثلج": "snow",
    "غابة": "forest", "صحراء": "desert", "نهر": "river", "بحيرة": "lake",
    "سايبربانك": "cyberpunk", "مستقبلي": "futuristic", "فضاء": "space",
    "روبوت": "robot", "تنين": "dragon", "قصر": "palace", "برج": "tower",
}


def _is_arabic(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))


def _translate_simple(text: str) -> str:
    """ترجمة بسيطة بالقاموس — إن فشلت نترك الأصل."""
    result = text
    for ar, en in _AR_TO_EN.items():
        result = result.replace(ar, en)
    return result


async def _translate_ai(text: str) -> str:
    """ترجمة عبر AI — يعطي نتائج أفضل بكثير."""
    try:
        from app.services.ai.router import get_ai
        prompt = (
            f"Translate to vivid English for image generation prompt. "
            f"Only output the translation, no quotes:\n{text}"
        )
        result = await get_ai().chat(prompt, temperature=0.3, max_tokens=200)
        return result.strip().strip('"').strip("'")
    except Exception as e:
        log.warning("AI translation failed: %s", e)
        return _translate_simple(text)


async def _prepare_prompt(user_prompt: str) -> str:
    """يحوّل العربية → إنجليزية مع إضافة سياق."""
    if _is_arabic(user_prompt):
        return await _translate_ai(user_prompt)
    return user_prompt


def _url(prompt: str, w: int, h: int, seed: Optional[int] = None,
         model: str = "flux") -> str:
    q = quote(prompt, safe="")
    params = f"?width={w}&height={h}&model={model}&nologo=true&enhance=true"
    if seed is not None:
        params += f"&seed={seed}"
    return f"{POLL_BASE}/{q}{params}"


async def generate(prompt: str, style: str = "realistic",
                   width: int = 1024, height: int = 1024,
                   seed: Optional[int] = None) -> Dict:
    # ترجمة إذا كانت عربية
    translated = await _prepare_prompt(prompt)
    full = image_prompt(translated, style)
    url = _url(full, width, height, seed)
    try:
        async with httpx.AsyncClient(timeout=120.0) as c:
            r = await c.get(url)
            ok = r.status_code == 200 and len(r.content) > 1000
    except Exception as e:
        log.warning("image gen failed: %s", e)
        ok = False
    return {
        "url": url, "prompt": full, "original_prompt": prompt,
        "translated": translated, "style": style,
        "width": width, "height": height, "seed": seed, "ok": ok,
    }


async def edit(image_url: str, instruction: str) -> Dict:
    translated = await _prepare_prompt(instruction)
    full = f"{translated}, high quality"
    new_url = _url(full, 1024, 1024)
    return {"url": new_url, "instruction": instruction,
            "source": image_url, "prompt": full, "ok": True}
