from __future__ import annotations

from pydantic import BaseModel

from ..enums import ChatIntent
from .match import MatchOut


class ChatTurn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    client_id: int | None = None
    history: list[ChatTurn] = []


class ChatResponse(BaseModel):
    reply: str
    intent: ChatIntent
    matches: list[MatchOut] | None = None
    ai_used: bool = False
    ai_error: str | None = None
