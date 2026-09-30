from fastapi import APIRouter
from app.core.config import settings
from app.services.ai.router import get_ai

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok", "app": settings.APP_NAME,
        "app_ar": settings.APP_NAME_AR, "version": settings.APP_VERSION,
        "developer": settings.DEVELOPER, "providers": get_ai().status(),
    }


@router.get("/")
async def root():
    return {
        "name": settings.APP_NAME, "name_ar": settings.APP_NAME_AR,
        "slogan": settings.SLOGAN, "version": settings.APP_VERSION,
    }
