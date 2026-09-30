"""Video generation via frames + GIF."""
import io, base64
from typing import Dict
import httpx
from PIL import Image
from app.core.logging import log
from app.prompts.creative_prompts import video_prompt
from app.services.creative.image_service import _url, _prepare_prompt


SIZES = {"16:9": (512, 288), "9:16": (288, 512), "1:1": (400, 400)}


async def generate(prompt: str, duration: int = 4, aspect: str = "16:9",
                   frames: int = 8) -> Dict:
    w, h = SIZES.get(aspect, SIZES["16:9"])
    frames = max(4, min(frames, 12))
    translated = await _prepare_prompt(prompt)
    base = video_prompt(translated)

    urls, images = [], []
    async with httpx.AsyncClient(timeout=60.0) as c:
        for i in range(frames):
            seed = 2000 + i * 13
            u = _url(f"{base}, motion scene {i+1}", w, h, seed=seed)
            urls.append(u)
            try:
                r = await c.get(u)
                if r.status_code == 200 and len(r.content) > 500:
                    images.append(Image.open(io.BytesIO(r.content)).convert("RGB"))
            except Exception as e:
                log.warning("frame %d: %s", i, e)

    gif_url = ""
    if len(images) >= 2:
        try:
            buf = io.BytesIO()
            images[0].save(
                buf, format="GIF", save_all=True,
                append_images=images[1:],
                duration=int((duration * 1000) / len(images)),
                loop=0, optimize=False,
            )
            gif_url = "data:image/gif;base64," + base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            log.warning("gif build: %s", e)

    return {
        "prompt": base, "frames": urls, "gif": gif_url,
        "duration": duration, "aspect": aspect,
        "frame_count": len(images), "ok": bool(images),
    }
