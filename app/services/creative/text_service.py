"""Text generation via AI router."""
from app.prompts.creative_prompts import article_prompt, script_prompt, story_prompt
from app.prompts.system_prompt import CREATIVE_SYSTEM
from app.services.ai.router import get_ai


BUILDERS = {
    "article": article_prompt,
    "script": script_prompt,
    "story": story_prompt,
}


async def generate(prompt: str, kind: str = "article",
                   tone: str = "creative", length: int = 500) -> str:
    builder = BUILDERS.get(kind, article_prompt)
    full = builder(prompt, tone, length)
    return await get_ai().chat(full, system=CREATIVE_SYSTEM, temperature=0.9)
