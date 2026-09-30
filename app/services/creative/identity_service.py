"""Identity design (colors + fonts + logo + tagline)."""
import json
from typing import Dict
from app.prompts.system_prompt import CREATIVE_SYSTEM
from app.services.ai.router import get_ai


async def design(brand: str, industry: str = "", mood: str = "modern") -> Dict:
    prompt = f"""صمّم هوية بصرية كاملة للعلامة التجارية: {brand}
المجال: {industry or "عام"}
المزاج: {mood}

أعد الإجابة بصيغة JSON فقط (بدون نص إضافي) بهذا الشكل:
{{
  "tagline": "شعار نصي قصير",
  "palette": ["#hex1", "#hex2", "#hex3", "#hex4"],
  "fonts": {{"headline": "اسم خط", "body": "اسم خط"}},
  "logo_concept": "وصف مفصل للشعار",
  "tone_of_voice": "وصف نبرة الصوت",
  "visual_keywords": ["كلمة1", "كلمة2", "كلمة3"]
}}
"""
    raw = await get_ai().chat(prompt, system=CREATIVE_SYSTEM, temperature=0.9)
    txt = raw.strip()
    if "```" in txt:
        txt = txt.split("```")[1]
        if txt.startswith("json"):
            txt = txt[4:]
    try:
        data = json.loads(txt)
    except Exception:
        data = {"raw": raw, "tagline": brand,
                "palette": ["#a855f7", "#22d3ee", "#fbbf24", "#f472b6"]}
    data["brand"] = brand
    data["industry"] = industry
    data["mood"] = mood
    return data


async def logo_svg(brand: str, industry: str = "", style: str = "modern",
                   colors: list = None) -> str:
    colors = colors or ["#a855f7", "#22d3ee", "#fbbf24"]
    initials = "".join([w[0] for w in brand.split()[:2]]).upper() or "AK"
    c1, c2, c3 = (colors + ["#a855f7", "#22d3ee", "#fbbf24"])[:3]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
<defs>
<linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="{c1}"/>
<stop offset="50%" stop-color="{c2}"/>
<stop offset="100%" stop-color="{c3}"/>
</linearGradient>
<filter id="glow"><feGaussianBlur stdDeviation="6" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="400" height="400" rx="60" fill="#0b0820"/>
<circle cx="200" cy="160" r="90" fill="url(#g1)" filter="url(#glow)" opacity="0.85"/>
<text x="200" y="190" font-family="Poppins,Arial,sans-serif" font-size="86" font-weight="900"
text-anchor="middle" fill="#ffffff">{initials}</text>
<text x="200" y="290" font-family="Poppins,Arial,sans-serif" font-size="34" font-weight="700"
text-anchor="middle" fill="url(#g1)">{brand}</text>
<text x="200" y="330" font-family="Poppins,Arial,sans-serif" font-size="16"
text-anchor="middle" fill="#c4b5fd" opacity="0.8">{industry or "CREATIVE AI"}</text>
</svg>"""
