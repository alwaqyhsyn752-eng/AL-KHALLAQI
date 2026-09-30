from typing import Any, Dict
from sqlalchemy import select, desc
from app.db.engine import session_scope
from app.models.db_models import Project


async def create(**kw) -> Dict[str, Any]:
    async with session_scope() as s:
        p = Project(**kw)
        s.add(p)
        await s.flush()
        return p.to_dict()


async def list_all(limit: int = 40) -> list:
    async with session_scope() as s:
        q = select(Project).order_by(desc(Project.created_at)).limit(limit)
        return [r.to_dict() for r in (await s.execute(q)).scalars().all()]
