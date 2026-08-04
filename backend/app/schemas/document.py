from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class DocumentCreate(BaseModel):
    filename: str
    file_type: Optional[str] = None


class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: Optional[str] = None
    file_path: str
    status: str
    num_chunks: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)