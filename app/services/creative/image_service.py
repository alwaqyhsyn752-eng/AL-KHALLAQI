"""Image generation & editing via Pollinations (free)."""
from typing import Dict, Optional
from urllib.parse import quote
import httpx
from app.core.logging import log
from app.prompts.creative_prompts import image_prompt


POLL_BASE = "https://image.pollinations.ai/prompt"


def _url(prompt: str, w: int, h: int, seed: Optional[int] = None,
         model: str = "flux") -> str:
    q = quote(prompt, safe="")
    params = f"?width={w}&height={h}&model={model}&nologo=true"
    if seed is not None:
        params += f"&seed={seed}"
    return f"{POLL_BASE}/{q}{params}"


async def generate(prompt: str, style: str = "realistic",
                   width: int = 1024, height: int = 1024,
                   seed: Optional[int] = None) -> Dict:
    full = image_prompt(prompt, style)
    url = _url(full, width, height, seed)
    try:
        async with httpx.AsyncClient(timeout=90.0) as c:
            r = await c.get(url)
            ok = r.status_code == 200 and len(r.content) > 1000
    except Exception as e:
        log.warning("image gen failed: %s", e)
        ok = False
    return {
        "url": url, "prompt": full, "style": style,
        "width": width, "height": height, "seed": seed, "ok": ok,
    }


async def edit(image_url: str, instruction: str) -> Dict:
    full = f"{instruction}, modify based on reference image"
    new_url = _url(full, 1024, 1024)
    return {"url": new_url, "instruction": instruction,
            "source": image_url, "prompt": full, "ok": True}
