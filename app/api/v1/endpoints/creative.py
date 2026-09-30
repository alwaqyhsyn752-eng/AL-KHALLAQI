from fastapi import APIRouter
from app.models.schemas import (
    ImageRequest, ImageEditRequest, VideoRequest, TextRequest,
)
from app.services.creative import image_service, video_service, text_service

router = APIRouter()


@router.post("/image")
async def gen_image(req: ImageRequest):
    return await image_service.generate(req.prompt, req.style,
                                        req.width, req.height, req.seed)


@router.post("/image/edit")
async def edit_image(req: ImageEditRequest):
    return await image_service.edit(req.image_url, req.instruction)


@router.post("/video")
async def gen_video(req: VideoRequest):
    return await video_service.generate(req.prompt, req.duration,
                                        req.aspect, req.frames)


@router.post("/text")
async def gen_text(req: TextRequest):
    text = await text_service.generate(req.prompt, req.kind,
                                       req.tone, req.length)
    return {"text": text, "kind": req.kind}
