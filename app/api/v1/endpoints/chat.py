from fastapi import APIRouter
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
