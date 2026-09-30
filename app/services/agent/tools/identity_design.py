from app.services.agent.tools.registry import register
from app.services.creative import identity_service
from app.services.creative.identity_service import logo_svg


async def _run(brand: str, industry: str = "", mood: str = "modern"):
    data = await identity_service.design(brand, industry, mood)
    data["logo_svg"] = await logo_svg(brand, industry, "modern",
                                      data.get("palette", []))
    return data


register("identity_design", "بناء هوية بصرية كاملة.", _run)
