"""Thinking modes."""
from typing import Dict

MODES: Dict[str, str] = {
    "creative": "فكّر بجرأة، اقترح أفكاراً غير تقليدية، استخدم الصور البلاغية.",
    "analytical": "حلّل المشكلة منطقياً، فكّك العناصر، ابنِ استنتاجك خطوة بخطوة.",
    "strategic": "فكّر على المدى البعيد، ضع خطة مرحلية، رتّب الأولويات.",
    "divergent": "ولّد أكبر عدد من الأفكار، لا تحكم عليها، ثم اختر الأفضل.",
    "critical": "افحص الفكرة من كل زاوية، ابحث عن نقاط الضعف، ثم اقترح تحسينات.",
}


def apply_mode(mode: str) -> str:
    return MODES.get(mode, MODES["creative"])
