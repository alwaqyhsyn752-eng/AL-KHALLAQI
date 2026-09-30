from app.services.agent.tools.registry import register
from app.services import web_search


async def _run(query: str, limit: int = 5):
    return {"query": query, "results": await web_search.search(query, limit)}


register("search", "بحث مرجعي على الويب.", _run)
