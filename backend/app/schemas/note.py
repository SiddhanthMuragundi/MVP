from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    body: str


class NoteOut(BaseModel):
    id: int
    body: str
    author_name: str
    created_at: datetime
