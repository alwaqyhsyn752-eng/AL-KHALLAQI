"""Base provider."""
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
