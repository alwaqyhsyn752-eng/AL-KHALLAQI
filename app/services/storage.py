"""Storage helpers (works persistence)."""
import secrets
from typing import Any, Dict, Optional
from sqlalchemy import select, desc
from app.db.engine import session_scope
from app.models.db_models import Work


def _new_token() -> str:
    return secrets.token_urlsafe(12)


async def save_work(title: str, kind: str, prompt: str = "",
                    content: str = "", extra: Optional[Dict[str, Any]] = None,
                    public: bool = False) -> Dict:
    async with session_scope() as s:
        w = Work(title=title, kind=kind, prompt=prompt,
                 content=content, extra=extra or {},
                 public=public, token=_new_token())
        s.add(w)
        await s.flush()
        return w.to_dict()


async def list_works(kind: Optional[str] = None, limit: int = 60) -> list:
    async with session_scope() as s:
        q = select(Work).order_by(desc(Work.created_at)).limit(limit)
        if kind:
            q = q.where(Work.kind == kind)
        rows = (await s.execute(q)).scalars().all()
        return [r.to_dict() for r in rows]


async def get_work(work_id: int) -> Optional[Dict]:
    async with session_scope() as s:
        w = await s.get(Work, work_id)
        return w.to_dict() if w else None


async def get_work_by_token(token: str) -> Optional[Dict]:
    async with session_scope() as s:
        q = select(Work).where(Work.token == token)
        w = (await s.execute(q)).scalars().first()
        return w.to_dict() if w else None


async def delete_work(work_id: int) -> bool:
    async with session_scope() as s:
        w = await s.get(Work, work_id)
        if not w:
            return False
        await s.delete(w)
        return True
