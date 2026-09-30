"""Lightweight web search via DuckDuckGo HTML."""
import re
from typing import Dict, List
from urllib.parse import quote_plus
import httpx
from app.core.logging import log


async def search(query: str, limit: int = 5) -> List[Dict[str, str]]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (AL-KHALLAQI/1.0)"}
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as c:
            r = await c.get(url, headers=headers)
        if r.status_code != 200:
            return []
        results = []
        pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        for m in re.finditer(pattern, r.text, re.DOTALL):
            href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if title and href.startswith("http"):
                results.append({"title": title, "url": href})
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        log.warning("search failed: %s", e)
        return []
