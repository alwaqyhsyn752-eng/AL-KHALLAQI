from fastapi import APIRouter
from app.models.schemas import AgentRequest
from app.services.agent.core import run_agent

router = APIRouter()


@router.post("/run")
async def run(req: AgentRequest):
    return await run_agent(req.goal, req.session_id, req.max_steps)
