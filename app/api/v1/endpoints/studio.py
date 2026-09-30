from fastapi import APIRouter
from app.models.schemas import LogoRequest, IdentityRequest
from app.services.creative.identity_service import design, logo_svg

router = APIRouter()


@router.post("/logo")
async def make_logo(req: LogoRequest):
    svg = await logo_svg(req.brand, req.industry, req.style, req.colors)
    return {"brand": req.brand, "svg": svg}


@router.post("/identity")
async def make_identity(req: IdentityRequest):
    data = await design(req.brand, req.industry, req.mood)
    data["logo_svg"] = await logo_svg(req.brand, req.industry, "modern",
                                      data.get("palette", []))
    return data
