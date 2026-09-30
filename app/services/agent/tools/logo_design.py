from app.services.agent.tools.registry import register
from app.services.creative.identity_service import logo_svg


async def _run(brand: str, industry: str = "",
               style: str = "modern", colors=None):
    svg = await logo_svg(brand, industry, style, colors or [])
    return {"svg": svg, "brand": brand}


register("logo_design", "تصميم شعار SVG.", _run)
