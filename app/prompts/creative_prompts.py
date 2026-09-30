"""Creative prompt builders."""


def image_prompt(user_prompt: str, style: str = "realistic") -> str:
    style_map = {
        "realistic": "ultra-realistic, 8k, professional photography, sharp focus",
        "artistic": "digital art, painterly, expressive brushstrokes, artstation",
        "cyberpunk": "cyberpunk, neon lights, futuristic city, blade runner mood",
        "anime": "anime style, studio ghibli inspired, vivid colors, cel shading",
    }
    suffix = style_map.get(style, style_map["realistic"])
    return f"{user_prompt}, {suffix}, high detail, cinematic lighting"


def video_prompt(user_prompt: str) -> str:
    return f"{user_prompt}, cinematic, smooth motion, high quality"


def script_prompt(topic: str, tone: str = "creative", length: int = 500) -> str:
    return (f"اكتب سيناريو إبداعي عن: {topic}\n"
            f"النبرة: {tone}\nالطول التقريبي: {length} كلمة\n"
            f"قسّمه إلى: مشهد افتتاحي، تطوير، ذروة، خاتمة.")


def article_prompt(topic: str, tone: str = "creative", length: int = 500) -> str:
    return (f"اكتب مقالاً إبداعياً عن: {topic}\n"
            f"النبرة: {tone}\nعدد الكلمات: حوالي {length}\n"
            f"استخدم عناوين فرعية ونقاط عند الحاجة.")


def story_prompt(topic: str, tone: str = "creative", length: int = 500) -> str:
    return (f"اكتب قصة قصيرة عن: {topic}\nالنبرة: {tone}\n"
            f"الطول: ~{length} كلمة\nاجعل لها بداية مشوقة ونهاية مؤثرة.")
