from app.services.agent.tools.registry import register
from app.services.creative import text_service


async def _run(prompt: str, kind: str = "article",
               tone: str = "creative", length: int = 500):
    text = await text_service.generate(prompt, kind, tone, length)
    return {"text": text, "kind": kind}


register("text_gen", "توليد نص إبداعي (مقال/قصة/سيناريو).", _run)
