"""AL-KHALLAQI — FastAPI entry."""
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
