"""Video generation: frames sequence -> GIF."""
import io
import base64
from typing import Dict
import httpx
from PIL import Image
from app.core.logging import log
from app.prompts.creative_prompts import video_prompt


SIZES = {"16:9": (768, 432), "9:16": (432, 768), "1:1": (512, 512)}


async def generate(prompt: str, duration: int = 4, aspect: str = "16:9",
                   frames: int = 12) -> Dict:
    w, h = SIZES.get(aspect, SIZES["16:9"])
    frames = max(4, min(frames, 24))
    base = video_prompt(prompt)
    from app.services.creative.image_service import _url

    urls = []
    images = []
    async with httpx.AsyncClient(timeout=90.0) as c:
        for i in range(frames):
            seed = 1000 + i * 7
            u = _url(f"{base}, frame {i+1}/{frames}", w, h, seed=seed)
            urls.append(u)
            try:
                r = await c.get(u)
                if r.status_code == 200:
                    images.append(Image.open(io.BytesIO(r.content)).convert("RGB"))
            except Exception as e:
                log.warning("frame %d failed: %s", i, e)

    gif_url = ""
    if images:
        buf = io.BytesIO()
        try:
            images[0].save(buf, format="GIF", save_all=True,
                           append_images=images[1:],
                           duration=int((duration * 1000) / len(images)),
                           loop=0)
            gif_url = "data:image/gif;base64," + base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            log.warning("gif build failed: %s", e)

    return {
        "prompt": base, "frames": urls, "gif": gif_url,
        "duration": duration, "aspect": aspect, "ok": bool(images),
    }
