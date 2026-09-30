from fastapi import APIRouter
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
