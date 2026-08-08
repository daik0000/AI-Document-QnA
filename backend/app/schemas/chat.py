from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ChatSessionCreate(BaseModel):
    document_id: int
    title: Optional[str] = None


class ChatSessionOut(BaseModel):
    id: int
    document_id: int
    title: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    question: str


class SourceChunkOut(BaseModel):
    text: str
    distance: float


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    source_chunks: Optional[list[SourceChunkOut]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
