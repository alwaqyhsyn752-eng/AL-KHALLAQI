from app.services.agent.tools.registry import register
from app.services.creative import video_service


async def _run(prompt: str, duration: int = 4, aspect: str = "16:9"):
    return await video_service.generate(prompt, duration, aspect)


register("video_gen", "توليد فيديو قصير (GIF) من وصف.", _run)
