from fastapi import APIRouter, HTTPException
from app.models.schemas import WorkCreate
from app.services import storage

router = APIRouter()


@router.get("/works")
async def list_works(kind: str | None = None, limit: int = 60):
    return {"works": await storage.list_works(kind, limit)}


@router.post("/works")
async def create_work(req: WorkCreate):
    return await storage.save_work(req.title, req.kind, req.prompt,
                                   req.content, req.extra, req.public)


@router.get("/works/{wid}")
async def get_work(wid: int):
    w = await storage.get_work(wid)
    if not w:
        raise HTTPException(404, "not found")
    return w


@router.delete("/works/{wid}")
async def del_work(wid: int):
    ok = await storage.delete_work(wid)
    if not ok:
        raise HTTPException(404, "not found")
    return {"ok": True}
