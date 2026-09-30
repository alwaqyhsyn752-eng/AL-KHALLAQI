"""Pydantic schemas."""
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
