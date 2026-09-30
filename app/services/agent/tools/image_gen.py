from app.services.agent.tools.registry import register
from app.services.creative import image_service


async def _run(prompt: str, style: str = "realistic",
               width: int = 1024, height: int = 1024, seed=None):
    return await image_service.generate(prompt, style, width, height, seed)


register("image_gen", "توليد صورة من وصف نصي.", _run)
