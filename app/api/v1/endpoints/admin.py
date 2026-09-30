from fastapi import APIRouter, Header, HTTPException
from app.core.config import settings
from app.services.ai.router import get_ai
from app.services import storage

router = APIRouter()


def _check(pwd: str | None):
    if pwd != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "unauthorized")


def _count_by_kind(works):
    out = {}
    for w in works:
        k = w.get("kind", "?")
        out[k] = out.get(k, 0) + 1
    return out


@router.get("/stats")
async def stats(x_admin_password: str | None = Header(default=None)):
    _check(x_admin_password)
    works = await storage.list_works(limit=1000)
    return {
        "total_works": len(works),
        "by_kind": _count_by_kind(works),
        "providers": get_ai().status(),
        "version": settings.APP_VERSION,
    }
