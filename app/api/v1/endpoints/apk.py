"""APK builder endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services import apk_builder

router = APIRouter()


class BuildRequest(BaseModel):
    version: str = "1.0.0"


@router.post("/build")
async def build(req: BuildRequest):
    return await apk_builder.trigger_build(req.version)


@router.get("/latest")
async def latest():
    return await apk_builder.get_latest_release()
