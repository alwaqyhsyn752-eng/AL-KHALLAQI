"""Redis with in-memory fallback."""
import json, time
from typing import Any, Optional
from app.core.config import settings
from app.core.logging import log


class InMemoryCache:
    def __init__(self) -> None:
        self._data: dict = {}

    async def get(self, key: str):
        item = self._data.get(key)
        if not item:
            return None
        value, expires = item
        if expires is not None and time.time() > expires:
            self._data.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires = (time.time() + ttl) if ttl else None
        self._data[key] = (value, expires)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def close(self) -> None:
        self._data.clear()


class RedisCache:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def get(self, key: str):
        try:
            raw = await self._client.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            log.warning("Redis get failed: %s", e)
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        try:
            payload = json.dumps(value, ensure_ascii=False, default=str)
            if ttl:
                await self._client.setex(key, ttl, payload)
            else:
                await self._client.set(key, payload)
        except Exception as e:
            log.warning("Redis set failed: %s", e)

    async def delete(self, key: str) -> None:
        try:
            await self._client.delete(key)
        except Exception:
            pass

    async def close(self) -> None:
        try:
            await self._client.aclose()
        except Exception:
            pass


_cache = None


async def get_cache():
    global _cache
    if _cache is not None:
        return _cache
    try:
        import redis.asyncio as aioredis
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        _cache = RedisCache(client)
        log.info("Redis connected")
    except Exception as e:
        log.warning("Redis unavailable, using memory: %s", e)
        _cache = InMemoryCache()
    return _cache


async def close_cache() -> None:
    global _cache
    if _cache is not None:
        await _cache.close()
        _cache = None
