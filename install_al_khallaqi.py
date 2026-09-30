#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AL-KHALLAQI — Single Install Script
يُنشئ مشروع AL-KHALLAQI كاملاً (78+ ملف) بأمر واحد.
تشغيل: python install_al_khallaqi.py
"""
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
CREATED = []

def w(rel: str, content: str) -> None:
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    CREATED.append(rel)
    print(f"[+] {rel}")

# ═══════════════════════════════════════════════════════════════
# 1) PACKAGE INIT FILES
# ═══════════════════════════════════════════════════════════════
w("app/__init__.py", '"""AL-KHALLAQI package."""\n')
w("app/core/__init__.py", '"""Core utilities."""\n')
w("app/db/__init__.py", '"""Database layer."""\n')
w("app/db/repositories/__init__.py", '"""Repositories."""\n')
w("app/models/__init__.py", '"""Models."""\n')
w("app/services/__init__.py", '"""Services layer."""\n')
w("app/services/ai/__init__.py", '"""AI providers."""\n')
w("app/services/creative/__init__.py", '"""Creative services."""\n')
w("app/services/agent/__init__.py", '"""Creative Agent."""\n')
w("app/services/agent/tools/__init__.py", '"""Agent tools."""\n')
w("app/api/__init__.py", '"""API."""\n')
w("app/api/v1/__init__.py", '"""API v1."""\n')
w("app/api/v1/endpoints/__init__.py", '"""Endpoints."""\n')
w("app/prompts/__init__.py", '"""Prompts."""\n')

# ═══════════════════════════════════════════════════════════════
# 2) CORE
# ═══════════════════════════════════════════════════════════════
w("app/core/config.py", r'''"""Application configuration for AL-KHALLAQI."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=True, extra="ignore",
    )

    APP_NAME: str = "AL-KHALLAQI"
    APP_NAME_AR: str = "الخلاقي"
    APP_VERSION: str = "1.0.0"
    DEVELOPER: str = "Hussein Ghallab"
    SLOGAN: str = "الإبداع بلا حدود"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""

    GITHUB_ACTIONS_TOKEN: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    ADMIN_PASSWORD: str = "hussein2026"

    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"

    MAX_AGENT_STEPS: int = 8
    REQUEST_TIMEOUT: int = 90

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL or "sqlite+aiosqlite:///./al_khallaqi.db"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
''')

w("app/core/logging.py", r'''"""Logging setup."""
import logging, sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("al_khallaqi")
    if logger.handlers:
        return logger
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


log = setup_logging()
''')

w("app/core/exceptions.py", r'''"""Custom exceptions."""
from typing import Optional


class HKBaseError(Exception):
    status_code: int = 500
    message: str = "Internal error"

    def __init__(self, message: Optional[str] = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class ConfigurationError(HKBaseError):
    status_code = 500
    message = "Configuration error"


class ProviderError(HKBaseError):
    status_code = 502
    message = "AI provider error"


class ToolError(HKBaseError):
    status_code = 400
    message = "Tool execution error"


class NotFoundError(HKBaseError):
    status_code = 404
    message = "Resource not found"


class AuthError(HKBaseError):
    status_code = 401
    message = "Unauthorized"


class ValidationError(HKBaseError):
    status_code = 422
    message = "Validation error"


class AgentMaxStepsError(HKBaseError):
    status_code = 422
    message = "Agent reached maximum steps"
''')

# ═══════════════════════════════════════════════════════════════
# 3) DATABASE
# ═══════════════════════════════════════════════════════════════
w("app/db/engine.py", r'''"""Async SQLAlchemy engine."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine,
)

from app.core.config import settings
from app.core.logging import log

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        url = settings.async_database_url
        kwargs = {"echo": settings.DEBUG, "future": True}
        if url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            kwargs["pool_pre_ping"] = True
            kwargs["pool_size"] = 5
            kwargs["max_overflow"] = 10
            kwargs["pool_recycle"] = 1800
        _engine = create_async_engine(url, **kwargs)
        log.info("DB engine created (%s)", url.split("://", 1)[0])
    return _engine


def get_session_factory() -> async_sessionmaker:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(), class_=AsyncSession,
            expire_on_commit=False, autoflush=False,
        )
    return _session_factory


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_scope() as session:
        yield session


async def init_db() -> None:
    from app.models.db_models import Base
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables initialized")


async def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
''')

w("app/db/redis.py", r'''"""Redis with in-memory fallback."""
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
''')

# ═══════════════════════════════════════════════════════════════
# 4) DB MODELS + SCHEMAS
# ═══════════════════════════════════════════════════════════════
w("app/models/db_models.py", r'''"""SQLAlchemy ORM models."""
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import (
    Boolean, DateTime, Integer, JSON, String, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Work(Base):
    __tablename__ = "works"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    extra: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    public: Mapped[bool] = mapped_column(Boolean, default=False)
    token: Mapped[str] = mapped_column(String(64), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "kind": self.kind,
            "prompt": self.prompt, "content": self.content,
            "extra": self.extra or {}, "public": self.public,
            "token": self.token,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    theme: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    html: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    apk_url: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name,
            "description": self.description, "theme": self.theme or {},
            "status": self.status, "apk_url": self.apk_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text, default="")
    extra: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "session_id": self.session_id, "role": self.role,
            "content": self.content, "extra": self.extra or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    goal: Mapped[str] = mapped_column(Text, default="")
    steps: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    final_answer: Mapped[str] = mapped_column(Text, default="")
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
''')

w("app/models/schemas.py", r'''"""Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkCreate(BaseModel):
    title: str
    kind: str
    prompt: str = ""
    content: str = ""
    extra: Dict[str, Any] = Field(default_factory=dict)
    public: bool = False


class WorkOut(BaseModel):
    id: int
    title: str
    kind: str
    prompt: str
    content: str
    extra: Dict[str, Any]
    public: bool
    token: str
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ImageRequest(BaseModel):
    prompt: str
    style: str = "realistic"
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None
    count: int = 1


class ImageEditRequest(BaseModel):
    image_url: str
    instruction: str


class VideoRequest(BaseModel):
    prompt: str
    duration: int = 4
    aspect: str = "16:9"
    frames: int = 12


class TextRequest(BaseModel):
    prompt: str
    kind: str = "article"
    tone: str = "creative"
    length: int = 500


class LogoRequest(BaseModel):
    brand: str
    industry: str = ""
    style: str = "modern"
    colors: List[str] = Field(default_factory=list)


class IdentityRequest(BaseModel):
    brand: str
    industry: str = ""
    mood: str = "modern"


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    extra: Dict[str, Any] = Field(default_factory=dict)


class AgentRequest(BaseModel):
    goal: str
    session_id: str = "default"
    max_steps: int = 8


class AgentStep(BaseModel):
    step: int
    thought: str = ""
    action: str = ""
    action_input: Dict[str, Any] = Field(default_factory=dict)
    observation: str = ""
    final: bool = False


class AgentResponse(BaseModel):
    goal: str
    steps: List[AgentStep]
    final_answer: str
    success: bool = True


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class ApkRequest(BaseModel):
    name: str
    description: str = ""
    theme: Dict[str, Any] = Field(default_factory=dict)
    html: str = ""


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str
    providers: Dict[str, bool] = Field(default_factory=dict)
''')

# ═══════════════════════════════════════════════════════════════
# 5) AI PROVIDERS
# ═══════════════════════════════════════════════════════════════
w("app/services/ai/base.py", r'''"""Base provider."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChatMessage:
    role: str
    content: str


class BaseProvider:
    name: str = "base"
    default_model: str = ""

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        raise NotImplementedError
''')

w("app/services/ai/_openai_compat.py", r'''"""OpenAI-compatible provider base."""
from typing import List, Optional
import httpx
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


class OpenAICompatProvider(BaseProvider):
    base_url: str = ""
    default_model: str = ""

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.available:
            raise ProviderError(f"{self.name}: no API key")

        payload = {
            "model": model or self.default_model,
            "messages": ([{"role": "system", "content": system}] if system else [])
                        + [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=90.0) as c:
            r = await c.post(f"{self.base_url}/chat/completions",
                             json=payload, headers=headers)
        if r.status_code >= 400:
            log.warning("%s error %s: %s", self.name, r.status_code, r.text[:200])
            raise ProviderError(f"{self.name}: {r.status_code}")
        data = r.json()
        return data["choices"][0]["message"]["content"]
''')

w("app/services/ai/groq.py", r'''"""Groq provider."""
from app.services.ai._openai_compat import OpenAICompatProvider


class GroqProvider(OpenAICompatProvider):
    name = "groq"
    base_url = "https://api.groq.com/openai/v1"
    default_model = "llama-3.3-70b-versatile"
''')

w("app/services/ai/openrouter.py", r'''"""OpenRouter provider."""
from app.services.ai._openai_compat import OpenAICompatProvider


class OpenRouterProvider(OpenAICompatProvider):
    name = "openrouter"
    base_url = "https://openrouter.ai/api/v1"
    default_model = "meta-llama/llama-3.3-70b-instruct:free"
''')

w("app/services/ai/deepseek.py", r'''"""DeepSeek provider."""
from app.services.ai._openai_compat import OpenAICompatProvider


class DeepSeekProvider(OpenAICompatProvider):
    name = "deepseek"
    base_url = "https://api.deepseek.com/v1"
    default_model = "deepseek-chat"
''')

w("app/services/ai/gemini.py", r'''"""Gemini provider with fallback models."""
from typing import List, Optional
import httpx
from app.core.exceptions import ProviderError
from app.services.ai.base import BaseProvider, ChatMessage


MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]


class GeminiProvider(BaseProvider):
    name = "gemini"
    default_model = "gemini-2.0-flash"
    base = "https://generativelanguage.googleapis.com/v1beta"

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.available:
            raise ProviderError("gemini: no API key")

        contents = []
        for m in messages:
            role = "user" if m.role in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        last_err = None
        for mdl in ([model] if model else MODELS):
            url = f"{self.base}/models/{mdl}:generateContent?key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=90.0) as c:
                    r = await c.post(url, json=body)
                if r.status_code >= 400:
                    last_err = f"{mdl}: {r.status_code}"
                    continue
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                last_err = f"{mdl}: {e}"
                continue
        raise ProviderError(f"gemini failed: {last_err}")
''')

w("app/services/ai/router.py", r'''"""AI Router: tries providers in order."""
from typing import List, Optional
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import ChatMessage
from app.services.ai.gemini import GeminiProvider
from app.services.ai.groq import GroqProvider
from app.services.ai.openrouter import OpenRouterProvider
from app.services.ai.deepseek import DeepSeekProvider


class AIRouter:
    def __init__(self) -> None:
        self.providers = [
            GeminiProvider(settings.GEMINI_API_KEY),
            GroqProvider(settings.GROQ_API_KEY),
            OpenRouterProvider(settings.OPENROUTER_API_KEY),
            DeepSeekProvider(settings.DEEPSEEK_API_KEY),
        ]

    def status(self) -> dict:
        return {p.name: p.available for p in self.providers}

    async def chat(self, prompt: str,
                   system: Optional[str] = None,
                   history: Optional[List[ChatMessage]] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048) -> str:
        messages = list(history or []) + [ChatMessage(role="user", content=prompt)]
        errors = []
        for p in self.providers:
            if not p.available:
                continue
            try:
                log.info("AI router trying %s", p.name)
                return await p.chat(messages, system=system,
                                    temperature=temperature,
                                    max_tokens=max_tokens)
            except Exception as e:
                errors.append(f"{p.name}: {e}")
                continue
        raise ProviderError("All providers failed: " + " | ".join(errors))


_router: Optional[AIRouter] = None


def get_ai() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
''')

# ═══════════════════════════════════════════════════════════════
# 6) PROMPTS
# ═══════════════════════════════════════════════════════════════
w("app/prompts/system_prompt.py", r'''"""System prompts for AL-KHALLAQI."""
BRAND = "AL-KHALLAQI"
BRAND_AR = "الخلاقي"
DEVELOPER = "Hussein Ghallab"
SLOGAN = "الإبداع بلا حدود"

SYSTEM_PROMPT = f"""أنت {BRAND_AR} ({BRAND})، وكيل ذكاء اصطناعي إبداعي طوّره {DEVELOPER}.
شعارك: "{SLOGAN}".
أنت متخصص في:
- توليد الأفكار الإبداعية وتحليل الاتجاهات
- تصميم الهويات البصرية والشعارات
- كتابة المحتوى الإبداعي والسيناريوهات
- تخطيط المشاريع الرقمية

تحدّث بالعربية الفصحى المبسّطة. كن محدداً وعملياً.
عند طلب إبداعي: اقترح خطوات واضحة + ناتج قابل للتنفيذ.
"""

CREATIVE_SYSTEM = SYSTEM_PROMPT + """
أنت في وضع الإبداع الخالص. اكتب بجرأة، استخدم استعارات قوية، وابنِ صوراً بصرية غنية.
"""
''')

w("app/prompts/creative_prompts.py", r'''"""Creative prompt builders."""


def image_prompt(user_prompt: str, style: str = "realistic") -> str:
    style_map = {
        "realistic": "ultra-realistic, 8k, professional photography, sharp focus",
        "artistic": "digital art, painterly, expressive brushstrokes, artstation",
        "cyberpunk": "cyberpunk, neon lights, futuristic city, blade runner mood",
        "anime": "anime style, studio ghibli inspired, vivid colors, cel shading",
    }
    suffix = style_map.get(style, style_map["realistic"])
    return f"{user_prompt}, {suffix}, high detail, cinematic lighting"


def video_prompt(user_prompt: str) -> str:
    return f"{user_prompt}, cinematic, smooth motion, high quality"


def script_prompt(topic: str, tone: str = "creative", length: int = 500) -> str:
    return (f"اكتب سيناريو إبداعي عن: {topic}\n"
            f"النبرة: {tone}\nالطول التقريبي: {length} كلمة\n"
            f"قسّمه إلى: مشهد افتتاحي، تطوير، ذروة، خاتمة.")


def article_prompt(topic: str, tone: str = "creative", length: int = 500) -> str:
    return (f"اكتب مقالاً إبداعياً عن: {topic}\n"
            f"النبرة: {tone}\nعدد الكلمات: حوالي {length}\n"
            f"استخدم عناوين فرعية ونقاط عند الحاجة.")


def story_prompt(topic: str, tone: str = "creative", length: int = 500) -> str:
    return (f"اكتب قصة قصيرة عن: {topic}\nالنبرة: {tone}\n"
            f"الطول: ~{length} كلمة\nاجعل لها بداية مشوقة ونهاية مؤثرة.")
''')

w("app/prompts/agent_prompt.py", r'''"""ReAct agent prompt."""
from app.prompts.system_prompt import SYSTEM_PROMPT

AGENT_SYSTEM = SYSTEM_PROMPT + """
أنت الآن في وضع الوكيل (ReAct Agent). لديك أدوات:
- image_gen: توليد صورة
- image_edit: تعديل صورة
- video_gen: توليد فيديو قصير
- text_gen: توليد نص
- logo_design: تصميم شعار
- identity_design: بناء هوية بصرية كاملة
- search: بحث مرجعي
- apk_build: بناء تطبيق

صيغة الاستدعاء الإلزامية لكل خطوة:

Thought: <تفكير قصير>
Action: <اسم الأداة>
Action Input: <JSON صحيح {"key": "value"}>

عند الانتهاء:
Thought: انتهيت
Action: finish
Action Input: {"answer": "الإجابة النهائية"}

ابدأ دائماً بـ Thought. لا تكتب نصاً خارج الصيغة.
"""
''')

# ═══════════════════════════════════════════════════════════════
# 7) THINKING MODES + WEB SEARCH
# ═══════════════════════════════════════════════════════════════
w("app/services/thinking_modes.py", r'''"""Thinking modes."""
from typing import Dict

MODES: Dict[str, str] = {
    "creative": "فكّر بجرأة، اقترح أفكاراً غير تقليدية، استخدم الصور البلاغية.",
    "analytical": "حلّل المشكلة منطقياً، فكّك العناصر، ابنِ استنتاجك خطوة بخطوة.",
    "strategic": "فكّر على المدى البعيد، ضع خطة مرحلية، رتّب الأولويات.",
    "divergent": "ولّد أكبر عدد من الأفكار، لا تحكم عليها، ثم اختر الأفضل.",
    "critical": "افحص الفكرة من كل زاوية، ابحث عن نقاط الضعف، ثم اقترح تحسينات.",
}


def apply_mode(mode: str) -> str:
    return MODES.get(mode, MODES["creative"])
''')

w("app/services/web_search.py", r'''"""Lightweight web search via DuckDuckGo HTML."""
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
''')

# ═══════════════════════════════════════════════════════════════
# 8) CREATIVE SERVICES
# ═══════════════════════════════════════════════════════════════
w("app/services/creative/image_service.py", r'''"""Image generation & editing via Pollinations (free)."""
from typing import Dict, Optional
from urllib.parse import quote
import httpx
from app.core.logging import log
from app.prompts.creative_prompts import image_prompt


POLL_BASE = "https://image.pollinations.ai/prompt"


def _url(prompt: str, w: int, h: int, seed: Optional[int] = None,
         model: str = "flux") -> str:
    q = quote(prompt, safe="")
    params = f"?width={w}&height={h}&model={model}&nologo=true"
    if seed is not None:
        params += f"&seed={seed}"
    return f"{POLL_BASE}/{q}{params}"


async def generate(prompt: str, style: str = "realistic",
                   width: int = 1024, height: int = 1024,
                   seed: Optional[int] = None) -> Dict:
    full = image_prompt(prompt, style)
    url = _url(full, width, height, seed)
    try:
        async with httpx.AsyncClient(timeout=90.0) as c:
            r = await c.get(url)
            ok = r.status_code == 200 and len(r.content) > 1000
    except Exception as e:
        log.warning("image gen failed: %s", e)
        ok = False
    return {
        "url": url, "prompt": full, "style": style,
        "width": width, "height": height, "seed": seed, "ok": ok,
    }


async def edit(image_url: str, instruction: str) -> Dict:
    full = f"{instruction}, modify based on reference image"
    new_url = _url(full, 1024, 1024)
    return {"url": new_url, "instruction": instruction,
            "source": image_url, "prompt": full, "ok": True}
''')

w("app/services/creative/video_service.py", r'''"""Video generation: frames sequence -> GIF."""
import io
import base64
from typing import Dict
import httpx
from PIL import Image
from app.core.logging import log
from app.prompts.creative_prompts import video_prompt


SIZES = {"16:9": (768, 432), "9:16": (432, 768), "1:1": (512, 512)}


async def generate(prompt: str, duration: int = 4, aspect: str = "16:9",
                   frames: int = 12) -> Dict:
    w, h = SIZES.get(aspect, SIZES["16:9"])
    frames = max(4, min(frames, 24))
    base = video_prompt(prompt)
    from app.services.creative.image_service import _url

    urls = []
    images = []
    async with httpx.AsyncClient(timeout=90.0) as c:
        for i in range(frames):
            seed = 1000 + i * 7
            u = _url(f"{base}, frame {i+1}/{frames}", w, h, seed=seed)
            urls.append(u)
            try:
                r = await c.get(u)
                if r.status_code == 200:
                    images.append(Image.open(io.BytesIO(r.content)).convert("RGB"))
            except Exception as e:
                log.warning("frame %d failed: %s", i, e)

    gif_url = ""
    if images:
        buf = io.BytesIO()
        try:
            images[0].save(buf, format="GIF", save_all=True,
                           append_images=images[1:],
                           duration=int((duration * 1000) / len(images)),
                           loop=0)
            gif_url = "data:image/gif;base64," + base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            log.warning("gif build failed: %s", e)

    return {
        "prompt": base, "frames": urls, "gif": gif_url,
        "duration": duration, "aspect": aspect, "ok": bool(images),
    }
''')

w("app/services/creative/text_service.py", r'''"""Text generation via AI router."""
from app.prompts.creative_prompts import article_prompt, script_prompt, story_prompt
from app.prompts.system_prompt import CREATIVE_SYSTEM
from app.services.ai.router import get_ai


BUILDERS = {
    "article": article_prompt,
    "script": script_prompt,
    "story": story_prompt,
}


async def generate(prompt: str, kind: str = "article",
                   tone: str = "creative", length: int = 500) -> str:
    builder = BUILDERS.get(kind, article_prompt)
    full = builder(prompt, tone, length)
    return await get_ai().chat(full, system=CREATIVE_SYSTEM, temperature=0.9)
''')

w("app/services/creative/identity_service.py", r'''"""Identity design (colors + fonts + logo + tagline)."""
import json
from typing import Dict
from app.prompts.system_prompt import CREATIVE_SYSTEM
from app.services.ai.router import get_ai


async def design(brand: str, industry: str = "", mood: str = "modern") -> Dict:
    prompt = f"""صمّم هوية بصرية كاملة للعلامة التجارية: {brand}
المجال: {industry or "عام"}
المزاج: {mood}

أعد الإجابة بصيغة JSON فقط (بدون نص إضافي) بهذا الشكل:
{{
  "tagline": "شعار نصي قصير",
  "palette": ["#hex1", "#hex2", "#hex3", "#hex4"],
  "fonts": {{"headline": "اسم خط", "body": "اسم خط"}},
  "logo_concept": "وصف مفصل للشعار",
  "tone_of_voice": "وصف نبرة الصوت",
  "visual_keywords": ["كلمة1", "كلمة2", "كلمة3"]
}}
"""
    raw = await get_ai().chat(prompt, system=CREATIVE_SYSTEM, temperature=0.9)
    txt = raw.strip()
    if "```" in txt:
        txt = txt.split("```")[1]
        if txt.startswith("json"):
            txt = txt[4:]
    try:
        data = json.loads(txt)
    except Exception:
        data = {"raw": raw, "tagline": brand,
                "palette": ["#a855f7", "#22d3ee", "#fbbf24", "#f472b6"]}
    data["brand"] = brand
    data["industry"] = industry
    data["mood"] = mood
    return data


async def logo_svg(brand: str, industry: str = "", style: str = "modern",
                   colors: list = None) -> str:
    colors = colors or ["#a855f7", "#22d3ee", "#fbbf24"]
    initials = "".join([w[0] for w in brand.split()[:2]]).upper() or "AK"
    c1, c2, c3 = (colors + ["#a855f7", "#22d3ee", "#fbbf24"])[:3]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
<defs>
<linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="{c1}"/>
<stop offset="50%" stop-color="{c2}"/>
<stop offset="100%" stop-color="{c3}"/>
</linearGradient>
<filter id="glow"><feGaussianBlur stdDeviation="6" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="400" height="400" rx="60" fill="#0b0820"/>
<circle cx="200" cy="160" r="90" fill="url(#g1)" filter="url(#glow)" opacity="0.85"/>
<text x="200" y="190" font-family="Poppins,Arial,sans-serif" font-size="86" font-weight="900"
text-anchor="middle" fill="#ffffff">{initials}</text>
<text x="200" y="290" font-family="Poppins,Arial,sans-serif" font-size="34" font-weight="700"
text-anchor="middle" fill="url(#g1)">{brand}</text>
<text x="200" y="330" font-family="Poppins,Arial,sans-serif" font-size="16"
text-anchor="middle" fill="#c4b5fd" opacity="0.8">{industry or "CREATIVE AI"}</text>
</svg>"""
''')

w("app/services/storage.py", r'''"""Storage helpers (works persistence)."""
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
''')

# ═══════════════════════════════════════════════════════════════
# 9) AGENT + TOOLS
# ═══════════════════════════════════════════════════════════════
w("app/services/agent/tools/registry.py", r'''"""Tool registry."""
from typing import Any, Awaitable, Callable, Dict


TOOLS: Dict[str, Dict[str, Any]] = {}


def register(name: str, description: str,
             func: Callable[..., Awaitable[Any]]) -> None:
    TOOLS[name] = {"name": name, "description": description, "func": func}


def get_tool(name: str):
    return TOOLS.get(name)


def list_tools():
    return [{"name": t["name"], "description": t["description"]}
            for t in TOOLS.values()]


async def run_tool(name: str, **kwargs):
    t = get_tool(name)
    if not t:
        return {"error": f"unknown tool: {name}"}
    try:
        return await t["func"](**kwargs)
    except Exception as e:
        return {"error": f"{name} failed: {e}"}
''')

w("app/services/agent/tools/image_gen.py", r'''from app.services.agent.tools.registry import register
from app.services.creative import image_service


async def _run(prompt: str, style: str = "realistic",
               width: int = 1024, height: int = 1024, seed=None):
    return await image_service.generate(prompt, style, width, height, seed)


register("image_gen", "توليد صورة من وصف نصي.", _run)
''')

w("app/services/agent/tools/image_edit.py", r'''from app.services.agent.tools.registry import register
from app.services.creative import image_service


async def _run(image_url: str, instruction: str):
    return await image_service.edit(image_url, instruction)


register("image_edit", "تعديل صورة موجودة بناءً على وصف.", _run)
''')

w("app/services/agent/tools/video_gen.py", r'''from app.services.agent.tools.registry import register
from app.services.creative import video_service


async def _run(prompt: str, duration: int = 4, aspect: str = "16:9"):
    return await video_service.generate(prompt, duration, aspect)


register("video_gen", "توليد فيديو قصير (GIF) من وصف.", _run)
''')

w("app/services/agent/tools/text_gen.py", r'''from app.services.agent.tools.registry import register
from app.services.creative import text_service


async def _run(prompt: str, kind: str = "article",
               tone: str = "creative", length: int = 500):
    text = await text_service.generate(prompt, kind, tone, length)
    return {"text": text, "kind": kind}


register("text_gen", "توليد نص إبداعي (مقال/قصة/سيناريو).", _run)
''')

w("app/services/agent/tools/logo_design.py", r'''from app.services.agent.tools.registry import register
from app.services.creative.identity_service import logo_svg


async def _run(brand: str, industry: str = "",
               style: str = "modern", colors=None):
    svg = await logo_svg(brand, industry, style, colors or [])
    return {"svg": svg, "brand": brand}


register("logo_design", "تصميم شعار SVG.", _run)
''')

w("app/services/agent/tools/identity_design.py", r'''from app.services.agent.tools.registry import register
from app.services.creative import identity_service
from app.services.creative.identity_service import logo_svg


async def _run(brand: str, industry: str = "", mood: str = "modern"):
    data = await identity_service.design(brand, industry, mood)
    data["logo_svg"] = await logo_svg(brand, industry, "modern",
                                      data.get("palette", []))
    return data


register("identity_design", "بناء هوية بصرية كاملة.", _run)
''')

w("app/services/agent/tools/search.py", r'''from app.services.agent.tools.registry import register
from app.services import web_search


async def _run(query: str, limit: int = 5):
    return {"query": query, "results": await web_search.search(query, limit)}


register("search", "بحث مرجعي على الويب.", _run)
''')

w("app/services/agent/tools/apk_build.py", r'''from app.services.agent.tools.registry import register


async def _run(name: str, description: str = "", html: str = ""):
    return {
        "name": name, "status": "queued",
        "note": "APK build queued. GitHub Actions workflow required.",
        "html_len": len(html),
    }


register("apk_build", "بناء تطبيق APK.", _run)
''')

w("app/services/agent/core.py", r'''"""ReAct Agent Loop for AL-KHALLAQI."""
import json
import re
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.prompts.agent_prompt import AGENT_SYSTEM
from app.services.ai.base import ChatMessage
from app.services.ai.router import get_ai
from app.services.agent.tools.registry import list_tools, run_tool


RE_ACTION = re.compile(r"Action\s*:\s*([a-zA-Z_]+)", re.IGNORECASE)
RE_INPUT = re.compile(r"Action\s*Input\s*:\s*(\{.*?\})\s*(?:\n|$)",
                      re.IGNORECASE | re.DOTALL)
RE_THOUGHT = re.compile(r"Thought\s*:\s*(.+?)(?=\nAction|\Z)",
                        re.IGNORECASE | re.DOTALL)


def _parse(text: str) -> Dict[str, Any]:
    thought_m = RE_THOUGHT.search(text)
    action_m = RE_ACTION.search(text)
    input_m = RE_INPUT.search(text)
    thought = thought_m.group(1).strip() if thought_m else ""
    action = action_m.group(1).strip() if action_m else ""
    payload = {}
    if input_m:
        raw = input_m.group(1)
        try:
            payload = json.loads(raw)
        except Exception:
            try:
                payload = json.loads(raw.replace("'", '"'))
            except Exception:
                payload = {"_raw": raw}
    return {"thought": thought, "action": action, "input": payload}


async def run_agent(goal: str, session_id: str = "default",
                    max_steps: Optional[int] = None) -> Dict[str, Any]:
    steps_limit = max_steps or settings.MAX_AGENT_STEPS
    tools = list_tools()
    tools_desc = "\n".join(f"- {t['name']}: {t['description']}" for t in tools)

    system = AGENT_SYSTEM + f"\n\nالأدوات المتاحة:\n{tools_desc}"
    history: List[ChatMessage] = []
    steps: List[Dict[str, Any]] = []
    final_answer = ""
    success = False

    for i in range(1, steps_limit + 1):
        prompt = f"الهدف: {goal}\n\nاستمر في التفكير واستدعاء الأدوات."
        raw = await get_ai().chat(prompt, system=system,
                                  history=history, temperature=0.6)
        parsed = _parse(raw)
        step = {
            "step": i, "thought": parsed["thought"],
            "action": parsed["action"], "action_input": parsed["input"],
            "observation": "", "final": False,
        }

        if parsed["action"].lower() in ("finish", "final", "done"):
            final_answer = parsed["input"].get("answer", "") or parsed["thought"]
            step["final"] = True
            steps.append(step)
            success = True
            break

        if not parsed["action"]:
            steps.append(step)
            history.append(ChatMessage(role="assistant", content=raw))
            history.append(ChatMessage(
                role="user",
                content="لم أفهم الأداة. التزم بالصيغة: Thought/Action/Action Input."))
            continue

        obs = await run_tool(parsed["action"], **parsed["input"])
        obs_str = json.dumps(obs, ensure_ascii=False, default=str)
        if len(obs_str) > 1500:
            obs_str = obs_str[:1500] + "... [truncated]"
        step["observation"] = obs_str
        steps.append(step)

        history.append(ChatMessage(role="assistant", content=raw))
        history.append(ChatMessage(role="user",
                                   content=f"Observation: {obs_str}"))

    if not final_answer:
        final_answer = "أنجزت الخطوات المطلوبة. راجع النتائج أعلاه."
        success = len(steps) > 0

    return {"goal": goal, "steps": steps,
            "final_answer": final_answer, "success": success}
''')

# ═══════════════════════════════════════════════════════════════
# 10) REPOSITORIES
# ═══════════════════════════════════════════════════════════════
w("app/db/repositories/works.py", r'''from typing import Any, Dict, Optional
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
''')

w("app/db/repositories/projects.py", r'''from typing import Any, Dict
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
''')

w("app/db/repositories/chat.py", r'''from typing import Any, Dict, List
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
''')

# ═══════════════════════════════════════════════════════════════
# 11) API ENDPOINTS
# ═══════════════════════════════════════════════════════════════
w("app/api/v1/endpoints/system.py", r'''from fastapi import APIRouter
from app.core.config import settings
from app.services.ai.router import get_ai

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok", "app": settings.APP_NAME,
        "app_ar": settings.APP_NAME_AR, "version": settings.APP_VERSION,
        "developer": settings.DEVELOPER, "providers": get_ai().status(),
    }


@router.get("/")
async def root():
    return {
        "name": settings.APP_NAME, "name_ar": settings.APP_NAME_AR,
        "slogan": settings.SLOGAN, "version": settings.APP_VERSION,
    }
''')

w("app/api/v1/endpoints/creative.py", r'''from fastapi import APIRouter
from app.models.schemas import (
    ImageRequest, ImageEditRequest, VideoRequest, TextRequest,
)
from app.services.creative import image_service, video_service, text_service

router = APIRouter()


@router.post("/image")
async def gen_image(req: ImageRequest):
    return await image_service.generate(req.prompt, req.style,
                                        req.width, req.height, req.seed)


@router.post("/image/edit")
async def edit_image(req: ImageEditRequest):
    return await image_service.edit(req.image_url, req.instruction)


@router.post("/video")
async def gen_video(req: VideoRequest):
    return await video_service.generate(req.prompt, req.duration,
                                        req.aspect, req.frames)


@router.post("/text")
async def gen_text(req: TextRequest):
    text = await text_service.generate(req.prompt, req.kind,
                                       req.tone, req.length)
    return {"text": text, "kind": req.kind}
''')

w("app/api/v1/endpoints/studio.py", r'''from fastapi import APIRouter
from app.models.schemas import LogoRequest, IdentityRequest
from app.services.creative.identity_service import design, logo_svg

router = APIRouter()


@router.post("/logo")
async def make_logo(req: LogoRequest):
    svg = await logo_svg(req.brand, req.industry, req.style, req.colors)
    return {"brand": req.brand, "svg": svg}


@router.post("/identity")
async def make_identity(req: IdentityRequest):
    data = await design(req.brand, req.industry, req.mood)
    data["logo_svg"] = await logo_svg(req.brand, req.industry, "modern",
                                      data.get("palette", []))
    return data
''')

w("app/api/v1/endpoints/agent.py", r'''from fastapi import APIRouter
from app.models.schemas import AgentRequest
from app.services.agent.core import run_agent

router = APIRouter()


@router.post("/run")
async def run(req: AgentRequest):
    return await run_agent(req.goal, req.session_id, req.max_steps)
''')

w("app/api/v1/endpoints/chat.py", r'''from fastapi import APIRouter
from app.db.repositories import chat as chat_repo
from app.models.schemas import ChatRequest, ChatResponse
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.ai.base import ChatMessage
from app.services.ai.router import get_ai

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send(req: ChatRequest):
    history = await chat_repo.history(req.session_id, limit=20)
    await chat_repo.add(req.session_id, "user", req.message)
    msgs = [ChatMessage(role=h["role"], content=h["content"]) for h in history]
    reply = await get_ai().chat(req.message, system=SYSTEM_PROMPT,
                                history=msgs, temperature=0.85)
    await chat_repo.add(req.session_id, "assistant", reply)
    return ChatResponse(reply=reply, session_id=req.session_id)


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    return {"messages": await chat_repo.history(session_id)}
''')

w("app/api/v1/endpoints/gallery.py", r'''from fastapi import APIRouter, HTTPException
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
''')

w("app/api/v1/endpoints/admin.py", r'''from fastapi import APIRouter, Header, HTTPException
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
''')

w("app/api/v1/router.py", r'''from fastapi import APIRouter
from app.api.v1.endpoints import (
    system, creative, studio, agent, chat, gallery, admin,
)

api = APIRouter()
api.include_router(system.router, tags=["system"])
api.include_router(creative.router, prefix="/creative", tags=["creative"])
api.include_router(studio.router, prefix="/studio", tags=["studio"])
api.include_router(agent.router, prefix="/agent", tags=["agent"])
api.include_router(chat.router, prefix="/chat", tags=["chat"])
api.include_router(gallery.router, prefix="/gallery", tags=["gallery"])
api.include_router(admin.router, prefix="/admin", tags=["admin"])
''')

# ═══════════════════════════════════════════════════════════════
# 12) MAIN.PY
# ═══════════════════════════════════════════════════════════════
w("app/main.py", r'''"""AL-KHALLAQI — FastAPI entry."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.router import api
from app.core.config import settings
from app.core.exceptions import HKBaseError
from app.core.logging import log, setup_logging
from app.db.engine import dispose_engine, init_db
from app.db.redis import close_cache
from app.services.ai.router import get_ai
from app.services.agent.tools import (  # noqa: F401
    image_gen, image_edit, video_gen, text_gen,
    logo_design, identity_design, search, apk_build,
)


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging("DEBUG" if settings.DEBUG else "INFO")
    log.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    await init_db()
    log.info("AI providers: %s", get_ai().status())
    yield
    await close_cache()
    await dispose_engine()
    log.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=f"{settings.APP_NAME_AR} — {settings.SLOGAN}",
    lifespan=lifespan,
)
app.include_router(api, prefix="/api/v1")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.exception_handler(HKBaseError)
async def hk_err(request: Request, exc: HKBaseError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})


def _render(name: str, request: Request, **kw):
    try:
        return templates.TemplateResponse(
            name, {"request": request, "settings": settings, **kw})
    except Exception as e:
        log.warning("template %s missing: %s", name, e)
        return HTMLResponse(
            f"<h1>{settings.APP_NAME}</h1><p>Template {name} not ready.</p>")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return _render("choice.html", request)


@app.get("/creative", response_class=HTMLResponse)
async def creative_ui(request: Request):
    return _render("creative.html", request)


@app.get("/studio", response_class=HTMLResponse)
async def studio_ui(request: Request):
    return _render("studio.html", request)


@app.get("/gallery", response_class=HTMLResponse)
async def gallery_ui(request: Request):
    return _render("gallery.html", request)


@app.get("/work/{wid}", response_class=HTMLResponse)
async def work_view(wid: int, request: Request):
    return _render("work_view.html", request, work_id=wid)


@app.get("/admin", response_class=HTMLResponse)
async def admin_ui(request: Request):
    return _render("admin.html", request)


@app.get("/manifest.json")
async def manifest():
    return RedirectResponse("/static/manifest.json")
''')

# ═══════════════════════════════════════════════════════════════
# 13) FRONTEND — CSS + HTML
# ═══════════════════════════════════════════════════════════════
w("static/css/main.css", r'''/* AL-KHALLAQI — crystal theme */
* { margin: 0; padding: 0; box-sizing: border-box; }
:root{
  --p1:#a855f7; --p2:#c084fc; --p3:#7c3aed;
  --c1:#22d3ee; --c2:#67e8f9; --c3:#06b6d4;
  --g1:#fbbf24; --g2:#fde68a; --g3:#f59e0b;
  --r1:#f472b6; --r2:#fb7185; --r3:#ec4899;
  --bg0:#05030f; --bg1:#0b0820; --bg2:#1e1b4b; --bg3:#312e81;
  --text:#f5f3ff; --muted:#c4b5fd;
  --glass:rgba(30,27,75,0.45);
  --border:rgba(168,85,247,0.35);
}
html,body{height:100%;}
body{
  font-family:'Poppins','Segoe UI',system-ui,sans-serif;
  background:var(--bg0); color:var(--text); overflow-x:hidden;
  min-height:100vh; position:relative;
}
body::before{
  content:""; position:fixed; inset:-20%; z-index:-2;
  background:
    radial-gradient(circle at 20% 20%, rgba(168,85,247,0.30), transparent 45%),
    radial-gradient(circle at 80% 30%, rgba(34,211,238,0.25), transparent 45%),
    radial-gradient(circle at 50% 80%, rgba(244,114,182,0.22), transparent 50%),
    radial-gradient(circle at 90% 90%, rgba(251,191,36,0.18), transparent 45%);
  filter:blur(60px); animation:aurora 18s ease-in-out infinite alternate;
}
body::after{
  content:""; position:fixed; inset:0; z-index:-1;
  background-image:
    linear-gradient(rgba(168,85,247,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34,211,238,0.06) 1px, transparent 1px);
  background-size:44px 44px;
  mask-image:radial-gradient(circle at center, black, transparent 80%);
}
@keyframes aurora{
  0%{transform:translate(0,0) scale(1)}
  50%{transform:translate(3%, -2%) scale(1.08)}
  100%{transform:translate(-2%, 2%) scale(1.02)}
}
.glass{
  background:var(--glass);
  backdrop-filter:blur(18px) saturate(160%);
  -webkit-backdrop-filter:blur(18px) saturate(160%);
  border:1px solid var(--border);
  border-radius:20px;
  box-shadow:0 8px 40px rgba(168,85,247,0.15), inset 0 1px 0 rgba(255,255,255,0.08);
}
.btn{
  position:relative; display:inline-flex; align-items:center; justify-content:center;
  gap:8px; padding:12px 22px; border-radius:14px; border:1px solid var(--border);
  background:linear-gradient(135deg, var(--p3), var(--c3));
  color:#fff; font-weight:700; cursor:pointer; overflow:hidden;
  transition:transform .25s cubic-bezier(.2,.8,.2,1), box-shadow .25s;
  box-shadow:0 4px 20px rgba(168,85,247,0.4);
  font-family:inherit; font-size:15px;
}
.btn:hover{transform:translateY(-2px); box-shadow:0 8px 30px rgba(168,85,247,0.7);}
.btn::after{
  content:""; position:absolute; inset:0;
  background:linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.35) 50%, transparent 70%);
  transform:translateX(-100%); transition:transform .6s;
}
.btn:hover::after{transform:translateX(100%);}
.input, textarea, select{
  width:100%; padding:12px 14px; border-radius:12px;
  background:rgba(11,8,32,0.6); border:1px solid var(--border);
  color:var(--text); font-family:inherit; font-size:15px; outline:none;
  transition:border-color .2s, box-shadow .2s;
}
.input:focus, textarea:focus, select:focus{
  border-color:var(--c1); box-shadow:0 0 0 3px rgba(34,211,238,0.18);
}
.topbar{
  position:sticky; top:0; z-index:20; padding:14px 20px;
  display:flex; align-items:center; justify-content:space-between;
  background:rgba(5,3,15,0.65); backdrop-filter:blur(16px);
  border-bottom:1px solid var(--border);
}
.brand{
  font-weight:900; font-size:20px; letter-spacing:1px;
  background:linear-gradient(90deg, var(--p1), var(--c1), var(--g1), var(--r1));
  background-size:300% 100%; -webkit-background-clip:text; background-clip:text;
  color:transparent; animation:shine 6s linear infinite;
}
@keyframes shine{0%{background-position:0% 50%}100%{background-position:300% 50%}}
.muted{color:var(--muted);}
.grid{display:grid; gap:16px;}
.g2{grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));}
.g3{grid-template-columns:repeat(auto-fill, minmax(160px, 1fr));}
.pulse{animation:pulse 2s ease-in-out infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.85;transform:scale(1.03)}}
.chip{
  display:inline-block; padding:5px 12px; border-radius:999px;
  background:rgba(168,85,247,0.15); border:1px solid var(--border);
  color:var(--muted); font-size:12px;
}
''')

# choice.html
w("templates/choice.html", r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الخلاقي</title>
<link rel="manifest" href="/static/manifest.json">
<link rel="stylesheet" href="/static/css/main.css">
<style>
.splash{position:fixed;inset:0;background:#000;display:flex;align-items:center;justify-content:center;z-index:100;transition:opacity .8s;}
.splash.hide{opacity:0;pointer-events:none;}
#crystal{position:fixed;inset:0;z-index:101;pointer-events:none;}
.hero{position:relative;z-index:2;text-align:center;padding:80px 20px 40px;}
.hero h1{
  font-size:clamp(38px,8vw,90px); font-weight:900; letter-spacing:4px;
  background:linear-gradient(90deg,var(--p1),var(--c1),var(--g1),var(--r1));
  background-size:300% 100%;-webkit-background-clip:text;background-clip:text;
  color:transparent;animation:shine 5s linear infinite;
  filter:drop-shadow(0 0 24px rgba(168,85,247,0.6));
}
.hero p{margin-top:14px;color:var(--muted);font-size:18px;}
.cards{max-width:1100px;margin:40px auto;padding:0 20px;display:grid;gap:20px;
       grid-template-columns:repeat(auto-fit,minmax(240px,1fr));}
.card{padding:26px;border-radius:22px;text-decoration:none;color:var(--text);
      background:var(--glass);backdrop-filter:blur(18px);
      border:1px solid var(--border);position:relative;overflow:hidden;
      transition:transform .3s cubic-bezier(.2,.8,.2,1),box-shadow .3s;}
.card:hover{transform:translateY(-6px);box-shadow:0 16px 50px rgba(168,85,247,0.35);}
.card::before{
  content:"";position:absolute;inset:-2px;border-radius:22px;
  background:conic-gradient(from 0deg,var(--p1),var(--c1),var(--g1),var(--r1),var(--p1));
  opacity:0;transition:opacity .4s;z-index:-1;filter:blur(14px);
}
.card:hover::before{opacity:.6;}
.card .icon{font-size:34px;margin-bottom:12px;}
.card h3{font-size:20px;margin-bottom:6px;}
.card p{color:var(--muted);font-size:14px;line-height:1.6;}
.foot{text-align:center;padding:40px 20px;color:var(--muted);font-size:13px;}
</style>
</head>
<body>
<div class="splash" id="splash"><canvas id="crystal"></canvas></div>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">الإبداع بلا حدود</span>
</div>
<div class="hero">
  <h1>AL-KHALLAQI</h1>
  <p>وكيل الذكاء الاصطناعي الإبداعي — طوّره Hussein Ghallab</p>
</div>
<div class="cards">
  <a class="card" href="/creative"><div class="icon">✨</div><h3>الواجهة الإبداعية</h3><p>تحدّث مع الوكيل الذكي واطلب أفكاراً إبداعية.</p></a>
  <a class="card" href="/studio"><div class="icon">🎨</div><h3>استوديو الإبداع</h3><p>صور، فيديو، نصوص، شعارات، هويات بصرية.</p></a>
  <a class="card" href="/gallery"><div class="icon">🖼️</div><h3>معرض الأعمال</h3><p>تصفّح كل ما أنشأته واحفظه وشاركه.</p></a>
  <a class="card" href="/admin"><div class="icon">⚙️</div><h3>لوحة الإدارة</h3><p>إحصائيات ومزودو الذكاء الاصطناعي.</p></a>
  <a class="card" href="/docs"><div class="icon">📚</div><h3>توثيق API</h3><p>كل المسارات المتاحة مع أمثلة تفاعلية.</p></a>
  <a class="card" href="/api/v1/health"><div class="icon">💚</div><h3>الحالة</h3><p>تحقق من صحة النظام والمزودين.</p></a>
</div>
<div class="foot">© 2026 Hussein Ghallab — AL-KHALLAQI v1.0</div>

<script>
(function(){
  const splash=document.getElementById('splash');
  const cv=document.getElementById('crystal');
  const ctx=cv.getContext('2d');
  let W,H;
  function fit(){W=cv.width=innerWidth;H=cv.height=innerHeight;}
  fit();addEventListener('resize',fit);
  const COLORS=['#a855f7','#22d3ee','#fbbf24','#f472b6','#c084fc','#67e8f9'];
  const N=140;
  const parts=[];
  for(let i=0;i<N;i++){
    parts.push({
      x:Math.random()*W, y:-Math.random()*H,
      vy:0.6+Math.random()*1.8, vx:(Math.random()-0.5)*0.6,
      r:1+Math.random()*2.4, c:COLORS[(Math.random()*COLORS.length)|0],
      a:0.4+Math.random()*0.6
    });
  }
  let t=0;
  function loop(){
    t++;
    ctx.fillStyle='rgba(0,0,0,0.18)';
    ctx.fillRect(0,0,W,H);
    for(const p of parts){
      p.y+=p.vy; p.x+=p.vx;
      if(p.y>H+10){p.y=-10;p.x=Math.random()*W;}
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=p.c;
      ctx.globalAlpha=p.a;
      ctx.shadowBlur=14; ctx.shadowColor=p.c;
      ctx.fill();
      ctx.globalAlpha=1; ctx.shadowBlur=0;
    }
    if(t<220){requestAnimationFrame(loop);}
    else{setTimeout(()=>splash.classList.add('hide'),200);}
  }
  loop();
})();
</script>
</body>
</html>
''')

# creative.html
w("templates/creative.html", r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الواجهة الإبداعية</title>
<link rel="manifest" href="/static/manifest.json">
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:900px;margin:0 auto;padding:20px;}
.toolbar{display:flex;gap:8px;overflow-x:auto;padding:12px 0;scrollbar-width:none;}
.toolbar::-webkit-scrollbar{display:none;}
.tool{padding:9px 16px;border-radius:12px;border:1px solid var(--border);
      background:rgba(11,8,32,0.5);color:var(--muted);cursor:pointer;
      white-space:nowrap;font-weight:600;font-size:14px;transition:.2s;}
.tool.active,.tool:hover{background:linear-gradient(135deg,var(--p3),var(--c3));
                          color:#fff;border-color:transparent;}
.chat{display:flex;flex-direction:column;gap:14px;margin:18px 0;min-height:50vh;}
.msg{padding:14px 18px;border-radius:18px;max-width:85%;line-height:1.7;
     animation:rise .35s cubic-bezier(.2,.8,.2,1);word-wrap:break-word;}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.msg.user{align-self:flex-start;background:linear-gradient(135deg,var(--p3),var(--c3));
          color:#fff;box-shadow:0 6px 24px rgba(168,85,247,0.35);}
.msg.bot{align-self:flex-end;background:rgba(30,27,75,0.6);border:1px solid var(--border);
         backdrop-filter:blur(14px);}
.msg img,.msg svg{max-width:100%;border-radius:14px;margin-top:8px;display:block;}
.composer{position:sticky;bottom:0;padding:14px 0;background:linear-gradient(to top,
  rgba(5,3,15,0.95),transparent);}
.composer-inner{display:flex;gap:10px;align-items:flex-end;}
textarea#inp{resize:none;min-height:52px;max-height:200px;line-height:1.5;}
.send{width:52px;height:52px;border-radius:50%;padding:0;font-size:22px;}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">وضع إبداعي</span>
</div>
<div class="wrap">
  <div class="toolbar" id="tools">
    <div class="tool active" data-t="image">🖼️ صور</div>
    <div class="tool" data-t="video">🎬 فيديو</div>
    <div class="tool" data-t="text">✍️ نصوص</div>
    <div class="tool" data-t="logo">🎯 شعار</div>
    <div class="tool" data-t="identity">🌈 هوية</div>
    <div class="tool" data-t="agent">🧠 وكيل</div>
  </div>
  <div class="chat" id="chat">
    <div class="msg bot">أهلاً بك في <b>AL-KHALLAQI</b> ✨<br>اختر أداة وابدأ الإبداع. اكتب فكرتك وسأحوّلها إلى واقع.</div>
  </div>
  <div class="composer">
    <div class="composer-inner">
      <textarea id="inp" placeholder="اكتب فكرتك... مثلاً: هوية بصرية لمقهى عربي مستقبلي"></textarea>
      <button class="btn send" id="send">➤</button>
    </div>
  </div>
</div>
<script>
const chat=document.getElementById('chat');
const inp=document.getElementById('inp');
const send=document.getElementById('send');
let currentTool='image';

document.querySelectorAll('.tool').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tool').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    currentTool=t.dataset.t;
    inp.placeholder={
      image:'صف الصورة التي تريدها...',
      video:'صف الفيديو القصير...',
      text:'اكتب موضوع المقال أو القصة...',
      logo:'اسم العلامة التجارية...',
      identity:'اسم المشروع والمجال...',
      agent:'اكتب هدفاً كاملاً وسيخططه الوكيل...'
    }[currentTool]||'اكتب...';
  });
});

function addMsg(cls,html){
  const d=document.createElement('div');
  d.className='msg '+cls;
  d.innerHTML=html;
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
  return d;
}

inp.addEventListener('input',()=>{
  inp.style.height='auto';
  inp.style.height=Math.min(inp.scrollHeight,200)+'px';
});
inp.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();doSend();}
});

async function api(path,body){
  const r=await fetch('/api/v1'+path,{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}

async function doSend(){
  const v=inp.value.trim();
  if(!v) return;
  inp.value=''; inp.style.height='52px';
  addMsg('user', v);
  const bot=addMsg('bot','<span class="pulse">⏳ يفكر...</span>');
  try{
    if(currentTool==='image'){
      const d=await api('/creative/image',{prompt:v});
      bot.innerHTML='<b>🖼️ صورة مولّدة</b><br><span class="muted">'+d.prompt+'</span>'
        +'<img src="'+d.url+'" alt=""/>';
    } else if(currentTool==='video'){
      const d=await api('/creative/video',{prompt:v});
      bot.innerHTML='<b>🎬 فيديو قصير</b>';
      if(d.gif){const img=document.createElement('img');img.src=d.gif;bot.appendChild(img);}
      else bot.innerHTML+='<br>'+d.frames.map(u=>'<img src="'+u+'"/>').join('');
    } else if(currentTool==='text'){
      const d=await api('/creative/text',{prompt:v,kind:'article'});
      bot.innerHTML='<b>✍️ نص مولّد</b><br>'+d.text.replace(/\n/g,'<br>');
    } else if(currentTool==='logo'){
      const d=await api('/studio/logo',{brand:v});
      bot.innerHTML='<b>🎯 شعار</b><br>'+d.svg;
    } else if(currentTool==='identity'){
      const d=await api('/studio/identity',{brand:v});
      const pal=(d.palette||[]).map(c=>'<span style="display:inline-block;width:26px;height:26px;border-radius:6px;background:'+c+';margin:2px;"></span>').join('');
      bot.innerHTML='<b>🌈 هوية بصرية</b><br>'
        +'<b>'+d.brand+'</b><br><i>'+(d.tagline||'')+'</i><br>'+pal
        +'<br>'+(d.logo_svg||'');
    } else if(currentTool==='agent'){
      const d=await api('/agent/run',{goal:v,max_steps:6});
      let html='<b>🧠 نتيجة الوكيل</b><br>';
      (d.steps||[]).forEach(s=>{
        html+='<div style="margin:8px 0;padding:8px;border-left:3px solid var(--p1);background:rgba(168,85,247,0.08);border-radius:8px;">'
          +'<b>خطوة '+s.step+'</b> — <span class="muted">'+s.action+'</span><br>'
          +'<span>'+s.thought+'</span></div>';
      });
      html+='<hr style="border-color:var(--border);margin:10px 0"><b>الإجابة:</b><br>'+d.final_answer;
      bot.innerHTML=html;
    }
  }catch(e){
    bot.innerHTML='<b style="color:#f87171">خطأ</b><br>'+e.message;
  }
  chat.scrollTop=chat.scrollHeight;
}
send.addEventListener('click',doSend);
</script>
</body>
</html>
''')

# studio.html
w("templates/studio.html", r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — استوديو الإبداع</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:1100px;margin:0 auto;padding:20px;}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;}
.tab{padding:10px 18px;border-radius:12px;border:1px solid var(--border);
     background:rgba(11,8,32,0.5);color:var(--muted);cursor:pointer;font-weight:600;}
.tab.active{background:linear-gradient(135deg,var(--p3),var(--c3));color:#fff;border-color:transparent;}
.panel{display:none;padding:24px;}
.panel.active{display:block;}
.row{display:grid;gap:12px;grid-template-columns:1fr 1fr;margin-bottom:12px;}
.row.full{grid-template-columns:1fr;}
.preview{margin-top:20px;min-height:200px;padding:16px;border-radius:16px;
         background:rgba(11,8,32,0.5);border:1px dashed var(--border);}
.preview img,.preview svg{max-width:100%;border-radius:12px;}
</style>
</head>
<body>
<div class="topbar"><span class="brand">AL-KHALLAQI</span><span class="chip">الاستوديو</span></div>
<div class="wrap">
  <div class="tabs">
    <div class="tab active" data-p="images">🖼️ صور</div>
    <div class="tab" data-p="video">🎬 فيديو</div>
    <div class="tab" data-p="text">✍️ نصوص</div>
    <div class="tab" data-p="identity">🌈 هويات</div>
  </div>

  <div class="glass panel active" id="images">
    <h3>توليد صورة</h3><br>
    <div class="row full"><textarea class="input" id="imgPrompt" rows="3" placeholder="صف الصورة..."></textarea></div>
    <div class="row">
      <select class="input" id="imgStyle">
        <option value="realistic">واقعي</option>
        <option value="artistic">فني</option>
        <option value="cyberpunk">سايبربانك</option>
        <option value="anime">أنمي</option>
      </select>
      <select class="input" id="imgSize">
        <option value="1024x1024">1024 × 1024</option>
        <option value="768x768">768 × 768</option>
        <option value="1344x768">1344 × 768</option>
        <option value="768x1344">768 × 1344</option>
      </select>
    </div>
    <button class="btn" onclick="genImage()">✨ توليد</button>
    <div class="preview" id="imgPrev">النتيجة ستظهر هنا...</div>
  </div>

  <div class="glass panel" id="video">
    <h3>توليد فيديو</h3><br>
    <div class="row full"><textarea class="input" id="vidPrompt" rows="3" placeholder="صف الفيديو..."></textarea></div>
    <div class="row">
      <select class="input" id="vidAspect">
        <option value="16:9">16:9</option><option value="9:16">9:16</option><option value="1:1">1:1</option>
      </select>
      <input class="input" id="vidDur" type="number" value="4" min="2" max="10" placeholder="مدة بالثواني">
    </div>
    <button class="btn" onclick="genVideo()">🎬 توليد</button>
    <div class="preview" id="vidPrev">النتيجة ستظهر هنا...</div>
  </div>

  <div class="glass panel" id="text">
    <h3>توليد نص</h3><br>
    <div class="row full"><textarea class="input" id="txtPrompt" rows="3" placeholder="الموضوع..."></textarea></div>
    <div class="row">
      <select class="input" id="txtKind">
        <option value="article">مقال</option>
        <option value="story">قصة</option>
        <option value="script">سيناريو</option>
      </select>
      <select class="input" id="txtTone">
        <option value="creative">إبداعي</option>
        <option value="formal">رسمي</option>
        <option value="fun">مرح</option>
      </select>
    </div>
    <button class="btn" onclick="genText()">✍️ توليد</button>
    <div class="preview" id="txtPrev">النتيجة ستظهر هنا...</div>
  </div>

  <div class="glass panel" id="identity">
    <h3>بناء هوية بصرية</h3><br>
    <div class="row">
      <input class="input" id="idBrand" placeholder="اسم العلامة التجارية">
      <input class="input" id="idIndustry" placeholder="المجال (اختياري)">
    </div>
    <button class="btn" onclick="genIdentity()">🌈 بناء</button>
    <div class="preview" id="idPrev">النتيجة ستظهر هنا...</div>
  </div>
</div>
<script>
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.p).classList.add('active');
  });
});
async function post(path,body){
  const r=await fetch('/api/v1'+path,{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
async function genImage(){
  const p=document.getElementById('imgPrompt').value.trim(); if(!p) return;
  const s=document.getElementById('imgStyle').value;
  const [w,h]=document.getElementById('imgSize').value.split('x').map(Number);
  const prev=document.getElementById('imgPrev');
  prev.textContent='⏳ جارٍ التوليد...';
  try{
    const d=await post('/creative/image',{prompt:p,style:s,width:w,height:h});
    prev.innerHTML='<img src="'+d.url+'"/>';
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genVideo(){
  const p=document.getElementById('vidPrompt').value.trim(); if(!p) return;
  const prev=document.getElementById('vidPrev');
  prev.textContent='⏳ جارٍ التوليد... (قد يستغرق دقيقة)';
  try{
    const d=await post('/creative/video',{
      prompt:p,aspect:document.getElementById('vidAspect').value,
      duration:Number(document.getElementById('vidDur').value)||4});
    if(d.gif){prev.innerHTML='<img src="'+d.gif+'"/>';}
    else{prev.innerHTML=d.frames.map(u=>'<img style="max-width:180px;margin:4px" src="'+u+'"/>').join('');}
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genText(){
  const p=document.getElementById('txtPrompt').value.trim(); if(!p) return;
  const prev=document.getElementById('txtPrev');
  prev.textContent='⏳ جارٍ الكتابة...';
  try{
    const d=await post('/creative/text',{prompt:p,
      kind:document.getElementById('txtKind').value,
      tone:document.getElementById('txtTone').value});
    prev.innerHTML=d.text.replace(/\n/g,'<br>');
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genIdentity(){
  const b=document.getElementById('idBrand').value.trim(); if(!b) return;
  const prev=document.getElementById('idPrev');
  prev.textContent='⏳ جارٍ البناء...';
  try{
    const d=await post('/studio/identity',{brand:b,
      industry:document.getElementById('idIndustry').value});
    const pal=(d.palette||[]).map(c=>'<span style="display:inline-block;width:32px;height:32px;border-radius:8px;background:'+c+';margin:3px;"></span>').join('');
    prev.innerHTML='<b>'+d.brand+'</b><br><i>'+(d.tagline||'')+'</i><br>'
      +'<div style="margin:10px 0">'+pal+'</div>'+(d.logo_svg||'');
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
</script>
</body>
</html>
''')

# gallery.html
w("templates/gallery.html", r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — المعرض</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:1100px;margin:0 auto;padding:20px;}
.cardwork{padding:14px;border-radius:18px;background:var(--glass);
          border:1px solid var(--border);transition:.3s;cursor:pointer;}
.cardwork:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(168,85,247,0.3);}
.cardwork .kind{font-size:11px;color:var(--muted);text-transform:uppercase;}
.cardwork h4{margin:8px 0 4px;}
.empty{padding:60px 20px;text-align:center;color:var(--muted);}
</style></head>
<body>
<div class="topbar"><span class="brand">AL-KHALLAQI</span><span class="chip">المعرض</span></div>
<div class="wrap">
  <h2 style="margin-bottom:16px;">🖼️ معرض الأعمال</h2>
  <div class="grid g2" id="grid"></div>
  <div class="empty" id="empty" style="display:none;">لا توجد أعمال بعد. ابدأ من <a href="/studio" style="color:var(--c1)">الاستوديو</a>.</div>
</div>
<script>
(async()=>{
  const r=await fetch('/api/v1/gallery/works?limit=100');
  const d=await r.json();
  const grid=document.getElementById('grid');
  if(!d.works||!d.works.length){document.getElementById('empty').style.display='block';return;}
  d.works.forEach(w=>{
    const a=document.createElement('a');
    a.href='/work/'+w.id;
    a.style.textDecoration='none'; a.style.color='inherit';
    a.className='cardwork';
    a.innerHTML='<div class="kind">'+w.kind+'</div>'
      +'<h4>'+w.title+'</h4>'
      +'<div class="muted" style="font-size:12px">'+(w.created_at||'').split('T')[0]+'</div>';
    grid.appendChild(a);
  });
})();
</script>
</body></html>
''')

# work_view.html
w("templates/work_view.html", r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — عرض العمل</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:900px;margin:0 auto;padding:24px;}
.body{padding:24px;border-radius:20px;background:var(--glass);border:1px solid var(--border);}
.body img,.body svg{max-width:100%;border-radius:14px;display:block;margin:12px 0;}
.actions{display:flex;gap:10px;margin-top:20px;}
</style></head>
<body>
<div class="topbar"><span class="brand">AL-KHALLAQI</span><span class="chip">عرض عمل</span></div>
<div class="wrap">
  <div class="body" id="body">⏳ جارٍ التحميل...</div>
  <div class="actions" id="actions"></div>
</div>
<script>
const wid=location.pathname.split('/').pop();
(async()=>{
  const r=await fetch('/api/v1/gallery/works/'+wid);
  if(!r.ok){document.getElementById('body').textContent='غير موجود';return;}
  const w=await r.json();
  const b=document.getElementById('body');
  let html='<h2>'+w.title+'</h2>'
    +'<div class="chip" style="margin:8px 0">'+w.kind+'</div>';
  if(w.prompt) html+='<p class="muted">'+w.prompt+'</p>';
  if(w.content) html+='<div>'+w.content+'</div>';
  const ex=w.extra||{};
  if(ex.url) html+='<img src="'+ex.url+'"/>';
  if(ex.svg) html+=ex.svg;
  if(ex.text) html+='<div>'+ex.text.replace(/\n/g,'<br>')+'</div>';
  b.innerHTML=html;
  document.getElementById('actions').innerHTML=
    '<button class="btn" onclick="history.back()">↩ رجوع</button>';
})();
</script>
</body></html>
''')

# admin.html
w("templates/admin.html", r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الإدارة</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>.wrap{max-width:900px;margin:0 auto;padding:24px;}
.stat{padding:20px;border-radius:16px;background:var(--glass);border:1px solid var(--border);}
.stat b{font-size:32px;display:block;background:linear-gradient(90deg,var(--p1),var(--c1));
        -webkit-background-clip:text;background-clip:text;color:transparent;}</style>
</head><body>
<div class="topbar"><span class="brand">AL-KHALLAQI</span><span class="chip">الإدارة</span></div>
<div class="wrap">
  <h2 style="margin-bottom:16px;">⚙️ لوحة الإدارة</h2>
  <div style="display:flex;gap:12px;margin-bottom:20px;">
    <input class="input" id="pwd" type="password" placeholder="كلمة المرور">
    <button class="btn" onclick="load()">دخول</button>
  </div>
  <div class="grid g2" id="stats"></div>
</div>
<script>
async function load(){
  const p=document.getElementById('pwd').value;
  const r=await fetch('/api/v1/admin/stats',{headers:{'X-Admin-Password':p}});
  const out=document.getElementById('stats');
  if(!r.ok){out.innerHTML='<div class="stat">كلمة مرور خاطئة</div>';return;}
  const d=await r.json();
  out.innerHTML=
    '<div class="stat"><b>'+d.total_works+'</b>إجمالي الأعمال</div>'
    +'<div class="stat"><b>'+Object.keys(d.providers||{}).length+'</b>مزودو الذكاء</div>'
    +Object.entries(d.providers||{}).map(([k,v])=>
      '<div class="stat"><b>'+(v?'✅':'❌')+'</b>'+k+'</div>').join('')
    +Object.entries(d.by_kind||{}).map(([k,v])=>
      '<div class="stat"><b>'+v+'</b>'+k+'</div>').join('');
}
</script>
</body></html>
''')

# manifest.json
w("static/manifest.json", r'''{
  "name": "AL-KHALLAQI — وكيل الذكاء الاصطناعي الإبداعي",
  "short_name": "AL-KHALLAQI",
  "description": "الإبداع بلا حدود — Hussein Ghallab",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#05030f",
  "theme_color": "#a855f7",
  "orientation": "portrait",
  "icons": []
}
''')

# ═══════════════════════════════════════════════════════════════
# 14) ROOT FILES
# ═══════════════════════════════════════════════════════════════
w("requirements.txt", """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
httpx>=0.26.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
sqlalchemy[asyncio]>=2.0.25
greenlet>=3.0.0
aiosqlite>=0.19.0
asyncpg>=0.29.0
redis>=5.0.1
jinja2>=3.1.3
python-multipart>=0.0.6
python-dotenv>=1.0.0
Pillow>=10.0.0
""")

w(".python-version", "3.11.9\n")

w(".env.example", """# AL-KHALLAQI — environment variables
APP_VERSION=1.0.0
GEMINI_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
DEEPSEEK_API_KEY=
GITHUB_ACTIONS_TOKEN=
TELEGRAM_BOT_TOKEN=
ADMIN_PASSWORD=hussein2026
DATABASE_URL=
REDIS_URL=redis://localhost:6379/0
DEBUG=false
""")

w("render.yaml", """services:
  - type: web
    name: al-khallaqi
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: APP_VERSION
        value: 1.0.0
      - key: GEMINI_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: OPENROUTER_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
""")

w(".gitignore", """__pycache__/
*.py[cod]
*.egg-info/
.env
.venv/
venv/
*.db
*.sqlite
.pytest_cache/
.DS_Store
dist/
build/
*.apk
""")

w("README.md", r'''# AL-KHALLAQI — وكيل الذكاء الاصطناعي الإبداعي

> **الإبداع بلا حدود**

مطوّره: **Hussein Ghallab**

## المزايا

- وكيل ReAct حقيقي بأدوات فعلية
- توليد صور / فيديو / شعارات / هويات بصرية
- توليد نصوص إبداعية وسيناريوهات
- بحث مرجعي
- بناء APK (GitHub Actions)
- 4 مزودي ذكاء مع fallback تلقائي

## التشغيل المحلي

    pip install -r requirements.txt
    cp .env.example .env
    uvicorn app.main:app --reload --port 8000

## النشر على Render

1. ارفع المشروع إلى GitHub
2. Render -> New Web Service -> اختر الريبو
3. Build Command: pip install -r requirements.txt
4. Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

## المسارات

- /          شاشة الاختيار
- /creative  الواجهة الإبداعية
- /studio    الاستوديو
- /gallery   المعرض
- /admin     الإدارة
- /docs      توثيق API
''')


def main():
    print("=" * 62)
    print("AL-KHALLAQI - Single Install")
    print("Hussein Ghallab Creative AI Agent")
    print("=" * 62)
    print()
    print("Folder:", BASE)
    print()
    print("-" * 62)
    print(f"Created {len(CREATED)} files")
    print("-" * 62)
    print()
    print("Next steps:")
    print("  pip install -r requirements.txt")
    print("  cp .env.example .env && nano .env")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print()
    print("To push to GitHub:")
    print("  git init -b main")
    print('  git config user.name  "Hussein Ghallab"')
    print('  git config user.email "alwaqyhsyn752-eng@users.noreply.github.com"')
    print("  git add .")
    print('  git commit -m "AL-KHALLAQI v1.0"')
    print("  git remote add origin https://github.com/alwaqyhsyn752-eng/al-khallaqi.git")
    print("  git push -u origin main")


if __name__ == "__main__":
    main()
