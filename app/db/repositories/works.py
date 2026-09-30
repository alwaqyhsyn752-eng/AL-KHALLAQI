from typing import Any, Dict, Optional
from sqlalchemy import select, desc
from app.db.engine import session_scope
from app.models.db_models import Work


async def create(**kw) -> Dict[str, Any]:
    async with session_scope() as s:
        w = Work(**kw)
        s.add(w)
        await s.flush()
        return w.to_dict()


async def list_all(kind: Optional[str] = None, limit: int = 60) -> list:
    async with session_scope() as s:
        q = select(Work).order_by(desc(Work.created_at)).limit(limit)
        if kind:
            q = q.where(Work.kind == kind)
        return [r.to_dict() for r in (await s.execute(q)).scalars().all()]


async def get_by_id(wid: int) -> Optional[Dict[str, Any]]:
    async with session_scope() as s:
        w = await s.get(Work, wid)
        return w.to_dict() if w else None


async def delete(wid: int) -> bool:
    async with session_scope() as s:
        w = await s.get(Work, wid)
        if not w:
            return False
        await s.delete(w)
        return True
