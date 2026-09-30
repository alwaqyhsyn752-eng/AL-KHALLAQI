from app.services.agent.tools.registry import register
from app.services.creative import image_service


async def _run(image_url: str, instruction: str):
    return await image_service.edit(image_url, instruction)


register("image_edit", "تعديل صورة موجودة بناءً على وصف.", _run)
