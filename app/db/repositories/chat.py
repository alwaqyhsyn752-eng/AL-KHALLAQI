from typing import Any, Dict, List
from sqlalchemy import select, desc
from app.db.engine import session_scope
from app.models.db_models import ChatMessage


async def add(session_id: str, role: str, content: str,
              extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    async with session_scope() as s:
        m = ChatMessage(session_id=session_id, role=role,
                        content=content, extra=extra or {})
        s.add(m)
        await s.flush()
        return m.to_dict()


async def history(session_id: str, limit: int = 30) -> List[Dict[str, Any]]:
    async with session_scope() as s:
        q = (select(ChatMessage)
             .where(ChatMessage.session_id == session_id)
             .order_by(desc(ChatMessage.created_at))
             .limit(limit))
        rows = (await s.execute(q)).scalars().all()
        return [r.to_dict() for r in reversed(rows)]
