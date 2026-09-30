"""API Keys management."""
import secrets
from fastapi import APIRouter, Header, HTTPException
from app.core.config import settings
from app.db.engine import session_scope
from app.models.db_models import Project
from sqlalchemy import select, desc

router = APIRouter()


def _check(pwd: str | None):
    if pwd != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "unauthorized")


@router.post("/create")
async def create_key(name: str, x_admin_password: str | None = Header(default=None)):
    _check(x_admin_password)
    key = "hk_" + secrets.token_urlsafe(32)
    async with session_scope() as s:
        proj = Project(
            name=name or "api-key",
            description="API key",
            theme={"api_key": key, "type": "apikey"},
            status="active",
        )
        s.add(proj)
        await s.flush()
    return {"name": name, "key": key, "status": "active"}


@router.get("/list")
async def list_keys(x_admin_password: str | None = Header(default=None)):
    _check(x_admin_password)
    async with session_scope() as s:
        q = (select(Project)
             .where(Project.status == "active")
             .order_by(desc(Project.created_at))
             .limit(50))
        rows = (await s.execute(q)).scalars().all()
        keys = []
        for r in rows:
            theme = r.theme or {}
            if theme.get("type") == "apikey":
                keys.append({"id": r.id, "name": r.name,
                             "key": theme.get("api_key", ""),
                             "created_at": r.created_at.isoformat() if r.created_at else None})
        return {"keys": keys}


@router.delete("/{kid}")
async def delete_key(kid: int, x_admin_password: str | None = Header(default=None)):
    _check(x_admin_password)
    async with session_scope() as s:
        p = await s.get(Project, kid)
        if not p:
            raise HTTPException(404, "not found")
        await s.delete(p)
    return {"ok": True}
